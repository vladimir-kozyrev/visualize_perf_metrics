"""create confluence table

Revision ID: 5d7b783ce39d
Revises: 1a61b2ec3d99
Create Date: 2020-07-04 22:04:45.924385

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5d7b783ce39d'
down_revision = '1a61b2ec3d99'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'confluence',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('person', sa.String(50)),
        sa.Column('contributions', sa.Integer),
    )

def downgrade():
    op.drop_table('confluence')
