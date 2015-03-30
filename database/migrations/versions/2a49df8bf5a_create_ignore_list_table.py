"""create ignore list table

Revision ID: 2a49df8bf5a
Revises: 53ac408e86c
Create Date: 2015-03-29 08:39:26.662823

"""

# revision identifiers, used by Alembic.
revision = '2a49df8bf5a'
down_revision = '53ac408e86c'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'ignore_list',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('source', sa.String(255)),
        sa.Column('mask', sa.String(50))
    )


def downgrade():
    op.drop_table('ignore_list')
