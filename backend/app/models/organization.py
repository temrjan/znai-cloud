"""Organization model."""
import enum
from datetime import datetime
from typing import Optional

from sqlalchemy.sql import func
from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.models.base import Base


class OrganizationStatus(str, enum.Enum):
    """Organization status enum."""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DELETED = "deleted"


class Organization(Base):
    """Organization model for multi-tenant support."""

    __tablename__ = "organizations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )

    # Quota limits
    max_members: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    max_documents: Mapped[int] = mapped_column(Integer, default=50, nullable=False)
    max_storage_mb: Mapped[int] = mapped_column(Integer, default=1000, nullable=False)
    max_queries_per_user_daily: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    max_queries_org_daily: Mapped[int] = mapped_column(Integer, default=500, nullable=False)

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
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    owner: Mapped["User"] = relationship(
        "User",
        foreign_keys=[owner_id],
        backref="owned_organizations"
    )
    members: Mapped[list["User"]] = relationship(
        "User",
        foreign_keys="User.organization_id",
        back_populates="organization"
    )
    documents: Mapped[list["Document"]] = relationship(
        "Document",
        back_populates="organization",
        cascade="all, delete-orphan"
    )
    settings: Mapped[Optional["OrganizationSettings"]] = relationship(
        "OrganizationSettings",
        back_populates="organization",
        uselist=False,
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Organization(id={self.id}, name={self.name}, slug={self.slug}, status={self.status})>"
