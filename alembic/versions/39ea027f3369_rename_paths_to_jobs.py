"""rename paths to jobs

Revision ID: 39ea027f3369
Revises: 15648d7d4347
Create Date: 2015-11-12 11:24:36.920040

"""

# revision identifiers, used by Alembic.
revision = '39ea027f3369'
down_revision = '15648d7d4347'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():

    op.rename_table('paths', 'jobs')


def downgrade():

    op.rename_table('jobs', 'paths')
