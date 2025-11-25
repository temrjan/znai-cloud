"""User feedback model for RAG quality tracking."""
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.models.base import Base


class Feedback(Base):
    """User feedback on RAG responses."""

    __tablename__ = "feedback"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Link to the message being rated
    message_id: Mapped[int] = mapped_column(
        ForeignKey("chat_messages.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Rating: True = helpful, False = not helpful
    is_helpful: Mapped[bool] = mapped_column(Boolean, nullable=False)
    
    # Optional detailed feedback
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Feedback categories (optional)
    category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    # Categories: 'incorrect', 'incomplete', 'irrelevant', 'outdated', 'other'
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    
    # Relationships
    message: Mapped["ChatMessage"] = relationship("ChatMessage")
    user: Mapped["User"] = relationship("User")

    def __repr__(self) -> str:
        return f"<Feedback(id={self.id}, message_id={self.message_id}, is_helpful={self.is_helpful})>"
