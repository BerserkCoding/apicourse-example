"""add foreign key to posts table

Revision ID: 43c8089f28e0
Revises: 6439a3c58abe
Create Date: 2022-05-05 13:16:12.467407

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '43c8089f28e0'
down_revision = '6439a3c58abe'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('posts', sa.Column('owner_id', sa.Integer(), nullable=False))
    op.create_foreign_key('post_users_fk', source_table="posts", referent_table="users", local_cols=[
                          'owner_id'], remote_cols=['id'], ondelete="CASCADE")
    pass


def downgrade():
    op.drop_constraint('post_users_fk', table_name="posts")
    op.drop_column('posts', 'owner_id')
    pass
