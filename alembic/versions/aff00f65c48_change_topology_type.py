"""change topology type

Revision ID: aff00f65c48
Revises: 21516ffc1799
Create Date: 2015-11-19 16:31:25.233716

"""

# revision identifiers, used by Alembic.
revision = 'aff00f65c48'
down_revision = '21516ffc1799'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():

    with op.batch_alter_table('systems') as bop:
        bop.alter_column('topology', type_=sa.String)

def downgrade():

    with op.batch_alter_table('systems') as bop:
        bop.alter_column('topology', type_=sa.String(3))
