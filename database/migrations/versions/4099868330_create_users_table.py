"""create users table

Revision ID: 4099868330
Revises: 
Create Date: 2015-03-07 04:03:21.577157

"""

# revision identifiers, used by Alembic.
revision = '4099868330'
down_revision = None
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('email', sa.String(255), unique=True),
        sa.Column('nick', sa.String(50), nullable=False),
        sa.Column('password', sa.CHAR(60), nullable=False),
        sa.Column('is_admin', sa.Boolean(), default=False)
    )


def downgrade():
    op.drop_table('users')
