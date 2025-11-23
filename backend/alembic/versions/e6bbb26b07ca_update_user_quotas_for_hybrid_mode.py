"""update user quotas for hybrid mode

Revision ID: e6bbb26b07ca
Revises: 900cfaaec3b1
Create Date: 2025-11-22 10:46:12.446196

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e6bbb26b07ca'
down_revision: Union[str, None] = '900cfaaec3b1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new columns for personal quotas
    op.add_column('user_quotas', sa.Column('personal_max_documents', sa.Integer(), nullable=True, server_default='5'))
    op.add_column('user_quotas', sa.Column('personal_current_documents', sa.Integer(), nullable=True, server_default='0'))
    op.add_column('user_quotas', sa.Column('personal_max_queries_daily', sa.Integer(), nullable=True, server_default='50'))


def downgrade() -> None:
    # Drop columns in reverse order
    op.drop_column('user_quotas', 'personal_max_queries_daily')
    op.drop_column('user_quotas', 'personal_current_documents')
    op.drop_column('user_quotas', 'personal_max_documents')
