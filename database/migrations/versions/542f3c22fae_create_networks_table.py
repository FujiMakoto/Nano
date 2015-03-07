"""create networks table

Revision ID: 542f3c22fae
Revises: 4099868330
Create Date: 2015-03-07 04:42:01.298366

"""

# revision identifiers, used by Alembic.
revision = '542f3c22fae'
down_revision = '4099868330'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'networks',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(255), unique=True, nullable=False),
        sa.Column('host', sa.String(255), unique=True, nullable=False),
        sa.Column('port', sa.SmallInteger, default=6667),
        sa.Column('server_password', sa.String(255)),
        sa.Column('nick', sa.String(50)),
        sa.Column('nick_password', sa.CHAR(255)),
        sa.Column('has_services', sa.Boolean()),
        sa.Column('autojoin', sa.Boolean(), default=True)
    )


def downgrade():
    op.drop_table('networks')
