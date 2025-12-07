"""Organization settings model."""
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, Text, JSON, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.models.base import Base


class OrganizationSettings(Base):
    """Organization settings model for customizing RAG behavior."""

    __tablename__ = "organization_settings"

    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        primary_key=True
    )

    # LLM Configuration
    custom_system_prompt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    custom_temperature: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    custom_max_tokens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    custom_model: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Language Settings
    primary_language: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    secondary_languages: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    require_bilingual_response: Mapped[Optional[bool]] = mapped_column(nullable=True, default=False)

    # Custom Terminology and Citations
    custom_terminology: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    citation_format: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    citation_template: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Document Processing
    chunk_size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    chunk_overlap: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Content Filtering
    content_filters: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Prompt Engineering
    pre_prompt_instructions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    post_prompt_instructions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Response Formatting
    response_format: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    include_sources_inline: Mapped[Optional[bool]] = mapped_column(nullable=True, default=True)
    show_confidence_score: Mapped[Optional[bool]] = mapped_column(nullable=True, default=False)

    # Telegram Bot Settings
    telegram_bot_token: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    telegram_bot_enabled: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True, default=False)
    telegram_bot_username: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    telegram_webhook_secret: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    # Metadata
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
    updated_by_user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )

    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="settings"
    )
    updated_by: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[updated_by_user_id]
    )

    def __repr__(self) -> str:
        return (
            f"<OrganizationSettings(organization_id={self.organization_id}, "
            f"custom_model={self.custom_model})>"
        )
