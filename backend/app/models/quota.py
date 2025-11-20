"""User quota model."""
from datetime import date
from typing import Optional

from sqlalchemy import Integer, Date, ForeignKey, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.models.base import Base


class UserQuota(Base):
    """User quota model for tracking usage limits."""

    __tablename__ = "user_quotas"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True
    )

    max_documents: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    current_documents: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    max_queries_daily: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    queries_today: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_query_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="quota")

    __table_args__ = (
        CheckConstraint(
            "current_documents <= max_documents",
            name="check_documents_quota"
        ),
        CheckConstraint(
            "queries_today >= 0",
            name="check_queries_positive"
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<UserQuota(user_id={self.user_id}, "
            f"documents={self.current_documents}/{self.max_documents}, "
            f"queries={self.queries_today}/{self.max_queries_daily})>"
        )
