"""create paths table

Revision ID: 51938c0be2f8
Revises: 47ee5e732f00
Create Date: 2015-11-11 04:59:50.333085

"""

# revision identifiers, used by Alembic.
revision = '51938c0be2f8'
down_revision = '47ee5e732f00'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():

    op.create_table(
        'paths',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('system_id', sa.Integer, sa.ForeignKey('systems.id')),
        sa.Column('name', sa.String),
        sa.Column('abspath', sa.String),
        sa.Column('inpname', sa.String),
        sa.Column('outname', sa.String),
        sa.Column('status', sa.String),
        )


def downgrade():

    op.drop_table('paths')
