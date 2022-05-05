"""add users table


Revision ID: 6439a3c58abe
Revises: f100d29bf588
Create Date: 2022-05-05 13:12:54.604501

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6439a3c58abe'
down_revision = 'f100d29bf588'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('users',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('email', sa.String(), nullable=False),
                    sa.Column('password', sa.String(), nullable=False),
                    sa.Column('created_at', sa.TIMESTAMP(timezone=True),
                              server_default=sa.text('now()'), nullable=False),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('email')
                    )
    pass


def downgrade():
    op.drop_table('users')
    pass
