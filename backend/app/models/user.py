"""User model."""
import enum
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy.sql import func
from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.models.base import Base

if TYPE_CHECKING:
    from backend.app.models.organization import Organization
    from backend.app.models.organization_member import OrganizationMember


class UserStatus(str, enum.Enum):
    """User status enum."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    SUSPENDED = "suspended"


class UserRole(str, enum.Enum):
    """User role enum."""
    USER = "user"
    ADMIN = "admin"


class User(Base):
    """User model."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    status: Mapped[UserStatus] = mapped_column(
        Enum(UserStatus),
        default=UserStatus.PENDING,
        nullable=False,
        index=True
    )
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole),
        default=UserRole.USER,
        nullable=False
    )

    approved_by_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Organization fields
    organization_id: Mapped[int | None] = mapped_column(
        ForeignKey("organizations.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    role_in_org: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )
    is_platform_admin: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    # Relationships
    organization: Mapped[Optional["Organization"]] = relationship(
        "Organization",
        foreign_keys=[organization_id],
        back_populates="members"
    )
    memberships: Mapped[list["OrganizationMember"]] = relationship(
        "OrganizationMember",
        foreign_keys="OrganizationMember.user_id",
        back_populates="user",
        lazy="selectin"
    )
    quota: Mapped["UserQuota"] = relationship(
        "UserQuota",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )
    documents: Mapped[list["Document"]] = relationship(
        "Document",
        foreign_keys="Document.uploaded_by_user_id",
        back_populates="uploaded_by_user",
        cascade="all, delete-orphan"
    )
    query_logs: Mapped[list["QueryLog"]] = relationship(
        "QueryLog",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    chat_sessions: Mapped[list["ChatSession"]] = relationship(
        "ChatSession",
        back_populates="user",
        cascade="all, delete-orphan",
        order_by="desc(ChatSession.updated_at)"
    )

    def get_org_role(self) -> str | None:
        """
        Get user's role in their current organization.
        Prefers OrganizationMember.role, falls back to role_in_org for compatibility.
        """
        if self.organization_id is None:
            return None

        # Check memberships (loaded via selectin)
        for membership in self.memberships:
            if membership.organization_id == self.organization_id:
                return membership.role

        # Fallback to legacy field
        return self.role_in_org

    def is_org_admin_or_owner(self) -> bool:
        """Check if user is admin or owner in their organization."""
        role = self.get_org_role()
        return role in ['admin', 'owner']

    def is_org_owner(self) -> bool:
        """Check if user is owner of their organization."""
        return self.get_org_role() == 'owner'

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, status={self.status})>"
