"""Create jobs and results tables

Revision ID: 001_create_jobs_and_results
Revises: 
Create Date: 2026-08-15 18:35:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "001_create_jobs_and_results"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create PostgreSQL Enum Types
    image_type_enum = postgresql.ENUM("IR", "THERMAL", "OPTICAL", "OTHER", name="image_type_enum", create_type=False)
    job_status_enum = postgresql.ENUM("PENDING", "PROCESSING", "COMPLETED", "FAILED", name="job_status_enum", create_type=False)
    severity_level_enum = postgresql.ENUM("LOW", "MEDIUM", "HIGH", "CRITICAL", name="severity_level_enum", create_type=False)

    image_type_enum.create(op.get_bind(), checkfirst=True)
    job_status_enum.create(op.get_bind(), checkfirst=True)
    severity_level_enum.create(op.get_bind(), checkfirst=True)

    # Create Jobs table
    op.create_table(
        "jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("image_url", sa.String(), nullable=False),
        sa.Column("image_type", image_type_enum, nullable=False, server_default="OTHER"),
        sa.Column("status", job_status_enum, nullable=False, server_default="PENDING"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_jobs_status", "jobs", ["status"], unique=False)

    # Create Results table
    op.create_table(
        "results",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("job_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("disaster_type", sa.String(), nullable=False),
        sa.Column("severity", severity_level_enum, nullable=False, server_default="MEDIUM"),
        sa.Column("affected_area_estimate", sa.String(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("confidence_score", sa.Float(), nullable=True),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("raw_model_output", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("job_id", name="uq_results_job_id"),
    )
    op.create_index("ix_results_job_id", "results", ["job_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_results_job_id", table_name="results")
    op.drop_table("results")
    op.drop_index("ix_jobs_status", table_name="jobs")
    op.drop_table("jobs")

    sa.Enum(name="severity_level_enum").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="job_status_enum").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="image_type_enum").drop(op.get_bind(), checkfirst=True)
