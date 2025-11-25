"""Feedback schemas."""
from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class FeedbackCreate(BaseModel):
    """Schema for creating feedback."""
    message_id: int
    is_helpful: bool
    comment: Optional[str] = None
    category: Optional[str] = None  # 'incorrect', 'incomplete', 'irrelevant', 'outdated', 'other'


class FeedbackResponse(BaseModel):
    """Schema for feedback response."""
    id: int
    message_id: int
    is_helpful: bool
    comment: Optional[str] = None
    category: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
