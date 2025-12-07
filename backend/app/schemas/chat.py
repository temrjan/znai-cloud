"""Chat/RAG schemas."""
from typing import List, Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Chat query request."""

    question: str
    search_scope: str = Field(default="all", pattern="^(all|organization|private)$")
    session_id: int | None = None  # If provided, use session for conversation history


class ChatResponse(BaseModel):
    """Chat query response."""

    answer: str
    sources: list[str]
    session_id: int | None = None  # Return session_id if created/used
