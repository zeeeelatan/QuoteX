"""add job_position and job_position_salary tables

驻场岗位职级与城市薪资表，替代旧 outsourced_personnel（旧表保留不删除，数据作废）。

Revision ID: 010
Revises: 009
Create Date: 2026-07-11
"""
from alembic import op
import sqlalchemy as sa

revision = "010"
down_revision = "009"
branch_labels = None
depends_on = None


def _table_exists(conn, table_name: str) -> bool:
    return conn.execute(sa.text(
        "SELECT 1 FROM information_schema.tables WHERE table_name=:t"
    ), {"t": table_name}).fetchone() is not None


def upgrade() -> None:
    conn = op.get_bind()

    if not _table_exists(conn, "job_position"):
        op.create_table(
            "job_position",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("sequence_type", sa.String(20), nullable=False),
            sa.Column("category", sa.String(50), nullable=False),
            sa.Column("position_name", sa.String(128), nullable=False),
            sa.Column("level_name", sa.String(64), nullable=False),
            sa.Column("level_rank", sa.Integer(), nullable=False, server_default="1"),
            sa.Column("core_requirements", sa.Text(), nullable=True),
            sa.Column("certifications", sa.Text(), nullable=True),
            sa.Column("work_content", sa.Text(), nullable=True),
            sa.Column("deliverables", sa.Text(), nullable=True),
            sa.Column("kpi_standards", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
            sa.UniqueConstraint("position_name", "level_name", name="uq_job_position_name_level"),
        )
        op.create_index("ix_job_position_sequence_type", "job_position", ["sequence_type"])
        op.create_index("ix_job_position_category", "job_position", ["category"])
        op.create_index("ix_job_position_position_name", "job_position", ["position_name"])

    if not _table_exists(conn, "job_position_salary"):
        op.create_table(
            "job_position_salary",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "position_id",
                sa.Integer(),
                sa.ForeignKey("job_position.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("province", sa.String(50), nullable=True),
            sa.Column("city", sa.String(50), nullable=False),
            sa.Column("salary", sa.DECIMAL(10, 2), nullable=False),
            sa.UniqueConstraint("position_id", "city", name="uq_job_position_salary_city"),
        )
        op.create_index("ix_job_position_salary_position_id", "job_position_salary", ["position_id"])
        op.create_index("ix_job_position_salary_city", "job_position_salary", ["city"])


def downgrade() -> None:
    conn = op.get_bind()
    if _table_exists(conn, "job_position_salary"):
        op.drop_table("job_position_salary")
    if _table_exists(conn, "job_position"):
        op.drop_table("job_position")
