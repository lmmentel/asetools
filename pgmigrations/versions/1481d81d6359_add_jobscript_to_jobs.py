"""add jobscript to Jobs

Revision ID: 1481d81d6359
Revises: 8f0bc0a7886
Create Date: 2015-11-26 19:53:29.308821

"""

# revision identifiers, used by Alembic.
revision = '1481d81d6359'
down_revision = '8f0bc0a7886'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():

    op.add_column('jobs', sa.Column('jobscript', sa.String))

def downgrade():

    op.drop_column('jobs', 'jobscript')
