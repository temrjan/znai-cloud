"""Admin routes."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from backend.app.database import get_db
from backend.app.models.user import User, UserStatus, UserRole
from backend.app.schemas.user import UserResponse
from backend.app.middleware.auth import get_current_user


router = APIRouter(prefix="/admin", tags=["Admin"])


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Require admin role."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user


@router.get("/users/pending", response_model=List[UserResponse])
async def get_pending_users(
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Get all pending user registrations."""
    result = await db.execute(
        select(User)
        .where(User.status == UserStatus.PENDING)
        .order_by(User.created_at.desc())
    )
    users = result.scalars().all()
    return users


@router.post("/users/{user_id}/approve", response_model=UserResponse)
async def approve_user(
    user_id: int,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Approve a pending user."""
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if user.status != UserStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User status is {user.status.value}, not pending",
        )

    user.status = UserStatus.APPROVED
    user.approved_by_id = admin.id

    await db.commit()
    await db.refresh(user)

    return user


@router.post("/users/{user_id}/reject", response_model=UserResponse)
async def reject_user(
    user_id: int,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Reject a pending user."""
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if user.status != UserStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User status is {user.status.value}, not pending",
        )

    user.status = UserStatus.REJECTED

    await db.commit()
    await db.refresh(user)

    return user
