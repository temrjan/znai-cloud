"""Document schemas."""
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel

from backend.app.models.document import DocumentStatus


class DocumentResponse(BaseModel):
    """Document response model."""

    id: UUID
    uploaded_by_user_id: int
    filename: str
    file_path: str | None = None
    file_size: int | None = None
    file_hash: str | None = None
    mime_type: str | None = None
    chunks_count: int = 0
    status: DocumentStatus
    error_message: str | None = None
    uploaded_at: datetime
    indexed_at: datetime | None = None

    model_config = {"from_attributes": True}
