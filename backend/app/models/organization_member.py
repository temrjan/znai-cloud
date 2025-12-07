"""Organization member model."""
from datetime import datetime
from typing import Optional

from sqlalchemy.sql import func
from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.models.base import Base


class OrganizationMember(Base):
    """Organization member model for tracking membership."""

    __tablename__ = "organization_members"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    role: Mapped[str] = mapped_column(String(50), nullable=False, default="member")

    joined_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    left_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    invited_by_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )

    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")
    user: Mapped["User"] = relationship(
        "User",
        foreign_keys=[user_id]
    )
    invited_by: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[invited_by_user_id]
    )

    def __repr__(self) -> str:
        return (
            f"<OrganizationMember(id={self.id}, organization_id={self.organization_id}, "
            f"user_id={self.user_id}, role={self.role})>"
        )
