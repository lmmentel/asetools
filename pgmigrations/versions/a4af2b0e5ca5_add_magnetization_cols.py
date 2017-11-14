"""add magnetization cols

Revision ID: a4af2b0e5ca5
Revises: 2d27a231857d
Create Date: 2017-11-14 13:27:35.639724

"""

# revision identifiers, used by Alembic.
revision = 'a4af2b0e5ca5'
down_revision = '2d27a231857d'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():

    op.add_column('systems', sa.Column('absolute_magnetization', sa.Float))
    op.add_column('systems', sa.Column('total_magnetization', sa.Float))


def downgrade():

    op.drop_column('systems', 'absolute_magnetization')
    op.drop_column('systems', 'total_magnetization')

