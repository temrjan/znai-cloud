"""Organization management routes."""
from datetime import datetime, timedelta
from typing import List
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload

from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.models.organization import Organization, OrganizationStatus
from backend.app.models.organization_invite import OrganizationInvite, InviteStatus
from backend.app.models.organization_member import OrganizationMember
from backend.app.models.organization_settings import OrganizationSettings
from backend.app.models.document import Document
from backend.app.models.query_log import QueryLog
from backend.app.schemas.organization import (
    OrganizationCreate,
    OrganizationUpdate,
    OrganizationResponse,
    OrganizationMemberResponse,
    OrganizationStatsResponse,
)
from backend.app.schemas.invite import (
    InviteCreate,
    InviteResponse,
    InviteAcceptRequest,
    InviteDetailsResponse,
)
from backend.app.schemas.settings import (
    OrganizationSettingsUpdate,
    OrganizationSettingsResponse,
)
from backend.app.middleware.auth import (
    get_current_user,
    require_org_member,
    require_org_admin,
    require_org_owner,
)


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
    """
    Create a new organization.

    User creating the organization becomes the owner automatically.
    """
    # Check if user is already in an organization
    if current_user.organization_id is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are already a member of an organization",
        )

    # Generate slug if not provided
    slug = org_data.slug
    if not slug:
        slug = org_data.name.lower().replace(" ", "-")
        # Remove special characters
        slug = "".join(c for c in slug if c.isalnum() or c == "-")

    # Check if slug is unique
    result = await db.execute(select(Organization).where(Organization.slug == slug))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Organization slug '{slug}' is already taken",
        )

    # Create organization
    organization = Organization(
        name=org_data.name,
        slug=slug,
        owner_id=current_user.id,
        max_members=org_data.max_members,
        max_documents=org_data.max_documents,
        max_queries_org_daily=org_data.max_queries_daily,
        status=OrganizationStatus.ACTIVE,
    )

    db.add(organization)
    await db.flush()

    # Update user to be owner
    current_user.organization_id = organization.id
    current_user.role_in_org = "owner"

    # Create organization member record
    member_record = OrganizationMember(
        organization_id=organization.id,
        user_id=current_user.id,
        role="owner",
        joined_at=datetime.utcnow(),
    )
    db.add(member_record)

    # Create default organization settings
    settings = OrganizationSettings(organization_id=organization.id)
    db.add(settings)

    await db.commit()
    await db.refresh(organization)

    # Add computed fields
    org_response = OrganizationResponse.model_validate(organization)
    org_response.current_members_count = 1
    org_response.current_documents_count = 0

    return org_response


@router.get("/my", response_model=OrganizationResponse)
async def get_my_organization(
    current_user: User = Depends(require_org_member),
    db: AsyncSession = Depends(get_db),
):
    """Get current user's organization details."""
    result = await db.execute(
        select(Organization).where(Organization.id == current_user.organization_id)
    )
    organization = result.scalar_one_or_none()

    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )

    # Get member count
    member_count_result = await db.execute(
        select(func.count(User.id)).where(
            User.organization_id == organization.id
        )
    )
    member_count = member_count_result.scalar()

    # Get document count
    doc_count_result = await db.execute(
        select(func.count(Document.id)).where(
            Document.organization_id == organization.id
        )
    )
    doc_count = doc_count_result.scalar()

    # Build response manually to avoid validation errors
    return OrganizationResponse(
        id=organization.id,
        name=organization.name,
        slug=organization.slug,
        owner_id=organization.owner_id,
        max_members=organization.max_members,
        current_members_count=member_count or 0,
        max_documents=organization.max_documents,
        current_documents_count=doc_count or 0,
        max_queries_daily=organization.max_queries_org_daily,
        status=organization.status,
        created_at=organization.created_at,
        updated_at=organization.updated_at,
    )


