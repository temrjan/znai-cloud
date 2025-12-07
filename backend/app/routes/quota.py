"""Quota routes."""
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import get_db
from backend.app.middleware.auth import get_current_user
from backend.app.models.quota import UserQuota
from backend.app.models.user import User
from backend.app.schemas.quota import QuotaResponse

router = APIRouter(prefix="/quota", tags=["Quota"])


@router.get("", response_model=QuotaResponse)
async def get_quota(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get current user's quota."""
    result = await db.execute(
        select(UserQuota).where(UserQuota.user_id == current_user.id)
    )
    quota = result.scalar_one()
    return quota
