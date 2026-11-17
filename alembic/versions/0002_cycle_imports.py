"""Add provenance metadata for cycle CSV imports."""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0002_cycle_imports"
down_revision = "0001_batterylims_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "cycle_imports",
        sa.Column("import_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("execution_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("battery_lims.test_executions.execution_id"), nullable=False),
        sa.Column("original_filename", sa.String(255), nullable=False),
        sa.Column("raw_file_path", sa.Text(), nullable=False),
        sa.Column("sha256", sa.String(64), nullable=False),
        sa.Column("row_count", sa.Integer(), nullable=False),
        sa.Column("imported_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        schema="battery_lims",
        if_not_exists=True,
    )
    op.create_index("ix_cycle_imports_execution_id", "cycle_imports", ["execution_id"], schema="battery_lims", if_not_exists=True)
    op.create_unique_constraint("uq_cycle_import_execution_sha256", "cycle_imports", ["execution_id", "sha256"], schema="battery_lims")


def downgrade() -> None:
    op.drop_table("cycle_imports", schema="battery_lims")
