"""Organization settings schemas."""
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class OrganizationSettingsUpdate(BaseModel):
    """Schema for updating organization AI settings."""
    custom_system_prompt: str | None = Field(None, max_length=16000)
    custom_temperature: float | None = Field(None, ge=0.0, le=2.0)
    custom_top_p: float | None = Field(None, ge=0.0, le=1.0)
    custom_max_tokens: int | None = Field(None, ge=100, le=32000)
    custom_terminology: dict[str, str] | None = None

    # Chunking settings
    chunk_size: int | None = Field(None, ge=128, le=8192)
    chunk_overlap: int | None = Field(None, ge=0, le=1000)

    # Search settings
    search_top_k: int | None = Field(None, ge=1, le=50)
    search_similarity_threshold: float | None = Field(None, ge=0.0, le=1.0)

    # Response settings
    response_max_length: int | None = Field(None, ge=100, le=4000)
    response_language: str | None = Field(None, max_length=10)
    enable_citations: bool | None = None
    enable_followup_questions: bool | None = None

    # Advanced settings
    reranking_enabled: bool | None = None
    reranking_top_n: int | None = Field(None, ge=1, le=20)
    answer_mode: str | None = Field(None, pattern=r'^(concise|detailed|structured)$')
    context_window_size: int | None = Field(None, ge=1000, le=128000)


class OrganizationSettingsResponse(BaseModel):
    """Schema for organization settings response."""
    organization_id: int

    # AI model settings
    custom_system_prompt: str | None = None
    custom_temperature: float | None = None
    custom_max_tokens: int | None = None
    custom_model: str | None = None
    custom_terminology: dict[str, Any] | None = None

    # Language settings
    primary_language: str | None = None
    response_language: str | None = None  # Alias for primary_language for frontend

    # Chunking settings
    chunk_size: int | None = None
    chunk_overlap: int | None = None

    class Config:
        from_attributes = True


class PromptTestRequest(BaseModel):
    """Schema for testing custom system prompt."""
    system_prompt: str = Field(..., min_length=10, max_length=16000)
    test_query: str = Field(..., min_length=5, max_length=500)


class PromptTestResponse(BaseModel):
    """Schema for prompt test response."""
    success: bool
    response_preview: str | None
    tokens_used: int | None
    error: str | None
