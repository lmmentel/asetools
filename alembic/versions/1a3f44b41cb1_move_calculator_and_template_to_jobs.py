"""move calculator and template to jobs

Revision ID: 1a3f44b41cb1
Revises: 39ea027f3369
Create Date: 2015-11-12 11:27:36.979936

"""

# revision identifiers, used by Alembic.
revision = '1a3f44b41cb1'
down_revision = '39ea027f3369'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():

    with op.batch_alter_table('jobs') as bop:
        bop.add_column(sa.Column('calculator_id', sa.Integer))
        bop.add_column(sa.Column('template_id', sa.Integer))
        bop.create_foreign_key('fk_job_calc', 'calculators', ['calculator_id'], ['id'])
        bop.create_foreign_key('fk_job_temp', 'asetemplates', ['template_id'], ['id'])

    jobs = sa.sql.table('jobs',
            sa.Column('id', sa.String),
            sa.Column('system_id', sa.Integer, sa.ForeignKey('systems.id')),
            sa.Column('name', sa.String),
            sa.Column('abspath', sa.String),
            sa.Column('inpname', sa.String),
            sa.Column('outname', sa.String),
            sa.Column('status', sa.String),
            sa.Column('calculator_id', sa.Integer, sa.ForeignKey('calculators.id')),
            sa.Column('template_id', sa.Integer, sa.ForeignKey('asetemplates.id')),
            )

    conn = op.get_bind()
    res = conn.execute("select id, calculator_id, template_id from systems")
    results = res.fetchall()
    data = [{'system_id' : r[0], 'calculator_id' : r[1], 'template_id' : r[2]} for r in results]

    op.bulk_insert(jobs, data)

    with op.batch_alter_table('systems') as bop:
        bop.drop_column('calculator_id')
        bop.drop_column('template_id')

def downgrade():

    op.add_column('systems', sa.Column('calculator_id', sa.Integer, sa.ForeignKey('calculators.id')))
    op.add_column('systems', sa.Column('template_id', sa.Integer, sa.ForeignKey('asetemplates.id')))

    op.drop_column('jobs', 'calculator_id')
    op.drop_column('jobs', 'template_id')
