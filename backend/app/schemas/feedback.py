"""Feedback schemas."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class FeedbackCreate(BaseModel):
    """Schema for creating feedback."""
    message_id: int
    is_helpful: bool
    comment: str | None = None
    category: str | None = None  # 'incorrect', 'incomplete', 'irrelevant', 'outdated', 'other'


class FeedbackResponse(BaseModel):
    """Schema for feedback response."""
    id: int
    message_id: int
    is_helpful: bool
    comment: str | None = None
    category: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True
