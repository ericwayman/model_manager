"""Add a column to models

Revision ID: 38909e21798e
Revises: 5ab383397fa8
Create Date: 2017-06-24 18:24:54.499424

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '38909e21798e'
down_revision = '5ab383397fa8'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('models',sa.Column('training_results_dict',sa.JSON))


def downgrade():
    op.drop_column('models','training_results_dict')
