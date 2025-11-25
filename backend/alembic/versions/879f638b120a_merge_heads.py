"""merge_heads

Revision ID: 879f638b120a
Revises: a1b2c3d4e5f6, fb509831036b
Create Date: 2025-11-25 11:48:37.941849

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '879f638b120a'
down_revision: Union[str, None] = ('a1b2c3d4e5f6', 'fb509831036b')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
