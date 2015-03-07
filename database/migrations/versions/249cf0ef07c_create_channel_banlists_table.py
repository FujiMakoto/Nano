"""create channel banlists table

Revision ID: 249cf0ef07c
Revises: 4fdbfa3b0e0
Create Date: 2015-03-07 05:21:38.694395

"""

# revision identifiers, used by Alembic.
revision = '249cf0ef07c'
down_revision = '4fdbfa3b0e0'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'channel_banlists',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('channel_id', sa.Integer, sa.ForeignKey('channels.id', ondelete="CASCADE", onupdate="CASCADE"),
                  nullable=False),
        sa.Column('nick', sa.String(50)),
        sa.Column('hostmask', sa.String(500), nullable=False),
        sa.Column('reason', sa.String(255)),
        sa.Column('banned_by_user_id', sa.Integer, sa.ForeignKey('users.id')),
        sa.Column('ban_length', sa.Integer),
        sa.Column('expires', sa.DateTime)
    )


def downgrade():
    op.drop_table('channel_banlists')
