"""Organization invite model."""
import enum
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy.sql import func
from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.models.base import Base


class InviteStatus(str, enum.Enum):
    """Invite status enum."""
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"


class OrganizationInvite(Base):
    """Organization invite model for member invitations."""

    __tablename__ = "organization_invites"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    code: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        unique=True,
        nullable=False,
        default=uuid.uuid4,
        index=True
    )
    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    created_by_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    max_uses: Mapped[int | None] = mapped_column(Integer, nullable=True)
    used_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    default_role: Mapped[str] = mapped_column(String(50), default="member", nullable=False)
    status: Mapped[str] = mapped_column(
        String(20),
        default="active",
        nullable=False,
        index=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")
    created_by: Mapped["User"] = relationship(
        "User",
        foreign_keys=[created_by_user_id]
    )

    def __repr__(self) -> str:
        return (
            f"<OrganizationInvite(id={self.id}, code={self.code}, "
            f"organization_id={self.organization_id}, status={self.status})>"
        )
