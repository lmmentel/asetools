"""move username from System to Job

Revision ID: 59a3c754a95a
Revises: 
Create Date: 2015-11-26 19:02:18.134381

"""

# revision identifiers, used by Alembic.
revision = '59a3c754a95a'
down_revision = None
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    
    op.add_column('jobs', sa.Column('username', sa.String))


def downgrade():
    
    op.drop_column('systems', 'username')
