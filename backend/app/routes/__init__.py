"""API routes."""
from backend.app.routes import health, auth, documents, chat, quota, admin, organizations

__all__ = ["health", "auth", "documents", "chat", "quota", "admin", "organizations"]
