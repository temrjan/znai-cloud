"""update documents table for organizations

Revision ID: 900cfaaec3b1
Revises: ad15bd2c1ec4
Create Date: 2025-11-22 10:46:11.838074

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '900cfaaec3b1'
down_revision: Union[str, None] = 'ad15bd2c1ec4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Rename user_id to uploaded_by_user_id
    op.alter_column('documents', 'user_id', new_column_name='uploaded_by_user_id')

    # Add new columns
    op.add_column('documents', sa.Column('organization_id', sa.Integer(), nullable=True))
    op.add_column('documents', sa.Column('visibility', sa.String(length=20), nullable=False, server_default='private'))

    # Create foreign key for organization_id
    op.create_foreign_key(
        'fk_documents_organization_id',
        'documents',
        'organizations',
        ['organization_id'],
        ['id'],
        ondelete='CASCADE'
    )

    # Add check constraint for ownership
    op.create_check_constraint(
        'check_ownership',
        'documents',
        '(organization_id IS NOT NULL AND visibility = \'organization\') OR (organization_id IS NULL AND visibility = \'private\' AND uploaded_by_user_id IS NOT NULL)'
    )

    # Create indexes
    op.create_index('ix_documents_organization_id', 'documents', ['organization_id', 'visibility'])
    op.create_index('ix_documents_uploaded_by', 'documents', ['uploaded_by_user_id'])

    # Drop old unique constraint if it exists (try-catch approach for safety)
    try:
        op.drop_constraint('unique_user_file_hash', 'documents', type_='unique')
    except:
        pass

    # Create partial unique indexes
    op.execute(
        'CREATE UNIQUE INDEX unique_org_file_hash ON documents(organization_id, file_hash) WHERE organization_id IS NOT NULL'
    )
    op.execute(
        'CREATE UNIQUE INDEX unique_user_file_hash ON documents(uploaded_by_user_id, file_hash) WHERE visibility = \'private\''
    )


def downgrade() -> None:
    # Drop partial unique indexes
    op.drop_index('unique_user_file_hash', table_name='documents')
    op.drop_index('unique_org_file_hash', table_name='documents')

    # Recreate old unique constraint
    op.create_unique_constraint('unique_user_file_hash', 'documents', ['uploaded_by_user_id', 'file_hash'])

    # Drop regular indexes
    op.drop_index('ix_documents_uploaded_by', table_name='documents')
    op.drop_index('ix_documents_organization_id', table_name='documents')

    # Drop check constraint
    op.drop_constraint('check_ownership', 'documents', type_='check')

    # Drop foreign key
    op.drop_constraint('fk_documents_organization_id', 'documents', type_='foreignkey')

    # Drop columns
    op.drop_column('documents', 'visibility')
    op.drop_column('documents', 'organization_id')

    # Rename uploaded_by_user_id back to user_id
    op.alter_column('documents', 'uploaded_by_user_id', new_column_name='user_id')
