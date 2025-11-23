"""add organizations table

Revision ID: 91c13f3883e5
Revises: 363736a35ffa
Create Date: 2025-11-22 10:45:13.775481

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '91c13f3883e5'
down_revision: Union[str, None] = '363736a35ffa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create organizations table
    op.create_table(
        'organizations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('slug', sa.String(length=100), nullable=False),
        sa.Column('owner_id', sa.Integer(), nullable=True),

        # Quotas
        sa.Column('max_members', sa.Integer(), nullable=False, server_default='10'),
        sa.Column('max_documents', sa.Integer(), nullable=False, server_default='50'),
        sa.Column('max_storage_mb', sa.Integer(), nullable=False, server_default='1000'),
        sa.Column('max_queries_per_user_daily', sa.Integer(), nullable=False, server_default='100'),
        sa.Column('max_queries_org_daily', sa.Integer(), nullable=False, server_default='1000'),

        # Status
        sa.Column('status', sa.String(length=20), nullable=False, server_default='active'),

        # Timestamps
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),

        # Constraints
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ondelete='SET NULL'),
        sa.UniqueConstraint('slug')
    )

    # Create indexes
    op.create_index('ix_organizations_slug', 'organizations', ['slug'])
    op.create_index('ix_organizations_owner_id', 'organizations', ['owner_id'])
    op.create_index('ix_organizations_status', 'organizations', ['status'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_organizations_status', table_name='organizations')
    op.drop_index('ix_organizations_owner_id', table_name='organizations')
    op.drop_index('ix_organizations_slug', table_name='organizations')

    # Drop table
    op.drop_table('organizations')
