"""create pull_requests table

Revision ID: 1a61b2ec3d99
Revises:
Create Date: 2020-06-28 14:04:45.026959

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1a61b2ec3d99'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'pull_requests',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('created_at', sa.String(50)),
        sa.Column('merged_at', sa.String(50)),
        sa.Column('login', sa.String(50)),
    )

def downgrade():
    op.drop_table('pull_requests')
