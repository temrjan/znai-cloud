"""Authentication middleware and dependencies."""
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from backend.app.database import get_db
from backend.app.models.user import User, UserStatus
from backend.app.models.organization_member import OrganizationMember
from backend.app.utils.security import decode_access_token


security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Get current authenticated user from JWT token.

    Args:
        credentials: HTTP bearer credentials
        db: Database session

    Returns:
        Current user

    Raises:
        HTTPException: If token is invalid or user not found
    """
    token = credentials.credentials

    # Decode token
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id: Optional[int] = payload.get("user_id")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    # Get user from database with memberships eagerly loaded
    result = await db.execute(
        select(User)
        .options(selectinload(User.memberships))
        .where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Check user status
    if user.status != UserStatus.APPROVED:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User status is {user.status.value}. Awaiting admin approval.",
        )

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get current active user (approved status)."""
    return current_user


async def require_org_member(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Require user to be a member of an organization.

    Args:
        current_user: Current authenticated user

    Returns:
        Current user (must have organization_id)

    Raises:
        HTTPException: If user is not part of any organization
    """
    if current_user.organization_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This action requires organization membership",
        )
    return current_user


async def require_org_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Require user to be an admin or owner in their organization.

    Args:
        current_user: Current authenticated user

    Returns:
        Current user (must be admin or owner)

    Raises:
        HTTPException: If user is not admin/owner or not in organization
    """
    if current_user.organization_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This action requires organization membership",
        )

    if not current_user.is_org_admin_or_owner():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This action requires admin or owner role in the organization",
        )

    return current_user


async def require_org_owner(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Require user to be the owner of their organization.

    Args:
        current_user: Current authenticated user

    Returns:
        Current user (must be owner)

    Raises:
        HTTPException: If user is not owner or not in organization
    """
    if current_user.organization_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This action requires organization membership",
        )

    if not current_user.is_org_owner():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This action requires organization owner role",
        )

    return current_user


async def require_platform_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Require user to be a platform administrator.

    Args:
        current_user: Current authenticated user

    Returns:
        Current user (must be platform admin)

    Raises:
        HTTPException: If user is not platform admin
    """
    if not current_user.is_platform_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This action requires platform administrator privileges",
        )

    return current_user
