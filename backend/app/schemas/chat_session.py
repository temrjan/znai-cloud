"""Chat session schemas."""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class ChatMessageBase(BaseModel):
    """Base chat message schema."""
    role: str
    content: str
    sources: list[str] | None = None


class ChatMessageCreate(BaseModel):
    """Schema for creating a chat message (internal use)."""
    role: str
    content: str
    sources: str | None = None  # JSON string


class ChatMessageResponse(BaseModel):
    """Chat message response schema."""
    id: int
    role: str
    content: str
    sources: list[str] | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class ChatSessionCreate(BaseModel):
    """Schema for creating a chat session."""
    title: str | None = Field(None, max_length=100)


class ChatSessionUpdate(BaseModel):
    """Schema for updating a chat session."""
    title: str = Field(..., min_length=1, max_length=100)


class ChatSessionResponse(BaseModel):
    """Chat session response schema."""
    id: int
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: int | None = 0

    class Config:
        from_attributes = True


class ChatSessionWithMessages(ChatSessionResponse):
    """Chat session with messages."""
    messages: list[ChatMessageResponse] = []


class ChatSessionListResponse(BaseModel):
    """List of chat sessions."""
    sessions: list[ChatSessionResponse]
    total: int