@router.patch("/my", response_model=OrganizationResponse)
async def update_my_organization(
    org_update: OrganizationUpdate,
    current_user: User = Depends(require_org_owner),
    db: AsyncSession = Depends(get_db),
):
    """Update organization details. Only owner can update."""
    result = await db.execute(
        select(Organization).where(Organization.id == current_user.organization_id)
    )
    organization = result.scalar_one_or_none()

    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )

    # Update fields
    if org_update.name is not None:
        organization.name = org_update.name
    if org_update.max_members is not None:
        organization.max_members = org_update.max_members
    if org_update.max_documents is not None:
        organization.max_documents = org_update.max_documents
    if org_update.max_queries_daily is not None:
        organization.max_queries_org_daily = org_update.max_queries_daily

    organization.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(organization)

    # Get counts
    member_count = await db.scalar(
        select(func.count(User.id)).where(User.organization_id == organization.id)
    )
    doc_count = await db.scalar(
        select(func.count(Document.id)).where(Document.organization_id == organization.id)
    )

    org_response = OrganizationResponse.model_validate(organization)
    org_response.current_members_count = member_count or 0
    org_response.current_documents_count = doc_count or 0

    return org_response


@router.delete("/my", status_code=status.HTTP_204_NO_CONTENT)
async def delete_my_organization(
    current_user: User = Depends(require_org_owner),
    db: AsyncSession = Depends(get_db),
):
    """Delete organization. Only owner can delete. This will remove all members."""
    result = await db.execute(
        select(Organization).where(Organization.id == current_user.organization_id)
    )
    organization = result.scalar_one_or_none()

    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )

    # Remove all members from organization (cascade will handle member records)
    await db.execute(
        select(User).where(User.organization_id == organization.id)
    )
    all_members = (await db.execute(
        select(User).where(User.organization_id == organization.id)
    )).scalars().all()

    for member in all_members:
        member.organization_id = None
        member.role_in_org = None

    # Soft delete organization
    organization.status = OrganizationStatus.DELETED
    organization.deleted_at = datetime.utcnow()

    await db.commit()


# ============================================================================
# MEMBER MANAGEMENT
# ============================================================================

@router.get("/my/members", response_model=List[OrganizationMemberResponse])
async def list_organization_members(
    current_user: User = Depends(require_org_member),
    db: AsyncSession = Depends(get_db),
):
    """List all members of current user's organization."""
    result = await db.execute(
        select(User).where(
            User.organization_id == current_user.organization_id
        ).order_by(User.created_at)
    )
    members = result.scalars().all()

    # Get join dates from member records
    member_records_result = await db.execute(
        select(OrganizationMember).where(
            OrganizationMember.organization_id == current_user.organization_id,
            OrganizationMember.left_at.is_(None)
        )
    )
    member_records = {m.user_id: m for m in member_records_result.scalars().all()}

    response = []
    for member in members:
        member_record = member_records.get(member.id)
        joined_at = member_record.joined_at if member_record else member.created_at

        response.append(
            OrganizationMemberResponse(
                user_id=member.id,
                email=member.email,
                full_name=member.full_name,
                role=member.role_in_org or "member",
                joined_at=joined_at,
            )
        )

    return response


