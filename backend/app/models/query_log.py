"""Query log model for analytics."""
from datetime import datetime
from typing import Optional

from sqlalchemy.sql import func
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.models.base import Base


class QueryLog(Base):
    """Query log model for tracking RAG queries."""

    __tablename__ = "query_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    organization_id: Mapped[int | None] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )

    query_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    response_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    sources_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    search_mode: Mapped[str] = mapped_column(String(50), default="all", nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="query_logs")
    organization: Mapped[Optional["Organization"]] = relationship("Organization")

    def __repr__(self) -> str:
        return f"<QueryLog(id={self.id}, user_id={self.user_id})>"
