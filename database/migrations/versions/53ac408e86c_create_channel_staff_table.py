"""create channel staff table

Revision ID: 53ac408e86c
Revises: 249cf0ef07c
Create Date: 2015-03-26 02:30:11.815921

"""

# revision identifiers, used by Alembic.
revision = '53ac408e86c'
down_revision = '249cf0ef07c'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'channel_staff',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('channel_id', sa.Integer, sa.ForeignKey('channels.id', ondelete="CASCADE", onupdate="CASCADE"),
                  nullable=False),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id', ondelete="CASCADE", onupdate="CASCADE"),
                  nullable=False),
        sa.Column('access_level', sa.SmallInteger, default=0)
    )


def downgrade():
    op.drop_table('channel_staff')