@router.delete("/my/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member(
    user_id: int,
    current_user: User = Depends(require_org_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Remove a member from organization.

    Only admins and owner can remove members.
    Owner cannot be removed.
    """
    # Get target user
    result = await db.execute(select(User).where(User.id == user_id))
    target_user = result.scalar_one_or_none()

    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Check if user is in same organization
    if target_user.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not in your organization",
        )

    # Cannot remove owner
    if target_user.role_in_org == "owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot remove organization owner",
        )

    # Update member record to mark as left
    member_result = await db.execute(
        select(OrganizationMember).where(
            OrganizationMember.organization_id == current_user.organization_id,
            OrganizationMember.user_id == user_id,
            OrganizationMember.left_at.is_(None)
        )
    )
    member_record = member_result.scalar_one_or_none()
    if member_record:
        member_record.left_at = datetime.utcnow()

    # Remove user from organization
    target_user.organization_id = None
    target_user.role_in_org = None

    await db.commit()


# ============================================================================
# INVITE MANAGEMENT
# ============================================================================

@router.post("/my/invites", response_model=InviteResponse, status_code=status.HTTP_201_CREATED)
async def create_invite(
    invite_data: InviteCreate,
    current_user: User = Depends(require_org_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Create an invite code for the organization.

    Only admins and owner can create invites.
    """
    # Get organization
    result = await db.execute(
        select(Organization).where(Organization.id == current_user.organization_id)
    )
    organization = result.scalar_one_or_none()

    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )

    # Create invite
    expires_at = datetime.utcnow() + timedelta(hours=invite_data.expires_in_hours)

    invite = OrganizationInvite(
        code=uuid4(),
        organization_id=current_user.organization_id,
        max_uses=invite_data.max_uses,
        used_count=0,
        expires_at=expires_at,
        default_role=invite_data.default_role,
        created_by_user_id=current_user.id,
        status=InviteStatus.ACTIVE,
    )

    db.add(invite)
    await db.commit()
    await db.refresh(invite)

    return InviteResponse(
        id=invite.id,
        code=invite.code,
        organization_id=invite.organization_id,
        organization_name=organization.name,
        max_uses=invite.max_uses,
        used_count=invite.used_count,
        expires_at=invite.expires_at,
        status=invite.status,
        default_role=invite.default_role,
        created_by_user_id=invite.created_by_user_id,
        created_at=invite.created_at,
    )


@router.get("/my/invites", response_model=List[InviteResponse])
async def list_invites(
    current_user: User = Depends(require_org_admin),
    db: AsyncSession = Depends(get_db),
):
    """List all invites for the organization."""
    result = await db.execute(
        select(OrganizationInvite, Organization.name)
        .join(Organization, OrganizationInvite.organization_id == Organization.id)
        .where(OrganizationInvite.organization_id == current_user.organization_id)
        .order_by(OrganizationInvite.created_at.desc())
    )
    invites = result.all()

    response = []
    for invite, org_name in invites:
        response.append(
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
        )

    return response


@router.delete("/my/invites/{invite_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_invite(
    invite_id: int,
    current_user: User = Depends(require_org_admin),
    db: AsyncSession = Depends(get_db),
):
    """Revoke an invite code."""
    result = await db.execute(
        select(OrganizationInvite).where(
            OrganizationInvite.id == invite_id,
            OrganizationInvite.organization_id == current_user.organization_id,
        )
    )
    invite = result.scalar_one_or_none()

    if not invite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invite not found",
        )

    invite.status = InviteStatus.REVOKED
    await db.commit()


@router.get("/invites/{code}", response_model=InviteDetailsResponse)
async def get_invite_details(
    code: str,
    db: AsyncSession = Depends(get_db),
):
    """Get public details of an invite code (no auth required)."""
    try:
        import uuid
        code_uuid = uuid.UUID(code)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid invite code format",
        )

    result = await db.execute(
        select(OrganizationInvite, Organization.name)
        .join(Organization, OrganizationInvite.organization_id == Organization.id)
        .where(OrganizationInvite.code == code_uuid)
    )
    row = result.one_or_none()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invite not found",
        )

    invite, org_name = row

    # Check if valid
    is_valid = (
        invite.status == InviteStatus.ACTIVE
        and invite.used_count < invite.max_uses
        and invite.expires_at > datetime.utcnow()
    )

    remaining_uses = max(0, invite.max_uses - invite.used_count)

    return InviteDetailsResponse(
        code=invite.code,
        organization_name=org_name,
        expires_at=invite.expires_at,
        is_valid=is_valid,
        remaining_uses=remaining_uses,
    )


