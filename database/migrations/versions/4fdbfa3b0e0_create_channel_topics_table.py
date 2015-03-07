"""create channel topics table

Revision ID: 4fdbfa3b0e0
Revises: 57fb2116a8c
Create Date: 2015-03-07 05:16:04.792419

"""

# revision identifiers, used by Alembic.
revision = '4fdbfa3b0e0'
down_revision = '57fb2116a8c'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'channel_topics',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('channel_id', sa.Integer, nullable=False),
        sa.Column('message', sa.String(1000), nullable=False),
        sa.Column('enabled', sa.Boolean, default=True),
        sa.Column('priority', sa.SmallInteger, default=0),
        sa.Column('expires', sa.DateTime)
    )


def downgrade():
    op.drop_table('channel_topics')
