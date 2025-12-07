"""Organization settings model."""
from datetime import datetime
from typing import Optional

from sqlalchemy.sql import func
from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String, Text
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
    custom_system_prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    custom_temperature: Mapped[float | None] = mapped_column(Float, nullable=True)
    custom_max_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    custom_model: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Language Settings
    primary_language: Mapped[str | None] = mapped_column(String(10), nullable=True)
    secondary_languages: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    require_bilingual_response: Mapped[bool | None] = mapped_column(nullable=True, default=False)

    # Custom Terminology and Citations
    custom_terminology: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    citation_format: Mapped[str | None] = mapped_column(String(50), nullable=True)
    citation_template: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Document Processing
    chunk_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    chunk_overlap: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Content Filtering
    content_filters: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Prompt Engineering
    pre_prompt_instructions: Mapped[str | None] = mapped_column(Text, nullable=True)
    post_prompt_instructions: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Response Formatting
    response_format: Mapped[str | None] = mapped_column(String(50), nullable=True)
    include_sources_inline: Mapped[bool | None] = mapped_column(nullable=True, default=True)
    show_confidence_score: Mapped[bool | None] = mapped_column(nullable=True, default=False)

    # Telegram Bot Settings
    telegram_bot_token: Mapped[str | None] = mapped_column(String(100), nullable=True)
    telegram_bot_enabled: Mapped[bool | None] = mapped_column(Boolean, nullable=True, default=False)
    telegram_bot_username: Mapped[str | None] = mapped_column(String(100), nullable=True)
    telegram_webhook_secret: Mapped[str | None] = mapped_column(String(64), nullable=True)

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
    updated_by_user_id: Mapped[int | None] = mapped_column(
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
