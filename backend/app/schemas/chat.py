"""Chat/RAG schemas."""
from pydantic import BaseModel, Field
from typing import List, Optional


class ChatRequest(BaseModel):
    """Chat query request."""

    question: str
    search_scope: str = Field(default="all", pattern="^(all|organization|private)$")


class ChatResponse(BaseModel):
    """Chat query response."""

    answer: str
    sources: List[str]
