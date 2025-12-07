"""Telegram notification service."""
import httpx

from backend.app.config import settings


async def send_telegram_notification(message: str) -> bool:
    """Send notification to platform owner via Telegram bot."""
    if not settings.telegram_bot_token or not settings.telegram_owner_chat_id:
        return False

    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"
    payload = {
        "chat_id": settings.telegram_owner_chat_id,
        "text": message,
        "parse_mode": "HTML",
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, timeout=10)
            return response.status_code == 200
    except Exception as e:
        print(f"Telegram notification error: {e}")
        return False


async def notify_new_organization(org_name: str, owner_email: str, owner_name: str) -> bool:
    """Notify about new organization registration."""
    message = (
        f"🏢 <b>Новая заявка на регистрацию</b>\n\n"
        f"<b>Организация:</b> {org_name}\n"
        f"<b>Админ:</b> {owner_name or 'Не указано'}\n"
        f"<b>Email:</b> {owner_email}\n\n"
        f"👉 <a href='https://znai.cloud/admin'>Открыть панель управления</a>"
    )
    return await send_telegram_notification(message)


async def notify_new_personal_user(email: str, full_name: str) -> bool:
    """Notify about new personal user registration."""
    message = (
        f"👤 <b>Новая личная регистрация</b>\n\n"
        f"<b>Имя:</b> {full_name or 'Не указано'}\n"
        f"<b>Email:</b> {email}\n\n"
        f"👉 <a href='https://znai.cloud/admin'>Открыть панель управления</a>"
    )
    return await send_telegram_notification(message)
