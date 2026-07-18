"""add missing roles

Revision ID: a1b2c3d4
Revises: e10af902d923
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'a1b2c3d4'
down_revision: Union[str, None] = 'e10af902d923'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # 1. Create the roles table
    op.create_table('roles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    
    # 2. Add role_id to users (nullable=True temporarily so existing rows don't crash)
    op.add_column('users', sa.Column('role_id', sa.Integer(), nullable=True))
    op.create_foreign_key('users_role_id_fkey', 'users', 'roles', ['role_id'], ['id'])
    
    # 3. Insert the default roles
    op.execute("INSERT INTO roles (id, name) VALUES (1, 'employee'), (2, 'manager'), (3, 'admin') ON CONFLICT DO NOTHING")
    
    # 4. Assign the 'employee' role to any users that currently don't have one
    op.execute("UPDATE users SET role_id = 1 WHERE role_id IS NULL")

def downgrade() -> None:
    op.drop_constraint('users_role_id_fkey', 'users', type_='foreignkey')
    op.drop_column('users', 'role_id')
    op.drop_table('roles')