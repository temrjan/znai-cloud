"""Organization invite schemas."""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from backend.app.models.organization_invite import InviteStatus


class InviteCreate(BaseModel):
    """Schema for creating invite."""
    max_uses: int = Field(default=1, ge=1, le=1000)
    expires_in_hours: int = Field(default=168, ge=1, le=8760)  # Default 7 days, max 1 year
    default_role: str = Field(default='member', pattern=r'^(admin|member)$')


class InviteResponse(BaseModel):
    """Schema for invite response."""
    id: int
    code: UUID
    organization_id: int
    organization_name: str | None = None  # Optional - may not be loaded
    max_uses: int
    used_count: int
    expires_at: datetime
    status: InviteStatus
    default_role: str
    created_by_user_id: int | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class InviteAcceptRequest(BaseModel):
    """Schema for accepting invite."""
    code: UUID


class InviteDetailsResponse(BaseModel):
    """Schema for public invite details (before accepting)."""
    organization_name: str
    default_role: str = "member"
    expires_at: datetime | None = None
    is_valid: bool = False

    class Config:
        from_attributes = True
