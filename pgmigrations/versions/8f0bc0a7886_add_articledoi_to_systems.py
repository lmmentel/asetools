"""add articledoi to systems

Revision ID: 8f0bc0a7886
Revises: 59a3c754a95a
Create Date: 2015-11-26 19:08:03.544727

"""

# revision identifiers, used by Alembic.
revision = '8f0bc0a7886'
down_revision = '59a3c754a95a'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():

    op.add_column('systems', sa.Column('articledoi', sa.String))

def downgrade():

    op.drop_column('systems', 'articledoi')
