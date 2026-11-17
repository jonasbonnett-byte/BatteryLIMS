"""Initial BatteryLIMS PostgreSQL schema.

This is the bootstrap migration for the project. Later revisions should use explicit
Alembic operations so deployed schema changes remain immutable and reviewable.
"""

from alembic import op

from app.db import Base
import app.models  # noqa: F401

revision = "0001_batterylims_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    op.execute("CREATE SCHEMA IF NOT EXISTS battery_lims")
    Base.metadata.create_all(bind=bind, checkfirst=True)


def downgrade() -> None:
    bind = op.get_bind()
    Base.metadata.drop_all(bind=bind, checkfirst=True)
    op.execute("DROP SCHEMA IF EXISTS battery_lims")
