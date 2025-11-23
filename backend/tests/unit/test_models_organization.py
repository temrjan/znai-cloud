"""Unit tests for Organization models."""
import uuid
from datetime import datetime, timedelta

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from backend.app.models.organization import Organization, OrganizationStatus
from backend.app.models.organization_invite import OrganizationInvite, InviteStatus
from backend.app.models.organization_member import OrganizationMember
from backend.app.models.organization_settings import OrganizationSettings
from backend.app.models.user import User, UserStatus, UserRole
from backend.app.models.document import Document, DocumentStatus


@pytest.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create a test user."""
    user = User(
        email="test@example.com",
        password_hash="hashed_password",
        full_name="Test User",
        status=UserStatus.APPROVED,
        role=UserRole.USER
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def test_organization(db_session: AsyncSession, test_user: User) -> Organization:
    """Create a test organization."""
    org = Organization(
        name="Test Organization",
        slug="test-org",
        owner_id=test_user.id
    )
    db_session.add(org)
    await db_session.commit()
    await db_session.refresh(org)
    return org


class TestOrganizationModel:
    """Tests for Organization model."""

    @pytest.mark.asyncio
    async def test_create_organization(self, db_session: AsyncSession, test_user: User):
        """Test creating an organization with default values."""
        org = Organization(
            name="New Organization",
            slug="new-org",
            owner_id=test_user.id
        )
        db_session.add(org)
        await db_session.commit()
        await db_session.refresh(org)

        # Check default values
        assert org.id is not None
        assert org.name == "New Organization"
        assert org.slug == "new-org"
        assert org.owner_id == test_user.id
        assert org.max_members == 10
        assert org.max_documents == 50
        assert org.max_storage_mb == 1000
        assert org.max_queries_per_user_daily == 100
        assert org.max_queries_org_daily == 500
        assert org.status == OrganizationStatus.ACTIVE
        assert org.created_at is not None
        assert org.updated_at is not None  # Has default value
        assert org.deleted_at is None

    @pytest.mark.asyncio
    async def test_organization_required_fields(self, db_session: AsyncSession, test_user: User):
        """Test that required fields are enforced."""
        # Missing name
        with pytest.raises(Exception):  # Will raise IntegrityError or similar
            org = Organization(
                slug="test-slug",
                owner_id=test_user.id
            )
            db_session.add(org)
            await db_session.commit()

        await db_session.rollback()

        # Missing slug
        with pytest.raises(Exception):
            org = Organization(
                name="Test Org",
                owner_id=test_user.id
            )
            db_session.add(org)
            await db_session.commit()

    @pytest.mark.asyncio
    async def test_organization_unique_slug(self, db_session: AsyncSession, test_user: User):
        """Test that slug must be unique."""
        org1 = Organization(
            name="Org One",
            slug="same-slug",
            owner_id=test_user.id
        )
        db_session.add(org1)
        await db_session.commit()

        # Try to create another org with same slug
        org2 = Organization(
            name="Org Two",
            slug="same-slug",
            owner_id=test_user.id
        )
        db_session.add(org2)

        with pytest.raises(IntegrityError):
            await db_session.commit()

    @pytest.mark.asyncio
    async def test_organization_relationships(self, db_session: AsyncSession, test_organization: Organization, test_user: User):
        """Test organization relationships."""
        # Test owner relationship
        await db_session.refresh(test_organization, ["owner"])
        assert test_organization.owner is not None
        assert test_organization.owner.id == test_user.id
        assert test_organization.owner.email == test_user.email

        # Test members relationship
        # Add user to organization
        test_user.organization_id = test_organization.id
        test_user.role_in_org = "admin"
        await db_session.commit()
        await db_session.refresh(test_organization, ["members"])

        assert len(test_organization.members) == 1
        assert test_organization.members[0].id == test_user.id

    @pytest.mark.asyncio
    async def test_organization_status_enum(self, db_session: AsyncSession, test_user: User):
        """Test organization status enum values."""
        org = Organization(
            name="Test Org",
            slug="test-org-status",
            owner_id=test_user.id,
            status=OrganizationStatus.SUSPENDED
        )
        db_session.add(org)
        await db_session.commit()
        await db_session.refresh(org)

        assert org.status == OrganizationStatus.SUSPENDED

        # Update to deleted
        org.status = OrganizationStatus.DELETED
        org.deleted_at = datetime.utcnow()
        await db_session.commit()
        await db_session.refresh(org)

        assert org.status == OrganizationStatus.DELETED
        assert org.deleted_at is not None

    @pytest.mark.asyncio
    async def test_organization_custom_quotas(self, db_session: AsyncSession, test_user: User):
        """Test setting custom quota values."""
        org = Organization(
            name="Premium Org",
            slug="premium-org",
            owner_id=test_user.id,
            max_members=50,
            max_documents=200,
            max_storage_mb=5000,
            max_queries_per_user_daily=500,
            max_queries_org_daily=2000
        )
        db_session.add(org)
        await db_session.commit()
        await db_session.refresh(org)

        assert org.max_members == 50
        assert org.max_documents == 200
        assert org.max_storage_mb == 5000
        assert org.max_queries_per_user_daily == 500
        assert org.max_queries_org_daily == 2000


class TestOrganizationInviteModel:
    """Tests for OrganizationInvite model."""

    @pytest.mark.asyncio
    async def test_create_invite(self, db_session: AsyncSession, test_organization: Organization, test_user: User):
        """Test creating an organization invite."""
        invite = OrganizationInvite(
            organization_id=test_organization.id,
            created_by_user_id=test_user.id
        )
        db_session.add(invite)
        await db_session.commit()
        await db_session.refresh(invite)

        # Check defaults
        assert invite.id is not None
        assert isinstance(invite.code, uuid.UUID)
        assert invite.organization_id == test_organization.id
        assert invite.created_by_user_id == test_user.id
        assert invite.max_uses is None  # unlimited by default in model
        assert invite.used_count == 0
        assert invite.expires_at is None
        assert invite.default_role == "member"
        assert invite.status == InviteStatus.ACTIVE
        assert invite.created_at is not None

    @pytest.mark.asyncio
    async def test_invite_unique_code(self, db_session: AsyncSession, test_organization: Organization, test_user: User):
        """Test that invite codes are unique."""
        invite1 = OrganizationInvite(
            organization_id=test_organization.id,
            created_by_user_id=test_user.id
        )
        db_session.add(invite1)
        await db_session.commit()
        await db_session.refresh(invite1)

        invite2 = OrganizationInvite(
            organization_id=test_organization.id,
            created_by_user_id=test_user.id
        )
        db_session.add(invite2)
        await db_session.commit()
        await db_session.refresh(invite2)

        # Codes should be different
        assert invite1.code != invite2.code

    @pytest.mark.asyncio
    async def test_invite_validation(self, db_session: AsyncSession, test_organization: Organization, test_user: User):
        """Test invite validation logic."""
        invite = OrganizationInvite(
            organization_id=test_organization.id,
            created_by_user_id=test_user.id,
            max_uses=3
        )
        db_session.add(invite)
        await db_session.commit()
        await db_session.refresh(invite)

        # Simulate using the invite
        invite.used_count = 1
        await db_session.commit()
        assert invite.used_count == 1

        invite.used_count = 2
        await db_session.commit()
        assert invite.used_count == 2

        # Should be able to set to max_uses
        invite.used_count = 3
        await db_session.commit()
        assert invite.used_count == 3

        # In a real app, you would check this in application logic
        # The database won't enforce this constraint automatically
        assert invite.used_count <= invite.max_uses

    @pytest.mark.asyncio
    async def test_invite_expiration(self, db_session: AsyncSession, test_organization: Organization, test_user: User):
        """Test invite expiration."""
        expires_at = datetime.utcnow() + timedelta(days=7)
        invite = OrganizationInvite(
            organization_id=test_organization.id,
            created_by_user_id=test_user.id,
            expires_at=expires_at,
            max_uses=10
        )
        db_session.add(invite)
        await db_session.commit()
        await db_session.refresh(invite)

        assert invite.expires_at == expires_at
        assert invite.expires_at > datetime.utcnow()

    @pytest.mark.asyncio
    async def test_invite_status_changes(self, db_session: AsyncSession, test_organization: Organization, test_user: User):
        """Test changing invite status."""
        invite = OrganizationInvite(
            organization_id=test_organization.id,
            created_by_user_id=test_user.id
        )
        db_session.add(invite)
        await db_session.commit()
        await db_session.refresh(invite)

        assert invite.status == InviteStatus.ACTIVE

        # Revoke invite
        invite.status = InviteStatus.REVOKED
        await db_session.commit()
        await db_session.refresh(invite)

        assert invite.status == InviteStatus.REVOKED

        # Mark as expired
        invite.status = InviteStatus.EXPIRED
        await db_session.commit()
        await db_session.refresh(invite)

        assert invite.status == InviteStatus.EXPIRED

    @pytest.mark.asyncio
    async def test_invite_relationships(self, db_session: AsyncSession, test_organization: Organization, test_user: User):
        """Test invite relationships."""
        invite = OrganizationInvite(
            organization_id=test_organization.id,
            created_by_user_id=test_user.id
        )
        db_session.add(invite)
        await db_session.commit()
        await db_session.refresh(invite, ["organization", "created_by"])

        assert invite.organization is not None
        assert invite.organization.id == test_organization.id
        assert invite.created_by is not None
        assert invite.created_by.id == test_user.id


class TestOrganizationMemberModel:
    """Tests for OrganizationMember model."""

    @pytest.mark.asyncio
    async def test_organization_member_history(self, db_session: AsyncSession, test_organization: Organization, test_user: User):
        """Test creating organization member history record."""
        member = OrganizationMember(
            organization_id=test_organization.id,
            user_id=test_user.id,
            role="admin"
        )
        db_session.add(member)
        await db_session.commit()
        await db_session.refresh(member)

        assert member.id is not None
        assert member.organization_id == test_organization.id
        assert member.user_id == test_user.id
        assert member.role == "admin"
        assert member.joined_at is not None
        assert member.left_at is None
        assert member.invited_by_user_id is None

    @pytest.mark.asyncio
    async def test_member_with_inviter(self, db_session: AsyncSession, test_organization: Organization):
        """Test member record with inviter information."""
        # Create inviter
        inviter = User(
            email="inviter@example.com",
            password_hash="hashed",
            status=UserStatus.APPROVED,
            role=UserRole.USER
        )
        db_session.add(inviter)
        await db_session.commit()
        await db_session.refresh(inviter)

        # Create invited user
        invited_user = User(
            email="invited@example.com",
            password_hash="hashed",
            status=UserStatus.APPROVED,
            role=UserRole.USER
        )
        db_session.add(invited_user)
        await db_session.commit()
        await db_session.refresh(invited_user)

        # Create member record
        member = OrganizationMember(
            organization_id=test_organization.id,
            user_id=invited_user.id,
            role="member",
            invited_by_user_id=inviter.id
        )
        db_session.add(member)
        await db_session.commit()
        await db_session.refresh(member, ["invited_by"])

        assert member.invited_by_user_id == inviter.id
        assert member.invited_by is not None
        assert member.invited_by.email == "inviter@example.com"

    @pytest.mark.asyncio
    async def test_member_leave_organization(self, db_session: AsyncSession, test_organization: Organization, test_user: User):
        """Test marking a member as left."""
        member = OrganizationMember(
            organization_id=test_organization.id,
            user_id=test_user.id,
            role="member"
        )
        db_session.add(member)
        await db_session.commit()
        await db_session.refresh(member)

        assert member.left_at is None

        # Member leaves
        left_time = datetime.utcnow()
        member.left_at = left_time
        await db_session.commit()
        await db_session.refresh(member)

        assert member.left_at is not None
        assert member.left_at >= member.joined_at

    @pytest.mark.asyncio
    async def test_member_role_types(self, db_session: AsyncSession, test_organization: Organization):
        """Test different member roles."""
        roles = ["owner", "admin", "member", "viewer"]

        for idx, role in enumerate(roles):
            user = User(
                email=f"user{idx}@example.com",
                password_hash="hashed",
                status=UserStatus.APPROVED,
                role=UserRole.USER
            )
            db_session.add(user)
            await db_session.commit()
            await db_session.refresh(user)

            member = OrganizationMember(
                organization_id=test_organization.id,
                user_id=user.id,
                role=role
            )
            db_session.add(member)
            await db_session.commit()
            await db_session.refresh(member)

            assert member.role == role


class TestOrganizationSettingsModel:
    """Tests for OrganizationSettings model."""

    @pytest.mark.asyncio
    async def test_organization_settings_defaults(self, db_session: AsyncSession, test_organization: Organization):
        """Test organization settings with default values."""
        settings = OrganizationSettings(
            organization_id=test_organization.id
        )
        db_session.add(settings)
        await db_session.commit()
        await db_session.refresh(settings)

        # Check defaults
        assert settings.organization_id == test_organization.id
        assert settings.custom_system_prompt is None
        assert settings.custom_temperature is None
        assert settings.custom_max_tokens is None
        assert settings.custom_model is None
        assert settings.primary_language is None
        assert settings.secondary_languages is None
        assert settings.require_bilingual_response is False
        assert settings.custom_terminology is None
        assert settings.citation_format is None
        assert settings.citation_template is None
        assert settings.chunk_size is None
        assert settings.chunk_overlap is None
        assert settings.content_filters is None
        assert settings.pre_prompt_instructions is None
        assert settings.post_prompt_instructions is None
        assert settings.response_format is None
        assert settings.include_sources_inline is True
        assert settings.show_confidence_score is False
        assert settings.created_at is not None
        assert settings.updated_at is not None  # Has default value

    @pytest.mark.asyncio
    async def test_settings_llm_configuration(self, db_session: AsyncSession, test_organization: Organization):
        """Test LLM configuration settings."""
        settings = OrganizationSettings(
            organization_id=test_organization.id,
            custom_system_prompt="You are a helpful assistant.",
            custom_temperature=0.7,
            custom_max_tokens=2000,
            custom_model="gpt-4"
        )
        db_session.add(settings)
        await db_session.commit()
        await db_session.refresh(settings)

        assert settings.custom_system_prompt == "You are a helpful assistant."
        assert settings.custom_temperature == 0.7
        assert settings.custom_max_tokens == 2000
        assert settings.custom_model == "gpt-4"

    @pytest.mark.asyncio
    async def test_settings_jsonb_fields(self, db_session: AsyncSession, test_organization: Organization):
        """Test JSONB fields for complex data."""
        custom_terminology = {
            "продукт": "изделие",
            "клиент": "заказчик"
        }
        content_filters = {
            "blocked_words": ["spam", "bad"],
            "min_confidence": 0.8
        }
        secondary_languages = {
            "languages": ["en", "kk"],
            "fallback": "en"
        }

        settings = OrganizationSettings(
            organization_id=test_organization.id,
            custom_terminology=custom_terminology,
            content_filters=content_filters,
            secondary_languages=secondary_languages
        )
        db_session.add(settings)
        await db_session.commit()
        await db_session.refresh(settings)

        assert settings.custom_terminology == custom_terminology
        assert settings.custom_terminology["продукт"] == "изделие"
        assert settings.content_filters == content_filters
        assert settings.content_filters["min_confidence"] == 0.8
        assert settings.secondary_languages == secondary_languages
        assert "en" in settings.secondary_languages["languages"]

    @pytest.mark.asyncio
    async def test_settings_document_processing(self, db_session: AsyncSession, test_organization: Organization):
        """Test document processing settings."""
        settings = OrganizationSettings(
            organization_id=test_organization.id,
            chunk_size=512,
            chunk_overlap=50
        )
        db_session.add(settings)
        await db_session.commit()
        await db_session.refresh(settings)

        assert settings.chunk_size == 512
        assert settings.chunk_overlap == 50

    @pytest.mark.asyncio
    async def test_settings_language_configuration(self, db_session: AsyncSession, test_organization: Organization):
        """Test language configuration."""
        settings = OrganizationSettings(
            organization_id=test_organization.id,
            primary_language="ru",
            require_bilingual_response=True
        )
        db_session.add(settings)
        await db_session.commit()
        await db_session.refresh(settings)

        assert settings.primary_language == "ru"
        assert settings.require_bilingual_response is True

    @pytest.mark.asyncio
    async def test_settings_citation_configuration(self, db_session: AsyncSession, test_organization: Organization):
        """Test citation configuration."""
        citation_template = "[{source}] ({confidence})"

        settings = OrganizationSettings(
            organization_id=test_organization.id,
            citation_format="inline",
            citation_template=citation_template,
            include_sources_inline=True,
            show_confidence_score=True
        )
        db_session.add(settings)
        await db_session.commit()
        await db_session.refresh(settings)

        assert settings.citation_format == "inline"
        assert settings.citation_template == citation_template
        assert settings.include_sources_inline is True
        assert settings.show_confidence_score is True

    @pytest.mark.asyncio
    async def test_settings_relationship(self, db_session: AsyncSession, test_organization: Organization):
        """Test settings relationship with organization."""
        settings = OrganizationSettings(
            organization_id=test_organization.id
        )
        db_session.add(settings)
        await db_session.commit()
        await db_session.refresh(settings, ["organization"])

        assert settings.organization is not None
        assert settings.organization.id == test_organization.id

        # Test from organization side
        await db_session.refresh(test_organization, ["settings"])
        assert test_organization.settings is not None
        assert test_organization.settings.organization_id == test_organization.id


class TestUserOrganizationFields:
    """Tests for new organization fields in User model."""

    @pytest.mark.asyncio
    async def test_user_organization_fields(self, db_session: AsyncSession, test_organization: Organization):
        """Test user organization-related fields."""
        user = User(
            email="orguser@example.com",
            password_hash="hashed",
            status=UserStatus.APPROVED,
            role=UserRole.USER,
            organization_id=test_organization.id,
            role_in_org="admin",
            is_platform_admin=False
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        assert user.organization_id == test_organization.id
        assert user.role_in_org == "admin"
        assert user.is_platform_admin is False

    @pytest.mark.asyncio
    async def test_user_platform_admin(self, db_session: AsyncSession):
        """Test platform admin user."""
        admin = User(
            email="admin@example.com",
            password_hash="hashed",
            status=UserStatus.APPROVED,
            role=UserRole.ADMIN,
            is_platform_admin=True
        )
        db_session.add(admin)
        await db_session.commit()
        await db_session.refresh(admin)

        assert admin.is_platform_admin is True
        assert admin.organization_id is None
        assert admin.role_in_org is None

    @pytest.mark.asyncio
    async def test_user_without_organization(self, db_session: AsyncSession):
        """Test user without organization."""
        user = User(
            email="solo@example.com",
            password_hash="hashed",
            status=UserStatus.APPROVED,
            role=UserRole.USER
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        assert user.organization_id is None
        assert user.role_in_org is None
        assert user.is_platform_admin is False


class TestDocumentVisibility:
    """Tests for document visibility and organization features."""

    @pytest.mark.asyncio
    async def test_document_visibility(self, db_session: AsyncSession, test_organization: Organization, test_user: User):
        """Test document visibility field."""
        doc = Document(
            uploaded_by_user_id=test_user.id,
            organization_id=test_organization.id,
            filename="test.pdf",
            visibility="organization"
        )
        db_session.add(doc)
        await db_session.commit()
        await db_session.refresh(doc)

        assert doc.visibility == "organization"
        assert doc.organization_id == test_organization.id
        assert doc.uploaded_by_user_id == test_user.id

    @pytest.mark.asyncio
    async def test_document_private_visibility(self, db_session: AsyncSession, test_user: User):
        """Test private document without organization."""
        doc = Document(
            uploaded_by_user_id=test_user.id,
            filename="private.pdf",
            visibility="private"
        )
        db_session.add(doc)
        await db_session.commit()
        await db_session.refresh(doc)

        assert doc.visibility == "private"
        assert doc.organization_id is None
        assert doc.uploaded_by_user_id == test_user.id

    @pytest.mark.asyncio
    async def test_document_organization_relationship(self, db_session: AsyncSession, test_organization: Organization, test_user: User):
        """Test document relationships with organization and user."""
        doc = Document(
            uploaded_by_user_id=test_user.id,
            organization_id=test_organization.id,
            filename="org-doc.pdf",
            status=DocumentStatus.INDEXED
        )
        db_session.add(doc)
        await db_session.commit()
        await db_session.refresh(doc, ["uploaded_by_user", "organization"])

        assert doc.uploaded_by_user is not None
        assert doc.uploaded_by_user.id == test_user.id
        assert doc.organization is not None
        assert doc.organization.id == test_organization.id

    @pytest.mark.asyncio
    async def test_document_default_visibility(self, db_session: AsyncSession, test_user: User):
        """Test document default visibility is private."""
        doc = Document(
            uploaded_by_user_id=test_user.id,
            filename="default.pdf"
        )
        db_session.add(doc)
        await db_session.commit()
        await db_session.refresh(doc)

        assert doc.visibility == "private"


class TestCascadeDeletes:
    """Tests for cascade delete behavior."""

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="SQLite doesn't fully support CASCADE deletes - test in PostgreSQL")
    async def test_organization_delete_cascades(self, db_session: AsyncSession, test_organization: Organization, test_user: User):
        """Test that deleting organization cascades to related records."""
        # Create settings
        settings = OrganizationSettings(
            organization_id=test_organization.id
        )
        db_session.add(settings)

        # Create invite
        invite = OrganizationInvite(
            organization_id=test_organization.id,
            created_by_user_id=test_user.id
        )
        db_session.add(invite)

        # Create member
        member = OrganizationMember(
            organization_id=test_organization.id,
            user_id=test_user.id,
            role="admin"
        )
        db_session.add(member)

        await db_session.commit()

        settings_id = settings.organization_id
        invite_id = invite.id
        member_id = member.id

        # Delete organization
        await db_session.delete(test_organization)
        await db_session.commit()

        # Verify cascade deletes
        from sqlalchemy import select

        # Settings should be deleted
        result = await db_session.execute(
            select(OrganizationSettings).where(OrganizationSettings.organization_id == settings_id)
        )
        assert result.scalar_one_or_none() is None

        # Invite should be deleted
        result = await db_session.execute(
            select(OrganizationInvite).where(OrganizationInvite.id == invite_id)
        )
        assert result.scalar_one_or_none() is None

        # Member should be deleted
        result = await db_session.execute(
            select(OrganizationMember).where(OrganizationMember.id == member_id)
        )
        assert result.scalar_one_or_none() is None