@router.post("/invites/accept", response_model=OrganizationResponse)
async def accept_invite(
    request: InviteAcceptRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Accept an invite and join organization."""
    # Check if user is already in an organization
    if current_user.organization_id is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are already a member of an organization",
        )

    # Get invite
    result = await db.execute(
        select(OrganizationInvite).where(OrganizationInvite.code == request.code)
    )
    invite = result.scalar_one_or_none()

    if not invite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invite not found",
        )

    # Validate invite
    if invite.status != InviteStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invite is {invite.status.value}",
        )

    if invite.used_count >= invite.max_uses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invite has been fully used",
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

    if not organization or organization.status != OrganizationStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization is not active",
        )

    # Check member limit
    member_count = await db.scalar(
        select(func.count(User.id)).where(User.organization_id == organization.id)
    )
    if member_count >= organization.max_members:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization has reached member limit",
        )

    # Join organization
    current_user.organization_id = organization.id
    current_user.role_in_org = invite.default_role

    # Create member record
    member_record = OrganizationMember(
        organization_id=organization.id,
        user_id=current_user.id,
        role=invite.default_role,
        joined_at=datetime.utcnow(),
        invited_by_user_id=invite.created_by_user_id,
    )
    db.add(member_record)

    # Increment invite usage
    invite.used_count += 1

    await db.commit()
    await db.refresh(organization)

    # Get counts
    doc_count = await db.scalar(
        select(func.count(Document.id)).where(Document.organization_id == organization.id)
    )

    org_response = OrganizationResponse.model_validate(organization)
    org_response.current_members_count = member_count + 1
    org_response.current_documents_count = doc_count or 0

    return org_response


# ============================================================================
# SETTINGS MANAGEMENT
# ============================================================================

@router.get("/my/settings", response_model=OrganizationSettingsResponse)
async def get_organization_settings(
    current_user: User = Depends(require_org_member),
    db: AsyncSession = Depends(get_db),
):
    """Get organization AI settings."""
    result = await db.execute(
        select(OrganizationSettings).where(
            OrganizationSettings.organization_id == current_user.organization_id
        )
    )
    settings = result.scalar_one_or_none()

    if not settings:
        # Create default settings if they don't exist
        settings = OrganizationSettings(organization_id=current_user.organization_id)
        db.add(settings)
        await db.commit()
        await db.refresh(settings)

    # Return with response_language alias for frontend compatibility
    return OrganizationSettingsResponse(
        organization_id=settings.organization_id,
        custom_system_prompt=settings.custom_system_prompt,
        custom_temperature=settings.custom_temperature,
        custom_max_tokens=settings.custom_max_tokens,
        custom_model=settings.custom_model,
        custom_terminology=settings.custom_terminology,
        primary_language=settings.primary_language,
        response_language=settings.primary_language,  # Alias for frontend
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )


@router.patch("/my/settings", response_model=OrganizationSettingsResponse)
async def update_organization_settings(
    settings_update: OrganizationSettingsUpdate,
    current_user: User = Depends(require_org_admin),
    db: AsyncSession = Depends(get_db),
):
    """Update organization AI settings. Only admins and owner can update."""
    result = await db.execute(
        select(OrganizationSettings).where(
            OrganizationSettings.organization_id == current_user.organization_id
        )
    )
    settings = result.scalar_one_or_none()

    if not settings:
        settings = OrganizationSettings(organization_id=current_user.organization_id)
        db.add(settings)
        await db.flush()

    # Update fields
    update_data = settings_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(settings, field, value)

    await db.commit()
    await db.refresh(settings)

    return settings


# ============================================================================
# STATISTICS
# ============================================================================

@router.get("/my/stats", response_model=OrganizationStatsResponse)
async def get_organization_stats(
    current_user: User = Depends(require_org_member),
    db: AsyncSession = Depends(get_db),
):
    """Get organization usage statistics."""
    # Get organization
    org_result = await db.execute(
        select(Organization).where(Organization.id == current_user.organization_id)
    )
    organization = org_result.scalar_one()

    # Get counts
    member_count = await db.scalar(
        select(func.count(User.id)).where(User.organization_id == organization.id)
    ) or 0

    doc_count = await db.scalar(
        select(func.count(Document.id)).where(Document.organization_id == organization.id)
    ) or 0

    # Get today's query count
    today = datetime.utcnow().date()
    query_count_today = await db.scalar(
        select(func.count(QueryLog.id)).where(
            QueryLog.organization_id == organization.id,
            func.date(QueryLog.created_at) == today,
        )
    ) or 0

    # Calculate quota usage percentages
    docs_usage = (doc_count / organization.max_documents * 100) if organization.max_documents > 0 else 0
    members_usage = (member_count / organization.max_members * 100) if organization.max_members > 0 else 0
    queries_usage = (query_count_today / organization.max_queries_org_daily * 100) if organization.max_queries_org_daily > 0 else 0

    return OrganizationStatsResponse(
        total_members=member_count,
        total_documents=doc_count,
        total_queries_today=query_count_today,
        documents_quota_usage=round(docs_usage, 2),
        members_quota_usage=round(members_usage, 2),
        queries_quota_usage=round(queries_usage, 2),
    )
