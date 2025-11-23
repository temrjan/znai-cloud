"""add organization settings table

Revision ID: 59b38f935a43
Revises: ff8036d8d628
Create Date: 2025-11-22 10:46:10.576016

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '59b38f935a43'
down_revision: Union[str, None] = 'ff8036d8d628'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'organization_settings',
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('custom_system_prompt', sa.Text(), nullable=True),
        sa.Column('custom_temperature', sa.Numeric(precision=3, scale=2), nullable=True, server_default='0.7'),
        sa.Column('custom_max_tokens', sa.Integer(), nullable=True, server_default='2500'),
        sa.Column('custom_model', sa.String(length=50), nullable=True, server_default='gpt-4o'),
        sa.Column('primary_language', sa.String(length=10), nullable=True, server_default='ru'),
        sa.Column('secondary_languages', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='[]'),
        sa.Column('require_bilingual_response', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('custom_terminology', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='{}'),
        sa.Column('citation_format', sa.String(length=50), nullable=True, server_default='inline'),
        sa.Column('citation_template', sa.Text(), nullable=True),
        sa.Column('chunk_size', sa.Integer(), nullable=True, server_default='512'),
        sa.Column('chunk_overlap', sa.Integer(), nullable=True, server_default='50'),
        sa.Column('content_filters', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='{}'),
        sa.Column('pre_prompt_instructions', sa.Text(), nullable=True),
        sa.Column('post_prompt_instructions', sa.Text(), nullable=True),
        sa.Column('response_format', sa.String(length=20), nullable=True, server_default='markdown'),
        sa.Column('include_sources_inline', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('show_confidence_score', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_by_user_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['updated_by_user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('organization_id')
    )


def downgrade() -> None:
    op.drop_table('organization_settings')
