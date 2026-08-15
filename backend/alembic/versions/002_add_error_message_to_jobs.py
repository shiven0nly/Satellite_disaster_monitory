"""Add error_message column to jobs table

Revision ID: 002_add_error_message_to_jobs
Revises: 001_create_jobs_and_results
Create Date: 2026-08-15 19:46:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "002_add_error_message_to_jobs"
down_revision: Union[str, None] = "001_create_jobs_and_results"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("jobs", sa.Column("error_message", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("jobs", "error_message")
