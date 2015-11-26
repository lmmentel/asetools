"""create vibrationsets and adapt vibrations

Revision ID: 1e8cdcbd84c5
Revises: 1481d81d6359
Create Date: 2015-11-26 20:37:01.319049

"""

# revision identifiers, used by Alembic.
revision = '1e8cdcbd84c5'
down_revision = '1481d81d6359'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():

    # create the vibrationsets table

    op.create_table(
        'vibrationsets',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String),
        sa.Column('atom_ids', sa.String),
        sa.Column('system_id', sa.Integer, sa.ForeignKey('systems.id')),
        )

    # modify the vibrations table

    op.drop_column('vibrations', 'system_id')
    op.add_column('vibrations', sa.Column('vibrationset_id', sa.Integer, sa.ForeignKey('vibrationsets.id')))


def downgrade():

    op.drop_column('vibrations', 'vibrationset_id')
    op.add_column('vibrations', sa.Column('system_id', sa.Integer, sa.ForeignKey('systems.id')))

    op.drop_table('vibrationsets')
