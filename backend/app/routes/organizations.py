"""Organization routes - thin layer over services."""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.middleware.auth import (
    get_current_user,
    require_org_member,
    require_org_admin,
    require_org_owner,
)
from backend.app.schemas.organization import (
    OrganizationCreate,
    OrganizationUpdate,
    OrganizationResponse,
    OrganizationMemberResponse,
    OrganizationStatsResponse,
)
from backend.app.schemas.settings import OrganizationSettingsResponse, OrganizationSettingsUpdate
from backend.app.services.organization_service import (
    OrganizationService,
    OrganizationNotFoundError,
    PermissionDeniedError,
)
from backend.app.services.member_service import (
    MemberService,
    MemberNotFoundError,
    CannotRemoveOwnerError,
)
from backend.app.services.settings_service import SettingsService


router = APIRouter(prefix="/organizations", tags=["Organizations"])


# ============================================================================
# ORGANIZATION CRUD
# ============================================================================

@router.post("", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
async def create_organization(
    org_data: OrganizationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new organization. User becomes the owner."""
    if current_user.organization_id is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already in an organization",
        )

    service = OrganizationService(db)
    organization = await service.create(
        name=org_data.name,
        owner=current_user,
        max_members=org_data.max_members,
        max_documents=org_data.max_documents,
        max_queries_org_daily=org_data.max_queries_daily,
    )

    await db.commit()
    await db.refresh(organization)

    response = OrganizationResponse.model_validate(organization)
    response.current_members_count = 1
    response.current_documents_count = 0
    return response


@router.get("/my", response_model=OrganizationResponse)
async def get_my_organization(
    current_user: User = Depends(require_org_member),
    db: AsyncSession = Depends(get_db),
):
    """Get current user's organization."""
    service = OrganizationService(db)
    organization = await service.get_by_id(current_user.organization_id)

    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")

    member_count = await service.get_member_count(organization.id)
    doc_count = await service.get_document_count(organization.id)

    response = OrganizationResponse.model_validate(organization)
    response.current_members_count = member_count
    response.current_documents_count = doc_count
    return response


@router.patch("/my", response_model=OrganizationResponse)
async def update_my_organization(
    updates: OrganizationUpdate,
    current_user: User = Depends(require_org_admin),
    db: AsyncSession = Depends(get_db),
):
    """Update organization settings (admin/owner only)."""
    service = OrganizationService(db)
    organization = await service.get_by_id(current_user.organization_id)

    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")

    await service.update(organization, updates.model_dump(exclude_unset=True))
    await db.commit()
    await db.refresh(organization)

    member_count = await service.get_member_count(organization.id)
    doc_count = await service.get_document_count(organization.id)

    response = OrganizationResponse.model_validate(organization)
    response.current_members_count = member_count
    response.current_documents_count = doc_count
    return response


@router.delete("/my", status_code=status.HTTP_204_NO_CONTENT)
async def delete_my_organization(
    current_user: User = Depends(require_org_owner),
    db: AsyncSession = Depends(get_db),
):
    """Delete organization (owner only)."""
    service = OrganizationService(db)
    organization = await service.get_by_id(current_user.organization_id)

    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")

    await service.soft_delete(organization)
    await db.commit()


# ============================================================================
# MEMBER MANAGEMENT
# ============================================================================

@router.get("/my/members", response_model=List[OrganizationMemberResponse])
async def list_organization_members(
    current_user: User = Depends(require_org_member),
    db: AsyncSession = Depends(get_db),
):
    """List all members of the organization."""
    service = MemberService(db)
    members = await service.list_members(current_user.organization_id)

    return [
        OrganizationMemberResponse(
            user_id=m["user_id"],
            email=m["email"],
            full_name=m["full_name"],
            role=m["role"],
            joined_at=m["joined_at"],
        )
        for m in members
    ]


@router.delete("/my/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member(
    user_id: int,
    current_user: User = Depends(require_org_admin),
    db: AsyncSession = Depends(get_db),
):
    """Remove a member from the organization (admin/owner only)."""
    result = await db.execute(select(User).where(User.id == user_id))
    user_to_remove = result.scalar_one_or_none()

    if not user_to_remove:
        raise HTTPException(status_code=404, detail="User not found")

    service = MemberService(db)
    try:
        await service.remove_member(
            current_user.organization_id,
            user_to_remove,
            current_user,
        )
        await db.commit()
    except MemberNotFoundError:
        raise HTTPException(status_code=403, detail="User is not in your organization")
    except CannotRemoveOwnerError:
        raise HTTPException(status_code=403, detail="Cannot remove organization owner")


# ============================================================================
# SETTINGS
# ============================================================================

@router.get("/my/settings", response_model=OrganizationSettingsResponse)
async def get_organization_settings(
    current_user: User = Depends(require_org_member),
    db: AsyncSession = Depends(get_db),
):
    """Get organization settings."""
    service = SettingsService(db)
    settings = await service.get_or_create(current_user.organization_id)
    await db.commit()
    return OrganizationSettingsResponse.model_validate(settings)


@router.patch("/my/settings", response_model=OrganizationSettingsResponse)
async def update_organization_settings(
    updates: OrganizationSettingsUpdate,
    current_user: User = Depends(require_org_admin),
    db: AsyncSession = Depends(get_db),
):
    """Update organization settings (admin/owner only)."""
    service = SettingsService(db)
    settings = await service.update(
        current_user.organization_id,
        updates.model_dump(exclude_unset=True),
        current_user.id,
    )
    await db.commit()
    await db.refresh(settings)
    return OrganizationSettingsResponse.model_validate(settings)


# ============================================================================
# STATISTICS
# ============================================================================

@router.get("/my/stats", response_model=OrganizationStatsResponse)
async def get_organization_stats(
    current_user: User = Depends(require_org_member),
    db: AsyncSession = Depends(get_db),
):
    """Get organization usage statistics."""
    service = OrganizationService(db)
    try:
        stats = await service.get_stats(current_user.organization_id)
        return OrganizationStatsResponse(**stats)
    except OrganizationNotFoundError:
        raise HTTPException(status_code=404, detail="Organization not found")


# ============================================================================
# OWNERSHIP TRANSFER
# ============================================================================

@router.post("/my/transfer-ownership/{new_owner_id}", status_code=status.HTTP_200_OK)
async def transfer_ownership(
    new_owner_id: int,
    current_user: User = Depends(require_org_owner),
    db: AsyncSession = Depends(get_db),
):
    """Transfer organization ownership (owner only)."""
    result = await db.execute(select(User).where(User.id == new_owner_id))
    new_owner = result.scalar_one_or_none()

    if not new_owner:
        raise HTTPException(status_code=404, detail="User not found")

    if new_owner.id == current_user.id:
        raise HTTPException(status_code=400, detail="You are already the owner")

    service = OrganizationService(db)
    organization = await service.get_by_id(current_user.organization_id)

    try:
        await service.transfer_ownership(organization, current_user, new_owner)
        await db.commit()
        return {
            "message": "Ownership transferred successfully",
            "new_owner_id": new_owner.id,
            "new_owner_email": new_owner.email,
        }
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))


