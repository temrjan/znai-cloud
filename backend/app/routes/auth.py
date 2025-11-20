"""Authentication routes."""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.database import get_db
from backend.app.models.user import User, UserStatus, UserRole
from backend.app.models.quota import UserQuota
from backend.app.schemas.user import UserCreate, UserLogin, Token, UserResponse
from backend.app.utils.security import hash_password, verify_password, create_access_token
from backend.app.config import settings


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Register a new user.

    User status will be 'pending' and requires admin approval.
    """
    # Check if email already exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create new user
    hashed_password = hash_password(user_data.password)

    new_user = User(
        email=user_data.email,
        password_hash=hashed_password,
        full_name=user_data.full_name,
        status=UserStatus.PENDING,
        role=UserRole.USER,
    )

    db.add(new_user)
    await db.flush()  # Get user.id

    # Create user quota
    quota = UserQuota(
        user_id=new_user.id,
        max_documents=settings.free_user_max_documents,
        max_queries_daily=settings.free_user_max_queries_daily,
    )
    db.add(quota)

    await db.commit()
    await db.refresh(new_user)

    return new_user


@router.post("/login", response_model=Token)
async def login(user_data: UserLogin, db: AsyncSession = Depends(get_db)):
    """
    Login user and return JWT token.

    User must be approved by admin to login.
    """
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
    db: AsyncSession = Depends(get_db),
):
    """Get current user information (requires authentication)."""
    # This is a placeholder - will be implemented with auth middleware
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Not implemented yet",
    )
