"""Add telegram bot settings to organization_settings.

Revision ID: b1c2d3e4f5g6
Revises: a1b2c3d4e5f6
Create Date: 2025-12-06

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = 'b1c2d3e4f5g6'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('organization_settings',
        sa.Column('telegram_bot_token', sa.String(100), nullable=True))
    op.add_column('organization_settings',
        sa.Column('telegram_bot_enabled', sa.Boolean(), nullable=True, server_default='false'))
    op.add_column('organization_settings',
        sa.Column('telegram_bot_username', sa.String(100), nullable=True))
    op.add_column('organization_settings',
        sa.Column('telegram_webhook_secret', sa.String(64), nullable=True))


def downgrade() -> None:
    op.drop_column('organization_settings', 'telegram_webhook_secret')
    op.drop_column('organization_settings', 'telegram_bot_username')
    op.drop_column('organization_settings', 'telegram_bot_enabled')
    op.drop_column('organization_settings', 'telegram_bot_token')
