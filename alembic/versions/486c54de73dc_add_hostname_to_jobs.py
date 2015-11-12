"""add hostname to jobs

Revision ID: 486c54de73dc
Revises: 1a3f44b41cb1
Create Date: 2015-11-12 14:52:11.264761

"""

# revision identifiers, used by Alembic.
revision = '486c54de73dc'
down_revision = '1a3f44b41cb1'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():

    op.add_column('jobs', sa.Column('hostname', sa.String))

def downgrade():

    op.drop_column('jobs', 'hostname')
