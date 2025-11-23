"""update query logs for organizations

Revision ID: fb509831036b
Revises: e6bbb26b07ca
Create Date: 2025-11-22 10:46:13.021273

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fb509831036b'
down_revision: Union[str, None] = 'e6bbb26b07ca'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new columns
    op.add_column('query_logs', sa.Column('organization_id', sa.Integer(), nullable=True))
    op.add_column('query_logs', sa.Column('search_mode', sa.String(length=20), nullable=True, server_default='all'))

    # Create foreign key for organization_id
    op.create_foreign_key(
        'fk_query_logs_organization_id',
        'query_logs',
        'organizations',
        ['organization_id'],
        ['id'],
        ondelete='SET NULL'
    )

    # Create composite index on organization_id and created_at
    op.create_index('ix_query_logs_organization_id', 'query_logs', ['organization_id', 'created_at'])


def downgrade() -> None:
    # Drop index
    op.drop_index('ix_query_logs_organization_id', table_name='query_logs')

    # Drop foreign key
    op.drop_constraint('fk_query_logs_organization_id', 'query_logs', type_='foreignkey')

    # Drop columns
    op.drop_column('query_logs', 'search_mode')
    op.drop_column('query_logs', 'organization_id')
