"""Organization settings service."""
from typing import Any, Dict, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.organization_settings import OrganizationSettings

# Mapping frontend field names to model field names
FIELD_MAPPING = {
    "response_language": "primary_language",
}


class SettingsService:
    """Service for managing organization settings."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_org_id(self, organization_id: int) -> OrganizationSettings | None:
        """Get settings for an organization."""
        result = await self.db.execute(
            select(OrganizationSettings).where(
                OrganizationSettings.organization_id == organization_id
            )
        )
        return result.scalar_one_or_none()

    async def get_or_create(self, organization_id: int) -> OrganizationSettings:
        """Get or create default settings for an organization."""
        settings = await self.get_by_org_id(organization_id)

        if not settings:
            settings = OrganizationSettings(organization_id=organization_id)
            self.db.add(settings)
            await self.db.flush()

        return settings

    async def update(
        self,
        organization_id: int,
        updates: dict[str, Any],
        updated_by_user_id: int,
    ) -> OrganizationSettings:
        """Update organization settings."""
        settings = await self.get_or_create(organization_id)

        for field, value in updates.items():
            # Map frontend field names to model field names
            model_field = FIELD_MAPPING.get(field, field)
            if hasattr(settings, model_field):
                setattr(settings, model_field, value)

        settings.updated_by_user_id = updated_by_user_id
        return settings

    async def get_custom_model(self, organization_id: int) -> str | None:
        """Get custom model setting if enabled."""
        settings = await self.get_by_org_id(organization_id)

        if settings and settings.custom_model:
            return settings.custom_model

        return None
