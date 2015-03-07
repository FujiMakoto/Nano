"""create channels table

Revision ID: 57fb2116a8c
Revises: 542f3c22fae
Create Date: 2015-03-07 04:49:24.278482

"""

# revision identifiers, used by Alembic.
revision = '57fb2116a8c'
down_revision = '542f3c22fae'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'channels',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('network_id', sa.Integer, sa.ForeignKey('networks.id', ondelete="CASCADE", onupdate="CASCADE"),
                  nullable=False),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('channel_password', sa.String(255)),
        sa.Column('xop_level', sa.SmallInteger, default=0),
        sa.Column('manage_topic', sa.Boolean, default=False),
        sa.Column('topic_separator', sa.String(10), default='#'),
        sa.Column('topic_mode', sa.String(20), default='STATIC'),
        sa.Column('topic_max', sa.SmallInteger),
        sa.Column('autojoin', sa.Boolean)
    )


def downgrade():
    op.drop_table('channels')
