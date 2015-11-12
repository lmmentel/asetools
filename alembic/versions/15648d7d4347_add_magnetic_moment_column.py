"""add magnetic_moment column

Revision ID: 15648d7d4347
Revises: 51938c0be2f8
Create Date: 2015-11-12 10:54:14.173072

"""

# revision identifiers, used by Alembic.
revision = '15648d7d4347'
down_revision = '51938c0be2f8'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():

    op.add_column('systems', sa.Column('magnetic_moment', sa.Float))

def downgrade():

    op.drop_column('systems', 'magnetic_moment')
