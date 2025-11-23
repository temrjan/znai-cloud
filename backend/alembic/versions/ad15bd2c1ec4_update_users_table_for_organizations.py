"""update users table for organizations

Revision ID: ad15bd2c1ec4
Revises: 59b38f935a43
Create Date: 2025-11-22 10:46:11.169204

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ad15bd2c1ec4'
down_revision: Union[str, None] = '59b38f935a43'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new columns to users table
    op.add_column('users', sa.Column('organization_id', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('role_in_org', sa.String(length=20), nullable=True))
    op.add_column('users', sa.Column('is_platform_admin', sa.Boolean(), nullable=True, server_default='false'))

    # Create foreign key constraint
    op.create_foreign_key(
        'fk_users_organization_id',
        'users',
        'organizations',
        ['organization_id'],
        ['id'],
        ondelete='SET NULL'
    )

    # Create index
    op.create_index('ix_users_organization_id', 'users', ['organization_id'])


def downgrade() -> None:
    # Drop index
    op.drop_index('ix_users_organization_id', table_name='users')

    # Drop foreign key constraint
    op.drop_constraint('fk_users_organization_id', 'users', type_='foreignkey')

    # Drop columns in reverse order
    op.drop_column('users', 'is_platform_admin')
    op.drop_column('users', 'role_in_org')
    op.drop_column('users', 'organization_id')
