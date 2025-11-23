"""Organization settings schemas."""
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class OrganizationSettingsUpdate(BaseModel):
    """Schema for updating organization AI settings."""
    custom_system_prompt: Optional[str] = Field(None, max_length=4000)
    custom_temperature: Optional[float] = Field(None, ge=0.0, le=2.0)
    custom_top_p: Optional[float] = Field(None, ge=0.0, le=1.0)
    custom_max_tokens: Optional[int] = Field(None, ge=100, le=32000)
    custom_terminology: Optional[Dict[str, str]] = None

    # Chunking settings
    chunk_size: Optional[int] = Field(None, ge=128, le=8192)
    chunk_overlap: Optional[int] = Field(None, ge=0, le=1000)

    # Search settings
    search_top_k: Optional[int] = Field(None, ge=1, le=50)
    search_similarity_threshold: Optional[float] = Field(None, ge=0.0, le=1.0)

    # Response settings
    response_max_length: Optional[int] = Field(None, ge=100, le=4000)
    response_language: Optional[str] = Field(None, max_length=10)
    enable_citations: Optional[bool] = None
    enable_followup_questions: Optional[bool] = None

    # Advanced settings
    reranking_enabled: Optional[bool] = None
    reranking_top_n: Optional[int] = Field(None, ge=1, le=20)
    answer_mode: Optional[str] = Field(None, pattern=r'^(concise|detailed|structured)$')
    context_window_size: Optional[int] = Field(None, ge=1000, le=128000)


class OrganizationSettingsResponse(BaseModel):
    """Schema for organization settings response."""
    id: int
    organization_id: int

    # AI model settings
    custom_system_prompt: Optional[str]
    custom_temperature: Optional[float]
    custom_top_p: Optional[float]
    custom_max_tokens: Optional[int]
    custom_terminology: Optional[Dict[str, Any]]

    # Chunking settings
    chunk_size: Optional[int]
    chunk_overlap: Optional[int]

    # Search settings
    search_top_k: Optional[int]
    search_similarity_threshold: Optional[float]

    # Response settings
    response_max_length: Optional[int]
    response_language: Optional[str]
    enable_citations: Optional[bool]
    enable_followup_questions: Optional[bool]

    # Advanced settings
    reranking_enabled: Optional[bool]
    reranking_top_n: Optional[int]
    answer_mode: Optional[str]
    context_window_size: Optional[int]

    class Config:
        from_attributes = True


class PromptTestRequest(BaseModel):
    """Schema for testing custom system prompt."""
    system_prompt: str = Field(..., min_length=10, max_length=4000)
    test_query: str = Field(..., min_length=5, max_length=500)


class PromptTestResponse(BaseModel):
    """Schema for prompt test response."""
    success: bool
    response_preview: Optional[str]
    tokens_used: Optional[int]
    error: Optional[str]
