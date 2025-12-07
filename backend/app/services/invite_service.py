"""Invite service for organization invitations."""
import uuid
from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.organization import Organization, OrganizationStatus
from backend.app.models.organization_invite import InviteStatus, OrganizationInvite
from backend.app.models.organization_member import OrganizationMember
from backend.app.models.user import User


class InviteNotFoundError(Exception):
    """Invite not found."""
    pass


class InviteExpiredError(Exception):
    """Invite has expired."""
    pass


class InviteExhaustedError(Exception):
    """Invite has been fully used."""
    pass


class InviteInvalidError(Exception):
    """Invite is invalid (revoked or inactive)."""
    pass


class UserAlreadyInOrganizationError(Exception):
    """User is already in an organization."""
    pass


class InviteService:
    """Service for invite operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_code(self, code: str) -> OrganizationInvite | None:
        """Get invite by code."""
        result = await self.db.execute(
            select(OrganizationInvite).where(OrganizationInvite.code == code)
        )
        return result.scalar_one_or_none()

    async def get_by_id(self, invite_id: int) -> OrganizationInvite | None:
        """Get invite by ID."""
        result = await self.db.execute(
            select(OrganizationInvite).where(OrganizationInvite.id == invite_id)
        )
        return result.scalar_one_or_none()

    async def list_by_organization(self, org_id: int) -> list[OrganizationInvite]:
        """List all invites for organization."""
        result = await self.db.execute(
            select(OrganizationInvite, Organization.name)
            .join(Organization)
            .where(OrganizationInvite.organization_id == org_id)
            .order_by(OrganizationInvite.created_at.desc())
        )
        return result.all()

    async def create(
        self,
        organization_id: int,
        created_by_user_id: int,
        max_uses: int = 1,
        expires_in_hours: int = 168,
        default_role: str = "member",
    ) -> OrganizationInvite:
        """
        Create a new invite.

        Args:
            organization_id: Organization ID
            created_by_user_id: User creating the invite
            max_uses: Maximum number of uses
            expires_in_hours: Hours until expiration (default 7 days)
            default_role: Role for invited users

        Returns:
            Created invite
        """
        expires_at = datetime.utcnow() + timedelta(hours=expires_in_hours)

        invite = OrganizationInvite(
            organization_id=organization_id,
            code=str(uuid.uuid4()),
            max_uses=max_uses,
            expires_at=expires_at,
            status=InviteStatus.ACTIVE,
            default_role=default_role,
            created_by_user_id=created_by_user_id,
        )

        self.db.add(invite)
        await self.db.flush()
        return invite

    async def revoke(self, invite: OrganizationInvite) -> None:
        """Revoke an invite."""
        invite.status = InviteStatus.REVOKED

    async def validate(self, invite: OrganizationInvite) -> bool:
        """
        Validate invite is usable.

        Returns:
            True if valid

        Raises:
            InviteInvalidError: If status is not active
            InviteExpiredError: If expired
            InviteExhaustedError: If fully used
        """
        if invite.status != InviteStatus.ACTIVE:
            raise InviteInvalidError(f"Invite is {invite.status.value}")

        if invite.used_count >= invite.max_uses:
            raise InviteExhaustedError("Invite has been fully used")

        if invite.expires_at < datetime.utcnow():
            raise InviteExpiredError("Invite has expired")

        return True

    async def accept(
        self,
        invite: OrganizationInvite,
        user: User,
    ) -> Organization:
        """
        Accept invite and add user to organization.

        Args:
            invite: Invite to accept
            user: User accepting the invite

        Returns:
            Organization joined

        Raises:
            UserAlreadyInOrganizationError: User already in org
            InviteInvalidError: Invalid invite
        """
        # Check user not already in organization
        if user.organization_id is not None:
            raise UserAlreadyInOrganizationError()

        # Validate invite
        await self.validate(invite)

        # Get organization
        org_result = await self.db.execute(
            select(Organization).where(Organization.id == invite.organization_id)
        )
        organization = org_result.scalar_one_or_none()

        if not organization or organization.status != OrganizationStatus.ACTIVE:
            raise InviteInvalidError("Organization is not active")

        # Join organization
        user.organization_id = organization.id
        user.role_in_org = invite.default_role

        # Create member record
        member = OrganizationMember(
            organization_id=organization.id,
            user_id=user.id,
            role=invite.default_role,
            joined_at=datetime.utcnow(),
            invited_by_user_id=invite.created_by_user_id,
        )
        self.db.add(member)

        # Increment usage
        invite.used_count += 1

        return organization

    async def get_details(self, code: str) -> dict:
        """
        Get invite details for display.

        Returns:
            Dict with organization_name, default_role, is_valid, etc.
        """
        invite = await self.get_by_code(code)
        if not invite:
            return {
                "is_valid": False,
                "error": "Invite not found",
            }

        # Get organization name
        org_result = await self.db.execute(
            select(Organization).where(Organization.id == invite.organization_id)
        )
        organization = org_result.scalar_one_or_none()

        try:
            await self.validate(invite)
            is_valid = True
            error = None
        except Exception as e:
            is_valid = False
            error = str(e)

        return {
            "organization_name": organization.name if organization else "Unknown",
            "default_role": invite.default_role,
            "expires_at": invite.expires_at.isoformat(),
            "is_valid": is_valid,
            "error": error,
        }
