"""remove job position salary bounds

Revision ID: 015
Revises: 014
Create Date: 2026-07-23
"""

from alembic import op
import sqlalchemy as sa


revision = "015"
down_revision = "014"
branch_labels = None
depends_on = None


def _column_exists(conn, table_name: str, column_name: str) -> bool:
    return conn.execute(
        sa.text(
            """
            SELECT 1
            FROM information_schema.columns
            WHERE table_name = :table_name
              AND column_name = :column_name
            """
        ),
        {"table_name": table_name, "column_name": column_name},
    ).fetchone() is not None


def upgrade() -> None:
    conn = op.get_bind()
    if _column_exists(conn, "job_position", "system_salary_min"):
        op.drop_column("job_position", "system_salary_min")
    if _column_exists(conn, "job_position", "system_salary_max"):
        op.drop_column("job_position", "system_salary_max")


def downgrade() -> None:
    conn = op.get_bind()
    if not _column_exists(conn, "job_position", "system_salary_max"):
        op.add_column(
            "job_position",
            sa.Column(
                "system_salary_max",
                sa.DECIMAL(12, 2),
                nullable=True,
                comment="系统取值最大值",
            ),
        )
    if not _column_exists(conn, "job_position", "system_salary_min"):
        op.add_column(
            "job_position",
            sa.Column(
                "system_salary_min",
                sa.DECIMAL(12, 2),
                nullable=True,
                comment="系统取值最小值",
            ),
        )
