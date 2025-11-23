"""Admin routes."""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from backend.app.database import get_db
from backend.app.models.user import User, UserStatus, UserRole
from backend.app.models.organization import Organization
from backend.app.schemas.user import UserResponse
from backend.app.middleware.auth import get_current_user


router = APIRouter(prefix="/admin", tags=["Admin"])


# Response schemas
class PendingOrganizationResponse(BaseModel):
    """Pending organization with owner info."""
    id: int
    name: str
    slug: str
    status: str
    created_at: datetime
    owner_id: Optional[int]
    owner_email: Optional[str]
    owner_full_name: Optional[str]

    class Config:
        from_attributes = True


def require_platform_admin(current_user: User = Depends(get_current_user)) -> User:
    """Require platform admin (owner) role."""
    if not current_user.is_platform_admin and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Platform admin access required",
        )
    return current_user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Require admin role (legacy, redirects to platform admin)."""
    return require_platform_admin(current_user)


# ============================================================================
# PENDING USERS (personal registrations)
# ============================================================================

@router.get("/users/pending", response_model=List[UserResponse])
async def get_pending_users(
    admin: User = Depends(require_platform_admin),
    db: AsyncSession = Depends(get_db),
):
    """Get all pending personal user registrations (without organization)."""
    result = await db.execute(
        select(User)
        .where(User.status == UserStatus.PENDING)
        .where(User.organization_id == None)  # Only personal registrations
        .order_by(User.created_at.desc())
    )
    users = result.scalars().all()
    return users


@router.post("/users/{user_id}/approve", response_model=UserResponse)
async def approve_user(
    user_id: int,
    admin: User = Depends(require_platform_admin),
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
    user.approved_at = datetime.utcnow()

    await db.commit()
    await db.refresh(user)

    return user


@router.post("/users/{user_id}/reject", response_model=UserResponse)
async def reject_user(
    user_id: int,
    admin: User = Depends(require_platform_admin),
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


# ============================================================================
# PENDING ORGANIZATIONS
# ============================================================================

@router.get("/organizations/pending", response_model=List[PendingOrganizationResponse])
async def get_pending_organizations(
    admin: User = Depends(require_platform_admin),
    db: AsyncSession = Depends(get_db),
):
    """Get all pending organization registrations with owner info."""
    result = await db.execute(
        select(Organization)
        .where(Organization.status == "pending")
        .order_by(Organization.created_at.desc())
    )
    organizations = result.scalars().all()

    response = []
    for org in organizations:
        # Get owner info
        owner_result = await db.execute(
            select(User).where(User.id == org.owner_id)
        )
        owner = owner_result.scalar_one_or_none()

        response.append(PendingOrganizationResponse(
            id=org.id,
            name=org.name,
            slug=org.slug,
            status=org.status,
            created_at=org.created_at,
            owner_id=org.owner_id,
            owner_email=owner.email if owner else None,
            owner_full_name=owner.full_name if owner else None,
        ))

    return response


@router.post("/organizations/{org_id}/approve", response_model=PendingOrganizationResponse)
async def approve_organization(
    org_id: int,
    admin: User = Depends(require_platform_admin),
    db: AsyncSession = Depends(get_db),
):
    """Approve a pending organization and its owner."""
    # Get organization
    result = await db.execute(
        select(Organization).where(Organization.id == org_id)
    )
    org = result.scalar_one_or_none()

    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )

    if org.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Organization status is {org.status}, not pending",
        )

    # Activate organization
    org.status = "active"

    # Approve owner user
    if org.owner_id:
        owner_result = await db.execute(
            select(User).where(User.id == org.owner_id)
        )
        owner = owner_result.scalar_one_or_none()
        if owner:
            owner.status = UserStatus.APPROVED
            owner.approved_by_id = admin.id
            owner.approved_at = datetime.utcnow()

    await db.commit()
    await db.refresh(org)

    # Get owner for response
    owner_result = await db.execute(
        select(User).where(User.id == org.owner_id)
    )
    owner = owner_result.scalar_one_or_none()

    return PendingOrganizationResponse(
        id=org.id,
        name=org.name,
        slug=org.slug,
        status=org.status,
        created_at=org.created_at,
        owner_id=org.owner_id,
        owner_email=owner.email if owner else None,
        owner_full_name=owner.full_name if owner else None,
    )


@router.post("/organizations/{org_id}/reject")
async def reject_organization(
    org_id: int,
    admin: User = Depends(require_platform_admin),
    db: AsyncSession = Depends(get_db),
):
    """Reject a pending organization and its owner."""
    # Get organization
    result = await db.execute(
        select(Organization).where(Organization.id == org_id)
    )
    org = result.scalar_one_or_none()

    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )

    if org.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Organization status is {org.status}, not pending",
        )

    # Reject organization
    org.status = "rejected"

    # Reject owner user
    if org.owner_id:
        owner_result = await db.execute(
            select(User).where(User.id == org.owner_id)
        )
        owner = owner_result.scalar_one_or_none()
        if owner:
            owner.status = UserStatus.REJECTED

    await db.commit()

    return {"message": "Organization rejected"}


# ============================================================================
# STATS
# ============================================================================

@router.get("/stats")
async def get_admin_stats(
    admin: User = Depends(require_platform_admin),
    db: AsyncSession = Depends(get_db),
):
    """Get admin dashboard stats."""
    # Pending users count
    pending_users_result = await db.execute(
        select(User)
        .where(User.status == UserStatus.PENDING)
        .where(User.organization_id == None)
    )
    pending_users_count = len(pending_users_result.scalars().all())

    # Pending organizations count
    pending_orgs_result = await db.execute(
        select(Organization).where(Organization.status == "pending")
    )
    pending_orgs_count = len(pending_orgs_result.scalars().all())

    return {
        "pending_users": pending_users_count,
        "pending_organizations": pending_orgs_count,
        "total_pending": pending_users_count + pending_orgs_count,
    }
