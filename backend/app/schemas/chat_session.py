"""Chat session schemas."""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class ChatMessageBase(BaseModel):
    """Base chat message schema."""
    role: str
    content: str
    sources: Optional[List[str]] = None


class ChatMessageCreate(BaseModel):
    """Schema for creating a chat message (internal use)."""
    role: str
    content: str
    sources: Optional[str] = None  # JSON string


class ChatMessageResponse(BaseModel):
    """Chat message response schema."""
    id: int
    role: str
    content: str
    sources: Optional[List[str]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ChatSessionCreate(BaseModel):
    """Schema for creating a chat session."""
    title: Optional[str] = Field(None, max_length=100)


class ChatSessionUpdate(BaseModel):
    """Schema for updating a chat session."""
    title: str = Field(..., min_length=1, max_length=100)


class ChatSessionResponse(BaseModel):
    """Chat session response schema."""
    id: int
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: Optional[int] = 0

    class Config:
        from_attributes = True


class ChatSessionWithMessages(ChatSessionResponse):
    """Chat session with messages."""
    messages: List[ChatMessageResponse] = []


class ChatSessionListResponse(BaseModel):
    """List of chat sessions."""
    sessions: List[ChatSessionResponse]
    total: int
