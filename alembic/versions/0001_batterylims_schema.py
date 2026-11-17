"""Initial BatteryLIMS PostgreSQL schema."""

from alembic import op

from app.db import Base
import app.models  # noqa: F401

revision = "0001_batterylims_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS battery_lims")
    Base.metadata.create_all(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    Base.metadata.drop_all(bind=op.get_bind(), checkfirst=True)
    op.execute("DROP SCHEMA IF EXISTS battery_lims")
