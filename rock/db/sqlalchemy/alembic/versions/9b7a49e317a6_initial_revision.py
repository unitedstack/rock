"""Initial revision

Revision ID: 9b7a49e317a6
Revises:
Create Date: 2016-08-20 11:50:49.529519

"""

# revision identifiers, used by Alembic.
revision = '9b7a49e317a6'
down_revision = None
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
from oslo_utils import timeutils


def upgrade():
    op.create_table(
        "ping",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("create_at",
                  sa.DateTime(),
                  default=lambda: timeutils.utcnow(),
                  nullable=False),
        sa.Column("target", sa.String(length=36), nullable=False),
        sa.Column("result", sa.Boolean(), default=False, nullable=False),
        sa.Column("delay", sa.Float(), default=0.0, nullable=False)
    )

    op.create_table(
        "nova_service",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("create_at",
                  sa.DateTime(),
                  default=lambda: timeutils.utcnow(),
                  nullable=False),
        sa.Column("target", sa.String(length=36), nullable=False),
        sa.Column("result", sa.Boolean(), default=False, nullable=False),
        sa.Column("service_status", sa.String(length=8), nullable=True)

    )

def downgrade():
    op.drop_table('ping')
    op.drop_table('nova_service')
