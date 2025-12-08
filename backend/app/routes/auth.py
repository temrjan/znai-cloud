"""Authentication routes with rate limiting."""
import time
from collections import defaultdict
from datetime import datetime
from typing import Dict, Tuple

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.config import settings
from backend.app.database import get_db
from backend.app.middleware.auth import get_current_user
from backend.app.models.organization import Organization, OrganizationStatus
from backend.app.models.organization_invite import InviteStatus, OrganizationInvite
from backend.app.models.organization_member import OrganizationMember
from backend.app.models.organization_settings import OrganizationSettings
from backend.app.models.quota import UserQuota
from backend.app.models.user import User, UserRole, UserStatus
from backend.app.schemas.user import Token, UserCreate, UserLogin, UserResponse
from backend.app.services.telegram import (
    notify_new_organization,
    notify_new_personal_user,
)
from backend.app.utils.security import (
    create_access_token,
    hash_password,
    verify_password,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


# Simple in-memory rate limiter
class RateLimiter:
    """Simple rate limiter using sliding window."""

    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: dict[str, list] = defaultdict(list)

    def is_allowed(self, key: str) -> tuple[bool, int]:
        """Check if request is allowed. Returns (allowed, retry_after_seconds)."""
        now = time.time()
        window_start = now - self.window_seconds

        # Clean old requests
        self.requests[key] = [t for t in self.requests[key] if t > window_start]

        if len(self.requests[key]) >= self.max_requests:
            oldest = min(self.requests[key])
            retry_after = int(oldest + self.window_seconds - now) + 1
            return False, retry_after

        self.requests[key].append(now)
        return True, 0


# Rate limiters for different endpoints
login_limiter = RateLimiter(max_requests=5, window_seconds=60)  # 5 per minute
register_limiter = RateLimiter(max_requests=3, window_seconds=60)  # 3 per minute


def get_client_ip(request: Request) -> str:
    """Get client IP from request."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Register a new user.

    If organization_name is provided, creates organization and user becomes owner (auto-approved).
    Otherwise, user status will be 'pending' and requires admin approval.
    """
    # Rate limiting
    client_ip = get_client_ip(request)
    allowed, retry_after = register_limiter.is_allowed(client_ip)
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Too many registration attempts. Try again in {retry_after} seconds.",
            headers={"Retry-After": str(retry_after)},
        )

    # Check if email already exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Hash password
    hashed_password = hash_password(user_data.password)

    # CASE 1: Registration with organization creation
    if user_data.organization_name:
        # Generate slug
        slug = user_data.organization_name.lower().replace(" ", "-")
        slug = "".join(c for c in slug if c.isalnum() or c == "-")

        # Check slug uniqueness
        slug_result = await db.execute(select(Organization).where(Organization.slug == slug))
        if slug_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Organization name '{user_data.organization_name}' is already taken",
            )

        # Create organization (owner_id will be set later)
        organization = Organization(
            name=user_data.organization_name,
            slug=slug,
            owner_id=None,  # Will be updated after user creation
            status="pending",  # Requires platform owner approval
        )
        db.add(organization)
        await db.flush()

        # Create user as organization owner (requires approval)
        new_user = User(
            email=user_data.email,
            password_hash=hashed_password,
            full_name=user_data.full_name,
            status=UserStatus.PENDING,  # Requires platform owner approval
            role=UserRole.USER,
            organization_id=organization.id,
            role_in_org="owner",
        )
        db.add(new_user)
        await db.flush()

        # Update organization owner_id
        organization.owner_id = new_user.id

        # Create organization member record
        member_record = OrganizationMember(
            organization_id=organization.id,
            user_id=new_user.id,
            role="owner",
            joined_at=datetime.utcnow(),
        )
        db.add(member_record)

        # Create default organization settings
        org_settings = OrganizationSettings(organization_id=organization.id)
        db.add(org_settings)

        # Create user quota with personal limits for hybrid mode
        quota = UserQuota(
            user_id=new_user.id,
            max_documents=settings.free_user_max_documents,
            max_queries_daily=settings.free_user_max_queries_daily,
            personal_max_documents=10,  # Default personal quota in hybrid mode
            personal_max_queries_daily=50,
        )
        db.add(quota)

    # CASE 2: Registration via invite code
    elif user_data.invite_code:
        import uuid
        try:
            code_uuid = uuid.UUID(user_data.invite_code)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid invite code format",
            )

        # Find and validate invite
        invite_result = await db.execute(
            select(OrganizationInvite).where(OrganizationInvite.code == code_uuid)
        )
        invite = invite_result.scalar_one_or_none()

        if not invite:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invite code not found",
            )

        if invite.status != InviteStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invite is {invite.status.value}",
            )

        if invite.used_count >= invite.max_uses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invite has reached maximum uses",
            )

        if invite.expires_at < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invite has expired",
            )

        # Get organization
        org_result = await db.execute(
            select(Organization).where(Organization.id == invite.organization_id)
        )
        organization = org_result.scalar_one_or_none()

        if not organization or organization.status != "active":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Organization is not active",
            )

        # Create user as organization member (auto-approved)
        new_user = User(
            email=user_data.email,
            password_hash=hashed_password,
            full_name=user_data.full_name,
            status=UserStatus.APPROVED,  # Auto-approved via invite
            role=UserRole.USER,
            organization_id=organization.id,
            role_in_org=invite.default_role,
        )
        db.add(new_user)
        await db.flush()

        # Update invite used_count
        invite.used_count += 1

        # Create organization member record
        member_record = OrganizationMember(
            organization_id=organization.id,
            user_id=new_user.id,
            role=invite.default_role,
            joined_at=datetime.utcnow(),
            invited_by_user_id=invite.created_by_user_id,
        )
        db.add(member_record)

        # Create user quota
        quota = UserQuota(
            user_id=new_user.id,
            max_documents=settings.free_user_max_documents,
            max_queries_daily=settings.free_user_max_queries_daily,
            personal_max_documents=10,
            personal_max_queries_daily=50,
        )
        db.add(quota)

    # CASE 3: Personal registration (no organization)
    else:
        new_user = User(
            email=user_data.email,
            password_hash=hashed_password,
            full_name=user_data.full_name,
            status=UserStatus.PENDING,  # Requires approval
            role=UserRole.USER,
            organization_id=None,
            role_in_org=None,
        )
        db.add(new_user)
        await db.flush()

        # Create user quota for personal mode
        quota = UserQuota(
            user_id=new_user.id,
            max_documents=settings.free_user_max_documents,
            max_queries_daily=settings.free_user_max_queries_daily,
        )
        db.add(quota)

    await db.commit()
    await db.refresh(new_user)

    # Send Telegram notification to platform owner (non-blocking)
    # Skip for invite registrations (auto-approved, no notification needed)
    try:
        if user_data.organization_name:
            await notify_new_organization(
                org_name=user_data.organization_name,
                owner_email=user_data.email,
                owner_name=user_data.full_name or "",
            )
        elif not user_data.invite_code:
            await notify_new_personal_user(
                email=user_data.email,
                full_name=user_data.full_name or "",
            )
    except Exception:
        pass  # Don't fail registration if notification fails

    return new_user


@router.post("/login", response_model=Token)
async def login(
    user_data: UserLogin,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Login user and return JWT token.

    User must be approved by admin to login.
    Rate limited to 5 attempts per minute per IP.
    """
    # Rate limiting
    client_ip = get_client_ip(request)
    allowed, retry_after = login_limiter.is_allowed(client_ip)
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Too many login attempts. Try again in {retry_after} seconds.",
            headers={"Retry-After": str(retry_after)},
        )

    # Find user by email
    result = await db.execute(select(User).where(User.email == user_data.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(user_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    # Check if user is approved
    if user.status != UserStatus.APPROVED:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User status is {user.status.value}. Please wait for admin approval.",
        )

    # Create access token
    access_token = create_access_token(data={"user_id": user.id})

    return Token(
        access_token=access_token,
        user=UserResponse.model_validate(user),
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
):
    """Get current user information (requires authentication)."""
    return current_user
