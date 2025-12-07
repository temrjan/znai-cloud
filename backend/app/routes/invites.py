"""Invite routes - separated from organizations for cleaner code."""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import get_db
from backend.app.middleware.auth import get_current_user, require_org_admin
from backend.app.models.user import User
from backend.app.schemas.invite import (
    InviteAcceptRequest,
    InviteCreate,
    InviteDetailsResponse,
    InviteResponse,
)
from backend.app.schemas.organization import OrganizationResponse
from backend.app.services.invite_service import (
    InviteExhaustedError,
    InviteExpiredError,
    InviteInvalidError,
    InviteService,
    UserAlreadyInOrganizationError,
)
from backend.app.services.organization_service import OrganizationService

router = APIRouter(prefix="/organizations", tags=["Invites"])


@router.post("/my/invites", response_model=InviteResponse, status_code=status.HTTP_201_CREATED)
async def create_invite(
    invite_data: InviteCreate,
    current_user: User = Depends(require_org_admin),
    db: AsyncSession = Depends(get_db),
):
    """Create an invite code (admin/owner only)."""
    service = InviteService(db)
    invite = await service.create(
        organization_id=current_user.organization_id,
        created_by_user_id=current_user.id,
        max_uses=invite_data.max_uses,
        expires_in_hours=invite_data.expires_in_hours,
        default_role=invite_data.default_role,
    )

    await db.commit()
    await db.refresh(invite)

    return InviteResponse(
        id=invite.id,
        code=invite.code,
        organization_id=invite.organization_id,
        organization_name=None,
        max_uses=invite.max_uses,
        used_count=invite.used_count,
        expires_at=invite.expires_at,
        status=invite.status,
        default_role=invite.default_role,
        created_by_user_id=invite.created_by_user_id,
        created_at=invite.created_at,
    )


@router.get("/my/invites", response_model=list[InviteResponse])
async def list_invites(
    current_user: User = Depends(require_org_admin),
    db: AsyncSession = Depends(get_db),
):
    """List all invites for the organization (admin/owner only)."""
    service = InviteService(db)
    invites = await service.list_by_organization(current_user.organization_id)

    return [
        InviteResponse(
            id=invite.id,
            code=invite.code,
            organization_id=invite.organization_id,
            organization_name=org_name,
            max_uses=invite.max_uses,
            used_count=invite.used_count,
            expires_at=invite.expires_at,
            status=invite.status,
            default_role=invite.default_role,
            created_by_user_id=invite.created_by_user_id,
            created_at=invite.created_at,
        )
        for invite, org_name in invites
    ]


@router.delete("/my/invites/{invite_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_invite(
    invite_id: int,
    current_user: User = Depends(require_org_admin),
    db: AsyncSession = Depends(get_db),
):
    """Revoke an invite (admin/owner only)."""
    service = InviteService(db)
    invite = await service.get_by_id(invite_id)

    if not invite or invite.organization_id != current_user.organization_id:
        raise HTTPException(status_code=404, detail="Invite not found")

    await service.revoke(invite)
    await db.commit()


@router.get("/invites/{code}", response_model=InviteDetailsResponse)
async def get_invite_details(code: str, db: AsyncSession = Depends(get_db)):
    """Get invite details (public endpoint for registration)."""
    service = InviteService(db)
    details = await service.get_details(code)

    return InviteDetailsResponse(
        organization_name=details.get("organization_name", "Unknown"),
        default_role=details.get("default_role", "member"),
        expires_at=details.get("expires_at"),
        is_valid=details.get("is_valid", False),
    )


@router.post("/invites/accept", response_model=OrganizationResponse)
async def accept_invite(
    request: InviteAcceptRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Accept an invite and join organization."""
    service = InviteService(db)
    invite = await service.get_by_code(request.code)

    if not invite:
        raise HTTPException(status_code=404, detail="Invite not found")

    try:
        organization = await service.accept(invite, current_user)
        await db.commit()
        await db.refresh(organization)

        org_service = OrganizationService(db)
        member_count = await org_service.get_member_count(organization.id)
        doc_count = await org_service.get_document_count(organization.id)

        response = OrganizationResponse.model_validate(organization)
        response.current_members_count = member_count
        response.current_documents_count = doc_count
        return response

    except UserAlreadyInOrganizationError:
        raise HTTPException(status_code=400, detail="You are already in an organization")
    except InviteInvalidError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except InviteExpiredError:
        raise HTTPException(status_code=400, detail="Invite has expired")
    except InviteExhaustedError:
        raise HTTPException(status_code=400, detail="Invite has been fully used")
