"""create account table

Revision ID: 5ab383397fa8
Revises: 
Create Date: 2017-06-24 18:10:14.879003

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5ab383397fa8'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'models',
        sa.Column('model_id',sa.Integer,primary_key=True),
        sa.Column('time_stamp',sa.DateTime),
        sa.Column('time_to_run_script',sa.Interval),
        sa.Column('model_script',sa.Text),
        sa.Column('model_nickname',sa.Text),
        sa.Column('model_param_dict',sa.JSON),
        sa.Column('param_config_file',sa.Text),
    )

def downgrade():
    op.drop_table('models')
