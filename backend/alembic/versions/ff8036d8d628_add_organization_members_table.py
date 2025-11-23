"""add organization members table

Revision ID: ff8036d8d628
Revises: 8dccaa9dc041
Create Date: 2025-11-22 10:46:09.875257

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ff8036d8d628'
down_revision: Union[str, None] = '8dccaa9dc041'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'organization_members',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('joined_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('left_at', sa.DateTime(), nullable=True),
        sa.Column('invited_by_user_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['invited_by_user_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('organization_id', 'user_id', 'joined_at', name='uq_org_user_joined')
    )


def downgrade() -> None:
    op.drop_table('organization_members')
