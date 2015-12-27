"""add enthalpy columns to systems

Revision ID: 2d27a231857d
Revises: 1e8cdcbd84c5
Create Date: 2015-12-01 14:22:01.585755

"""

# revision identifiers, used by Alembic.
revision = '2d27a231857d'
down_revision = '1e8cdcbd84c5'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():

    op.add_column('systems', sa.Column('enthalpy', sa.Float))

def downgrade():

    op.drop_column('systems', 'enthalpy')
