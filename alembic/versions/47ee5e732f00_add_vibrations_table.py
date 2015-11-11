"""add vibrations table

Revision ID: 47ee5e732f00
Revises: 
Create Date: 2015-11-10 16:05:07.464763

"""

# revision identifiers, used by Alembic.
revision = '47ee5e732f00'
down_revision = None
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():

    op.create_table(
        'vibrations',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('system_id', sa.Integer, sa.ForeignKey('systems.id')),
        sa.Column('energy', sa.Float, nullable=False)
        )

def downgrade():

    op.drop_table('vibrations')
