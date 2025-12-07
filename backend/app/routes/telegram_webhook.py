"""Telegram webhook endpoint for RAG bot."""
import logging
from typing import Dict, Any

from fastapi import APIRouter, HTTPException, Header, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.database import AsyncSessionLocal
from backend.app.models.organization_settings import OrganizationSettings
from backend.app.services.document_processor import document_processor
from backend.app.services.chat_service import chat_service, DEFAULT_SYSTEM_PROMPT
from backend.app.services.telegram_bot import TelegramBotService
from backend.app.config import settings

router = APIRouter(prefix="/telegram", tags=["Telegram"])
logger = logging.getLogger(__name__)

# Default messages
WELCOME_MESSAGE = """Привет! Я ассистент базы знаний.

Задайте мне вопрос, и я найду ответ в документах организации."""

NO_RESULTS_MESSAGE = """К сожалению, я не нашёл информации по вашему вопросу в базе знаний.

Попробуйте:
• Переформулировать вопрос
• Использовать другие ключевые слова"""

ERROR_MESSAGE = "Произошла ошибка при обработке запроса. Попробуйте позже."


async def get_org_settings(org_id: int) -> OrganizationSettings | None:
    """Get organization settings from DB."""
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(OrganizationSettings).where(
                OrganizationSettings.organization_id == org_id
            )
        )
        return result.scalar_one_or_none()


def escape_html(text: str) -> str:
    """Escape HTML special characters for Telegram."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


@router.post("/webhook/{org_id}")
async def telegram_webhook(
    org_id: int,
    request: Request,
    x_telegram_bot_api_secret_token: str = Header(None, alias="X-Telegram-Bot-Api-Secret-Token")
):
    """Handle incoming Telegram webhook updates."""
    # Get organization settings
    org_settings = await get_org_settings(org_id)
    
    if not org_settings:
        logger.warning(f"Organization {org_id} not found")
        return {"ok": True}  # Return OK to prevent Telegram retries
    
    if not org_settings.telegram_bot_enabled:
        logger.warning(f"Telegram bot disabled for org {org_id}")
        return {"ok": True}
    
    # Verify webhook secret
    if org_settings.telegram_webhook_secret:
        if x_telegram_bot_api_secret_token != org_settings.telegram_webhook_secret:
            logger.warning(f"Invalid webhook secret for org {org_id}")
            return {"ok": True}
    
    # Parse update
    try:
        update = await request.json()
    except Exception as e:
        logger.error(f"Failed to parse update: {e}")
        return {"ok": True}
    
    # Get message
    message = update.get("message")
    if not message:
        return {"ok": True}
    
    chat_id = message.get("chat", {}).get("id")
    text = message.get("text", "")
    message_id = message.get("message_id")
    
    if not chat_id or not text:
        return {"ok": True}
    
    # Initialize bot service
    bot = TelegramBotService(org_settings.telegram_bot_token)
    
    # Handle /start command
    if text.startswith("/start"):
        await bot.send_message(chat_id, WELCOME_MESSAGE)
        return {"ok": True}
    
    # Send typing indicator
    await bot.send_typing_action(chat_id)
    
    try:
        # RAG Search
        search_results = document_processor.search(
            user_id=0,  # Public bot - no user filtering
            query=text,
            limit=5,
            score_threshold=0.35,
            organization_id=org_id,
            search_scope="organization",
            use_reranking=False,
            rerank_top_n=5
        )
        
        if not search_results:
            await bot.send_message(chat_id, NO_RESULTS_MESSAGE, reply_to_message_id=message_id)
            return {"ok": True}
        
        # Build context
        context = chat_service.build_context(
            search_results,
            org_settings.custom_terminology if org_settings.custom_terminology else None
        )
        
        # Get system prompt
        system_prompt = org_settings.custom_system_prompt or DEFAULT_SYSTEM_PROMPT
        
        # Build messages (no history for simplicity)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Контекст из документов:\n{context}\n\nВопрос: {text}"}
        ]
        
        # Get model settings
        model = org_settings.custom_model or settings.openai_llm_model
        temperature = org_settings.custom_temperature or 0.5
        max_tokens = org_settings.custom_max_tokens or 4096
        
        # Generate response
        answer = chat_service.generate_response(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # Add sources
        sources = list(set(r["filename"] for r in search_results[:3]))
        if sources:
            answer += f"\n\n📚 Источники: {', '.join(sources)}"
        
        # Send response
        await bot.send_message(chat_id, escape_html(answer), reply_to_message_id=message_id)
        
        logger.info(f"Telegram bot org={org_id} processed query: {text[:50]}...")
        
    except Exception as e:
        logger.error(f"Error processing telegram message: {e}", exc_info=True)
        await bot.send_message(chat_id, ERROR_MESSAGE, reply_to_message_id=message_id)
    
    return {"ok": True}
