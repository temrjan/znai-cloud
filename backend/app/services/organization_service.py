"""Organization service for business logic."""
from datetime import datetime
from typing import Optional, List, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from backend.app.models.organization import Organization, OrganizationStatus
from backend.app.models.organization_member import OrganizationMember
from backend.app.models.organization_settings import OrganizationSettings
from backend.app.models.user import User
from backend.app.models.document import Document
from backend.app.models.query_log import QueryLog


class OrganizationNotFoundError(Exception):
    """Organization not found."""
    def __init__(self, org_id: int):
        self.org_id = org_id
        super().__init__(f"Organization {org_id} not found")


class MemberLimitReachedError(Exception):
    """Organization member limit reached."""
    pass


class PermissionDeniedError(Exception):
    """User does not have required permission."""
    pass


class OrganizationService:
    """Service for organization operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, org_id: int) -> Optional[Organization]:
        """Get organization by ID."""
        result = await self.db.execute(
            select(Organization).where(Organization.id == org_id)
        )
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Optional[Organization]:
        """Get organization by slug."""
        result = await self.db.execute(
            select(Organization).where(Organization.slug == slug)
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        name: str,
        owner: User,
        max_members: int = 10,
        max_documents: int = 50,
        max_queries_org_daily: int = 500,
    ) -> Organization:
        """
        Create a new organization.

        Args:
            name: Organization name
            owner: User who will be the owner
            max_members: Maximum members limit
            max_documents: Maximum documents limit
            max_queries_org_daily: Daily query limit

        Returns:
            Created organization
        """
        # Generate slug from name
        slug = name.lower().replace(" ", "-")
        base_slug = slug
        counter = 1
        while await self.get_by_slug(slug):
            slug = f"{base_slug}-{counter}"
            counter += 1

        organization = Organization(
            name=name,
            slug=slug,
            owner_id=owner.id,
            max_members=max_members,
            max_documents=max_documents,
            max_queries_org_daily=max_queries_org_daily,
            status=OrganizationStatus.ACTIVE,
        )

        self.db.add(organization)
        await self.db.flush()

        # Update user
        owner.organization_id = organization.id
        owner.role_in_org = "owner"

        # Create member record
        member = OrganizationMember(
            organization_id=organization.id,
            user_id=owner.id,
            role="owner",
            joined_at=datetime.utcnow(),
        )
        self.db.add(member)

        # Create default settings
        settings = OrganizationSettings(
            organization_id=organization.id,
            custom_max_tokens=1000,
            custom_temperature=0.5,
            primary_language="ru"
        )
        self.db.add(settings)

        return organization

    async def update(
        self,
        organization: Organization,
        updates: Dict[str, Any]
    ) -> Organization:
        """Update organization fields."""
        allowed_fields = ['name', 'max_members', 'max_documents', 'max_queries_org_daily']
        for field, value in updates.items():
            if field in allowed_fields and value is not None:
                setattr(organization, field, value)
        return organization

    async def soft_delete(self, organization: Organization) -> None:
        """Soft delete organization."""
        # Remove all members from organization
        members_result = await self.db.execute(
            select(User).where(User.organization_id == organization.id)
        )
        for member in members_result.scalars().all():
            member.organization_id = None
            member.role_in_org = None

        organization.status = OrganizationStatus.DELETED
        organization.deleted_at = datetime.utcnow()

    async def get_member_count(self, org_id: int) -> int:
        """Get current member count."""
        result = await self.db.scalar(
            select(func.count(User.id)).where(User.organization_id == org_id)
        )
        return result or 0

    async def get_document_count(self, org_id: int) -> int:
        """Get organization document count."""
        result = await self.db.scalar(
            select(func.count(Document.id)).where(Document.organization_id == org_id)
        )
        return result or 0

    async def get_stats(self, org_id: int) -> Dict[str, Any]:
        """Get organization statistics."""
        organization = await self.get_by_id(org_id)
        if not organization:
            raise OrganizationNotFoundError(org_id)

        member_count = await self.get_member_count(org_id)
        doc_count = await self.get_document_count(org_id)

        # Get today's query count
        today = datetime.utcnow().date()
        query_count_today = await self.db.scalar(
            select(func.count(QueryLog.id)).where(
                QueryLog.organization_id == org_id,
                func.date(QueryLog.created_at) == today,
            )
        ) or 0

        # Calculate quotas
        docs_usage = (doc_count / organization.max_documents * 100) if organization.max_documents > 0 else 0
        members_usage = (member_count / organization.max_members * 100) if organization.max_members > 0 else 0
        queries_usage = (query_count_today / organization.max_queries_org_daily * 100) if organization.max_queries_org_daily > 0 else 0

        return {
            "total_members": member_count,
            "total_documents": doc_count,
            "total_queries_today": query_count_today,
            "documents_quota_usage": round(docs_usage, 2),
            "members_quota_usage": round(members_usage, 2),
            "queries_quota_usage": round(queries_usage, 2),
        }

    async def transfer_ownership(
        self,
        organization: Organization,
        current_owner: User,
        new_owner: User,
    ) -> None:
        """
        Transfer organization ownership to another member.

        Args:
            organization: Organization to transfer
            current_owner: Current owner
            new_owner: New owner (must be member)

        Raises:
            PermissionDeniedError: If new_owner is not in organization
        """
        if new_owner.organization_id != organization.id:
            raise PermissionDeniedError("New owner must be a member of the organization")

        # Update organization
        organization.owner_id = new_owner.id

        # Update user roles
        current_owner.role_in_org = "admin"
        new_owner.role_in_org = "owner"

        # Update OrganizationMember records
        current_member_result = await self.db.execute(
            select(OrganizationMember).where(
                OrganizationMember.organization_id == organization.id,
                OrganizationMember.user_id == current_owner.id,
                OrganizationMember.left_at.is_(None)
            )
        )
        current_member = current_member_result.scalar_one_or_none()
        if current_member:
            current_member.role = "admin"

        new_owner_member_result = await self.db.execute(
            select(OrganizationMember).where(
                OrganizationMember.organization_id == organization.id,
                OrganizationMember.user_id == new_owner.id,
                OrganizationMember.left_at.is_(None)
            )
        )
        new_owner_member = new_owner_member_result.scalar_one_or_none()
        if new_owner_member:
            new_owner_member.role = "owner"