# ============================================================================
# TELEGRAM BOT
# ============================================================================

from backend.app.services.telegram_bot import validate_bot_token, setup_bot_webhook, TelegramBotService
# TelegramBotSetupRequest and TelegramBotResponse defined below
from pydantic import BaseModel


class TelegramBotSetupRequest(BaseModel):
    """Request to setup telegram bot."""
    bot_token: str


class TelegramBotResponse(BaseModel):
    """Response with telegram bot info."""
    enabled: bool
    bot_username: str | None = None
    webhook_url: str | None = None


@router.post("/my/telegram-bot", response_model=TelegramBotResponse)
async def setup_telegram_bot(
    request: TelegramBotSetupRequest,
    current_user: User = Depends(require_org_admin),
    db: AsyncSession = Depends(get_db),
):
    """Setup Telegram bot for organization."""
    # Validate token
    bot_info = await validate_bot_token(request.bot_token)
    if not bot_info:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid bot token. Please check the token and try again."
        )
    
    # Setup webhook
    base_url = "https://znai.cloud"  # TODO: move to config
    success, result = await setup_bot_webhook(
        request.bot_token,
        current_user.organization_id,
        base_url
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to setup webhook: {result}"
        )
    
    # Save to settings
    service = SettingsService(db)
    settings = await service.update(
        current_user.organization_id,
        {
            "telegram_bot_token": request.bot_token,
            "telegram_bot_enabled": True,
            "telegram_bot_username": bot_info.get("username"),
            "telegram_webhook_secret": result,
        },
        current_user.id,
    )
    await db.commit()
    
    webhook_url = f"{base_url}/api/telegram/webhook/{current_user.organization_id}"
    
    return TelegramBotResponse(
        enabled=True,
        bot_username=bot_info.get("username"),
        webhook_url=webhook_url
    )


@router.get("/my/telegram-bot", response_model=TelegramBotResponse)
async def get_telegram_bot_status(
    current_user: User = Depends(require_org_member),
    db: AsyncSession = Depends(get_db),
):
    """Get Telegram bot status for organization."""
    service = SettingsService(db)
    settings = await service.get_by_org_id(current_user.organization_id)
    
    if not settings or not settings.telegram_bot_enabled:
        return TelegramBotResponse(enabled=False)
    
    webhook_url = f"https://znai.cloud/api/telegram/webhook/{current_user.organization_id}"
    
    return TelegramBotResponse(
        enabled=True,
        bot_username=settings.telegram_bot_username,
        webhook_url=webhook_url
    )


@router.delete("/my/telegram-bot", status_code=status.HTTP_200_OK)
async def disable_telegram_bot(
    current_user: User = Depends(require_org_admin),
    db: AsyncSession = Depends(get_db),
):
    """Disable Telegram bot for organization."""
    service = SettingsService(db)
    settings = await service.get_by_org_id(current_user.organization_id)
    
    if settings and settings.telegram_bot_token:
        # Delete webhook
        bot = TelegramBotService(settings.telegram_bot_token)
        await bot.delete_webhook()
        
        # Clear settings
        await service.update(
            current_user.organization_id,
            {
                "telegram_bot_token": None,
                "telegram_bot_enabled": False,
                "telegram_bot_username": None,
                "telegram_webhook_secret": None,
            },
            current_user.id,
        )
        await db.commit()
    
    return {"message": "Telegram bot disabled"}
