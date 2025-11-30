"""Chat service for LLM interactions (Gemini/OpenAI)."""
import logging
import re
from typing import List, Dict, Optional

from openai import OpenAI
import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from backend.app.config import settings
from backend.app.utils.metrics import OPENAI_REQUESTS, OPENAI_TOKENS

logger = logging.getLogger(__name__)

MAX_CONTEXT_MESSAGES = 6

DEFAULT_SYSTEM_PROMPT = """Ты - ассистент базы знаний. Твоя задача - давать точные ответы на основе загруженных документов организации.

СТРОГИЕ ПРАВИЛА:
- Используй ТОЛЬКО информацию из предоставленного контекста
- Если ответа нет в контексте: "В загруженных документах нет информации по этому вопросу"
- ЗАПРЕЩЕНО использовать общие знания или домысливать факты

ЦИТИРОВАНИЕ:
- Указывай источник КАЖДОГО факта: [Название документа, стр./раздел]
- Сохраняй оригинальную нумерацию из документов (номера, коды, индексы)
- При прямом цитировании используй кавычки

ФОРМАТИРОВАНИЕ:
- НЕ используй markdown разметку (**, *, #, ##, -, *)
- НЕ используй жирный текст, курсив, заголовки
- Пиши обычным текстом с нумерованными списками: 1. 2. 3.
- Эмоджи используй УМЕРЕННО - максимум 1-2 за весь ответ, только если уместно

СТИЛЬ ОТВЕТА:
- Адаптируйся под терминологию и стиль документов
- Давай развёрнутые, но чёткие ответы
- Структурируй информацию логично
- Если информация противоречива, укажи все точки зрения

ФОРМАТ:
1. Прямой ответ на вопрос
2. Детальное объяснение с цитатами
3. Источники (если несколько)

Твоя цель - максимальная точность и полезность."""


def strip_markdown(text: str) -> str:
    """Remove markdown formatting from text."""
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text = re.sub(r'\*([^*]+)\*', r'\1', text)
    text = re.sub(r'__([^_]+)__', r'\1', text)
    text = re.sub(r'_([^_]+)_', r'\1', text)
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'```[^`]*```', '', text, flags=re.DOTALL)
    text = re.sub(r'`([^`]+)`', r'\1', text)
    text = re.sub(r'^\s*[-*+]\s+', '', text, flags=re.MULTILINE)
    return text


class ChatService:
    """Service for chat generation using Gemini (primary) or OpenAI (fallback)."""

    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.openai_api_key)

        self.gemini_model = None
        if settings.gemini_api_key:
            genai.configure(api_key=settings.gemini_api_key)
            self.gemini_model = genai.GenerativeModel(settings.gemini_model)
            logger.info(f"Gemini initialized with model: {settings.gemini_model}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((Exception,)),
        reraise=True
    )
    def generate_response(
        self,
        messages: List[Dict],
        model: str,
        temperature: float,
        max_tokens: int,
    ) -> str:
        """Generate response from LLM with retry logic."""
        if settings.use_gemini and self.gemini_model and not model.startswith('o1'):
            return self._call_gemini(messages, temperature, max_tokens)

        if model.startswith('o1'):
            response = self._call_o1_model(messages, model, max_tokens)
        else:
            response = self.openai_client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )

        self._track_usage(response, model)
        return strip_markdown(response.choices[0].message.content)

    def _call_gemini(self, messages: List[Dict], temperature: float, max_tokens: int) -> str:
        """Call Gemini API."""
        system_prompt = ""
        conversation = []

        for msg in messages:
            if msg['role'] == 'system':
                system_prompt = msg['content']
            elif msg['role'] == 'user':
                conversation.append({'role': 'user', 'parts': [msg['content']]})
            elif msg['role'] == 'assistant':
                conversation.append({'role': 'model', 'parts': [msg['content']]})

        generation_config = genai.types.GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
        )

        chat = self.gemini_model.start_chat(history=conversation[:-1] if len(conversation) > 1 else [])

        user_message = conversation[-1]['parts'][0] if conversation else ""
        if system_prompt:
            full_prompt = f"System Instructions: {system_prompt}\n\nUser Query: {user_message}"
        else:
            full_prompt = user_message

        response = chat.send_message(full_prompt, generation_config=generation_config)

        logger.info(f"Gemini response generated, model: {settings.gemini_model}")
        OPENAI_REQUESTS.labels(model=settings.gemini_model, status="success").inc()

        return strip_markdown(response.text)

    def _call_o1_model(self, messages: List[Dict], model: str, max_tokens: int):
        """Handle o1 model specifics (no temperature, convert system to user)."""
        converted_messages = []
        system_content = None

        for msg in messages:
            if msg['role'] == 'system':
                system_content = msg['content']
            else:
                converted_messages.append(msg)

        if system_content and converted_messages:
            first_user_idx = next(
                (i for i, m in enumerate(converted_messages) if m['role'] == 'user'),
                None
            )
            if first_user_idx is not None:
                converted_messages[first_user_idx]['content'] = (
                    "Instructions: " + system_content + "\n\n" +
                    converted_messages[first_user_idx]['content']
                )

        return self.openai_client.chat.completions.create(
            model=model,
            messages=converted_messages,
            max_completion_tokens=max_tokens,
        )

    def _track_usage(self, response, model: str):
        """Track token usage in Prometheus metrics."""
        if response.usage:
            OPENAI_TOKENS.labels(model=model, type="prompt").inc(response.usage.prompt_tokens)
            OPENAI_TOKENS.labels(model=model, type="completion").inc(response.usage.completion_tokens)
            logger.info(
                f"OpenAI usage: model={model}, "
                f"prompt_tokens={response.usage.prompt_tokens}, "
                f"completion_tokens={response.usage.completion_tokens}"
            )
        OPENAI_REQUESTS.labels(model=model, status="success").inc()

    def build_context(
        self,
        search_results: List[Dict],
        custom_terminology: Optional[Dict] = None,
    ) -> str:
        """Build context string from search results."""
        context = "\n\n".join([
            f"From {result['filename']}:\n{result['text']}"
            for result in search_results
        ])

        if custom_terminology:
            for term, expansion in custom_terminology.items():
                context = context.replace(term, f"{term} ({expansion})")

        return context

    def build_messages(
        self,
        system_prompt: str,
        history_messages: List,
        question: str,
        context: str,
    ) -> List[Dict]:
        """Build messages array for LLM API."""
        messages = [{"role": "system", "content": system_prompt}]

        for msg in history_messages:
            messages.append({
                "role": msg.role.value,
                "content": msg.content
            })

        messages.append({
            "role": "user",
            "content": f"Контекст из документов:\n{context}\n\nВопрос: {question}"
        })

        return messages


chat_service = ChatService()
