"""Quota schemas."""
from datetime import date
from pydantic import BaseModel


class QuotaResponse(BaseModel):
    """User quota response."""

    max_documents: int
    current_documents: int
    max_queries_daily: int
    queries_today: int
    last_query_date: date | None = None

    model_config = {"from_attributes": True}
