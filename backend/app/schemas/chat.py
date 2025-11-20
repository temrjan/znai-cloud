"""Chat/RAG schemas."""
from pydantic import BaseModel
from typing import List


class ChatRequest(BaseModel):
    """Chat query request."""

    question: str


class ChatResponse(BaseModel):
    """Chat query response."""

    answer: str
    sources: List[str]
