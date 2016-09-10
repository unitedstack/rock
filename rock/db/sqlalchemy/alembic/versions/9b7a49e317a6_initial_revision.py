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
import sqlalchemy  as sa
from oslo_utils import timeutils
from oslo_utils import uuidutils
import sqlalchemy_utils as su
from taskflow.persistence import models
from taskflow import states


# Column length limits...
NAME_LENGTH = 255
UUID_LENGTH = 64
STATE_LENGTH = 255
VERSION_LENGTH = 64


def upgrade():
    op.create_table(
        "ping",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("created_at",
                  sa.DateTime(),
                  default=lambda: timeutils.utcnow(),
                  nullable=False),
        sa.Column("target", sa.String(length=36), nullable=False),
        sa.Column("result", sa.Boolean(), nullable=False),
        sa.Column("delay", sa.Float(), default=0.0, nullable=False)
    )

    op.create_table(
        "nova_service",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("created_at",
                  sa.DateTime(),
                  default=lambda: timeutils.utcnow(),
                  nullable=False),
        sa.Column("target", sa.String(length=36), nullable=False),
        sa.Column("result", sa.Boolean(), nullable=False),
        sa.Column("service_status", sa.Boolean(), nullable=False),
        sa.Column("service_state", sa.Boolean(), nullable=False)

    )
    op.create_table(
        "logbooks",
        sa.Column('created_at',
                  sa.DateTime(),
                  default=lambda: timeutils.utcnow(),
                  nullable=True),
        sa.Column('updated_at',
                  sa.DateTime(),
                  default=lambda: timeutils.utcnow(),
                  nullable=True),
        sa.Column('meta', su.JSONType),
        sa.Column('name', sa.String(length=NAME_LENGTH)),
        sa.Column('uuid', sa.String(length=UUID_LENGTH),
                  primary_key=True, nullable=False, unique=True,
                  default=uuidutils.generate_uuid)
    )
    op.create_table(
        "flowdetails",
        sa.Column('created_at',
                  sa.DateTime(),
                  default=lambda: timeutils.utcnow(),
                  nullable=True),
        sa.Column('updated_at',
                  sa.DateTime(),
                  default=lambda: timeutils.utcnow(),
                  nullable=True),
        sa.Column('parent_uuid', sa.String(length=UUID_LENGTH),
                  sa.ForeignKey('logbooks.uuid',
                             ondelete='CASCADE')),
        sa.Column('meta', su.JSONType),
        sa.Column('name', sa.String(length=NAME_LENGTH)),
        sa.Column('state', sa.String(length=STATE_LENGTH)),
        sa.Column('uuid', sa.String(length=UUID_LENGTH),
                  primary_key=True, nullable=False, unique=True,
                  default=uuidutils.generate_uuid)
    )

    op.create_table(
        "atomdetails",
        sa.Column('created_at',
                  sa.DateTime(),
                  default=lambda: timeutils.utcnow(),
                  nullable=True),
        sa.Column('updated_at',
                  sa.DateTime(),
                  default=lambda: timeutils.utcnow(),
                  nullable=True),
        sa.Column('parent_uuid', sa.String(length=UUID_LENGTH),
                  sa.ForeignKey('flowdetails.uuid',
                             ondelete='CASCADE')),
        sa.Column('meta', su.JSONType),
        sa.Column('name', sa.String(length=NAME_LENGTH)),
        sa.Column('version', sa.String(length=VERSION_LENGTH)),
        sa.Column('state', sa.String(length=STATE_LENGTH)),
        sa.Column('uuid', sa.String(length=UUID_LENGTH),
                  primary_key=True, nullable=False, unique=True,
                  default=uuidutils.generate_uuid),
        sa.Column('failure', su.JSONType),
        sa.Column('results', su.JSONType),
        sa.Column('revert_results', su.JSONType),
        sa.Column('revert_failure', su.JSONType),
        sa.Column('atom_type', sa.Enum(*models.ATOM_TYPES,
                                    name='atom_types')),
        sa.Column('intention', sa.Enum(*states.INTENTIONS,
                                                 name='intentions'))
    )

def downgrade():
    op.drop_table('ping')
    op.drop_table('nova_service')
    op.drop_table('atomdetails')
    op.drop_table('flowdetails')
    op.drop_table('logbooks')
