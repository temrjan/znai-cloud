"""add organization invites table

Revision ID: 8dccaa9dc041
Revises: 91c13f3883e5
Create Date: 2025-11-22 10:46:01.022668

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '8dccaa9dc041'
down_revision: Union[str, None] = '91c13f3883e5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'organization_invites',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('created_by_user_id', sa.Integer(), nullable=True),
        sa.Column('max_uses', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('used_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('default_role', sa.String(length=20), nullable=False, server_default='member'),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='active'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.CheckConstraint('max_uses > 0', name='check_max_uses_positive'),
        sa.CheckConstraint('used_count >= 0 AND used_count <= max_uses', name='check_used_count_valid'),
        sa.ForeignKeyConstraint(['created_by_user_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )

    op.create_index('ix_organization_invites_code', 'organization_invites', ['code'])
    op.create_index('ix_organization_invites_organization_id', 'organization_invites', ['organization_id'])
    op.create_index('ix_organization_invites_status', 'organization_invites', ['status'])


def downgrade() -> None:
    op.drop_index('ix_organization_invites_status', table_name='organization_invites')
    op.drop_index('ix_organization_invites_organization_id', table_name='organization_invites')
    op.drop_index('ix_organization_invites_code', table_name='organization_invites')
    op.drop_table('organization_invites')
