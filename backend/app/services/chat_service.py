"""Chat service for OpenAI interactions."""
import logging
import re
from typing import List, Dict, Optional

from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from backend.app.config import settings
from backend.app.utils.metrics import OPENAI_REQUESTS, OPENAI_TOKENS

logger = logging.getLogger(__name__)

# Constants
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
    """Service for chat generation using OpenAI."""
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
    
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
        """Generate response from OpenAI with retry logic."""
        if model.startswith('o1'):
            response = self._call_o1_model(messages, model, max_tokens)
        else:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        
        self._track_usage(response, model)
        return strip_markdown(response.choices[0].message.content)
    
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
        
        return self.client.chat.completions.create(
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
        """Build messages array for OpenAI API."""
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


# Singleton
chat_service = ChatService()
