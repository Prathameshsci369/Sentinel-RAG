"""add tenants departments and doc visibility

Revision ID: e10af902d923
Revises: 06a108864d03
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e10af902d923'
down_revision: Union[str, None] = '06a108864d03'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create new tables
    op.create_table('tenants',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    
    op.create_table('departments',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('tenant_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_departments_tenant_id'), 'departments', ['tenant_id'], unique=False)

    # 2. FIX: Explicitly create the Enum type FIRST
    document_visibility_enum = sa.Enum('general', 'management', 'confidential', name='document_visibility')
    document_visibility_enum.create(op.get_bind(), checkfirst=True)

    # 3. Add columns to users
    op.add_column('users', sa.Column('tenant_id', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('department_id', sa.Integer(), nullable=True))
    op.create_foreign_key('users_tenant_id_fkey', 'users', 'tenants', ['tenant_id'], ['id'])
    op.create_foreign_key('users_department_id_fkey', 'users', 'departments', ['department_id'], ['id'])

    # 4. NOW add the column to documents using the type we just created
    op.add_column('documents', sa.Column('tenant_id', sa.Integer(), nullable=True))
    op.add_column('documents', sa.Column('department_id', sa.Integer(), nullable=True))
    op.add_column('documents', sa.Column('visibility', document_visibility_enum, nullable=True))
    op.create_foreign_key('documents_tenant_id_fkey', 'documents', 'tenants', ['tenant_id'], ['id'])
    op.create_foreign_key('documents_department_id_fkey', 'documents', 'departments', ['department_id'], ['id'])


def downgrade() -> None:
    # 1. Drop columns from documents
    op.drop_constraint('documents_department_id_fkey', 'documents', type_='foreignkey')
    op.drop_constraint('documents_tenant_id_fkey', 'documents', type_='foreignkey')
    op.drop_column('documents', 'visibility')
    op.drop_column('documents', 'department_id')
    op.drop_column('documents', 'tenant_id')

    # 2. Drop columns from users
    op.drop_constraint('users_department_id_fkey', 'users', type_='foreignkey')
    op.drop_constraint('users_tenant_id_fkey', 'users', type_='foreignkey')
    op.drop_column('users', 'department_id')
    op.drop_column('users', 'tenant_id')

    # 3. Drop tables
    op.drop_index(op.f('ix_departments_tenant_id'), table_name='departments')
    op.drop_table('departments')
    op.drop_table('tenants')

    # 4. Drop the Enum type last
    sa.Enum(name='document_visibility').drop(op.get_bind(), checkfirst=True)