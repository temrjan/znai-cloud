"""Telegram Bot Service for RAG assistants."""
import logging
import secrets
from typing import Any, Dict, Optional

import httpx

from backend.app.config import settings

logger = logging.getLogger(__name__)

TELEGRAM_API_BASE = "https://api.telegram.org/bot"


class TelegramBotService:
    """Service for managing Telegram bot operations."""

    def __init__(self, bot_token: str):
        self.bot_token = bot_token
        self.api_base = f"{TELEGRAM_API_BASE}{bot_token}"

    async def get_me(self) -> dict[str, Any] | None:
        """Get bot info to validate token."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.api_base}/getMe", timeout=10.0)
                data = response.json()
                if data.get("ok"):
                    return data.get("result")
                return None
        except Exception as e:
            logger.error(f"Failed to get bot info: {e}")
            return None

    async def set_webhook(self, webhook_url: str, secret_token: str) -> bool:
        """Set webhook for the bot."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_base}/setWebhook",
                    json={
                        "url": webhook_url,
                        "secret_token": secret_token,
                        "allowed_updates": ["message"],
                        "drop_pending_updates": True
                    },
                    timeout=10.0
                )
                data = response.json()
                if data.get("ok"):
                    logger.info(f"Webhook set successfully: {webhook_url}")
                    return True
                logger.error(f"Failed to set webhook: {data}")
                return False
        except Exception as e:
            logger.error(f"Failed to set webhook: {e}")
            return False

    async def delete_webhook(self) -> bool:
        """Delete webhook for the bot."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_base}/deleteWebhook",
                    json={"drop_pending_updates": True},
                    timeout=10.0
                )
                data = response.json()
                return data.get("ok", False)
        except Exception as e:
            logger.error(f"Failed to delete webhook: {e}")
            return False

    async def send_message(
        self,
        chat_id: int,
        text: str,
        parse_mode: str = "HTML",
        reply_to_message_id: int | None = None
    ) -> bool:
        """Send message to a chat."""
        try:
            # Telegram limit is 4096 chars
            if len(text) > 4000:
                text = text[:4000] + "..."

            async with httpx.AsyncClient() as client:
                payload = {
                    "chat_id": chat_id,
                    "text": text,
                    "parse_mode": parse_mode
                }
                if reply_to_message_id:
                    payload["reply_to_message_id"] = reply_to_message_id

                response = await client.post(
                    f"{self.api_base}/sendMessage",
                    json=payload,
                    timeout=30.0
                )
                data = response.json()
                if not data.get("ok"):
                    logger.error(f"Failed to send message: {data}")
                return data.get("ok", False)
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return False

    async def send_typing_action(self, chat_id: int) -> bool:
        """Send typing indicator."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_base}/sendChatAction",
                    json={"chat_id": chat_id, "action": "typing"},
                    timeout=5.0
                )
                return response.json().get("ok", False)
        except Exception:
            return False


def generate_webhook_secret() -> str:
    """Generate a secure webhook secret."""
    return secrets.token_hex(32)


async def validate_bot_token(token: str) -> dict[str, Any] | None:
    """Validate bot token and return bot info."""
    service = TelegramBotService(token)
    return await service.get_me()


async def setup_bot_webhook(token: str, org_id: int, base_url: str) -> tuple[bool, str]:
    """Setup webhook for a bot.
    
    Returns:
        tuple: (success, webhook_secret or error_message)
    """
    service = TelegramBotService(token)

    # Validate token first
    bot_info = await service.get_me()
    if not bot_info:
        return False, "Invalid bot token"

    # Generate webhook secret
    secret = generate_webhook_secret()

    # Set webhook
    webhook_url = f"{base_url}/api/telegram/webhook/{org_id}"
    success = await service.set_webhook(webhook_url, secret)

    if success:
        return True, secret
    return False, "Failed to set webhook"
