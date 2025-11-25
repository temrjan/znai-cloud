"""Organization schemas."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator

from backend.app.models.organization import OrganizationStatus


class OrganizationCreate(BaseModel):
    """Schema for creating organization."""
    name: str = Field(..., min_length=2, max_length=255)
    slug: Optional[str] = Field(None, min_length=2, max_length=100, pattern=r'^[a-z0-9-]+$')
    max_members: int = Field(default=10, ge=2, le=1000)
    max_documents: int = Field(default=50, ge=1, le=10000)
    max_queries_daily: int = Field(default=500, ge=10, le=100000)

    @field_validator('slug')
    @classmethod
    def validate_slug(cls, v: Optional[str]) -> Optional[str]:
        """Validate slug format."""
        if v and (v.startswith('-') or v.endswith('-') or '--' in v):
            raise ValueError('Slug cannot start/end with hyphen or contain consecutive hyphens')
        return v


class OrganizationUpdate(BaseModel):
    """Schema for updating organization."""
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    max_members: Optional[int] = Field(None, ge=2, le=1000)
    max_documents: Optional[int] = Field(None, ge=1, le=10000)
    max_queries_daily: Optional[int] = Field(None, ge=10, le=100000)


class OrganizationResponse(BaseModel):
    """Schema for organization response."""
    id: int
    name: str
    slug: str
    owner_id: Optional[int] = None
    max_members: int
    max_documents: int
    max_queries_org_daily: int = Field(alias="max_queries_daily", default=500)
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    # Computed fields - set after model_validate
    current_members_count: int = 0
    current_documents_count: int = 0

    class Config:
        from_attributes = True
        populate_by_name = True


class OrganizationMemberResponse(BaseModel):
    """Schema for organization member info."""
    user_id: int
    email: str
    full_name: Optional[str] = None
    role: str
    joined_at: datetime

    class Config:
        from_attributes = True


class OrganizationStatsResponse(BaseModel):
    """Schema for organization statistics."""
    total_members: int
    total_documents: int
    total_queries_today: int
    documents_quota_usage: float
    members_quota_usage: float
    queries_quota_usage: float
