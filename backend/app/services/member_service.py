"""Member service for organization member management."""
from datetime import datetime
from typing import Optional, List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.models.organization import Organization
from backend.app.models.organization_member import OrganizationMember
from backend.app.models.user import User


class MemberNotFoundError(Exception):
    """Member not found."""
    pass


class CannotRemoveOwnerError(Exception):
    """Cannot remove organization owner."""
    pass


class MemberService:
    """Service for organization member operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_members(self, org_id: int) -> List[dict]:
        """
        List all members of organization.

        Returns:
            List of member dicts with user info and role
        """
        # Get users in organization
        users_result = await self.db.execute(
            select(User).where(
                User.organization_id == org_id
            ).order_by(User.created_at)
        )
        users = users_result.scalars().all()

        # Get member records
        members_result = await self.db.execute(
            select(OrganizationMember).where(
                OrganizationMember.organization_id == org_id,
                OrganizationMember.left_at.is_(None)
            )
        )
        member_records = {m.user_id: m for m in members_result.scalars().all()}

        result = []
        for user in users:
            member_record = member_records.get(user.id)
            role = member_record.role if member_record else (user.role_in_org or "member")
            joined_at = member_record.joined_at if member_record else user.created_at

            result.append({
                "user_id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "role": role,
                "joined_at": joined_at,
            })

        return result

    async def remove_member(
        self,
        org_id: int,
        user_to_remove: User,
        removed_by: User,
    ) -> None:
        """
        Remove a member from organization.

        Args:
            org_id: Organization ID
            user_to_remove: User to remove
            removed_by: Admin/owner performing the action

        Raises:
            MemberNotFoundError: User not in organization
            CannotRemoveOwnerError: Trying to remove owner
        """
        # Verify user is in organization
        if user_to_remove.organization_id != org_id:
            raise MemberNotFoundError("User is not in this organization")

        # Cannot remove owner
        if user_to_remove.is_org_owner():
            raise CannotRemoveOwnerError()

        # Update member record
        member_result = await self.db.execute(
            select(OrganizationMember).where(
                OrganizationMember.organization_id == org_id,
                OrganizationMember.user_id == user_to_remove.id,
                OrganizationMember.left_at.is_(None)
            )
        )
        member_record = member_result.scalar_one_or_none()
        if member_record:
            member_record.left_at = datetime.utcnow()

        # Remove from organization
        user_to_remove.organization_id = None
        user_to_remove.role_in_org = None

    async def update_role(
        self,
        org_id: int,
        user: User,
        new_role: str,
    ) -> None:
        """
        Update member's role.

        Args:
            org_id: Organization ID
            user: User to update
            new_role: New role (member, admin)
        """
        if new_role not in ['member', 'admin']:
            raise ValueError("Role must be 'member' or 'admin'")

        # Update user
        user.role_in_org = new_role

        # Update member record
        member_result = await self.db.execute(
            select(OrganizationMember).where(
                OrganizationMember.organization_id == org_id,
                OrganizationMember.user_id == user.id,
                OrganizationMember.left_at.is_(None)
            )
        )
        member_record = member_result.scalar_one_or_none()
        if member_record:
            member_record.role = new_role
