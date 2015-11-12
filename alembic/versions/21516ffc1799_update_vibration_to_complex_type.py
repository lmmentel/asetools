"""update vibration to complex type

Revision ID: 21516ffc1799
Revises: 486c54de73dc
Create Date: 2015-11-12 15:32:15.532495

"""

# revision identifiers, used by Alembic.
revision = '21516ffc1799'
down_revision = '486c54de73dc'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():

    with op.batch_alter_table('vibrations') as bop:
        bop.drop_column('energy')
        bop.add_column(sa.Column('energy_real', sa.Float))
        bop.add_column(sa.Column('energy_imag', sa.Float))


def downgrade():
    pass
