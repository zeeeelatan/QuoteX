"""add korea job salary table

Revision ID: 013
Revises: 012
Create Date: 2026-07-20
"""
from alembic import op
import sqlalchemy as sa


revision = "013"
down_revision = "012"
branch_labels = None
depends_on = None


def _table_exists(conn, table_name: str) -> bool:
    return conn.execute(
        sa.text("SELECT 1 FROM information_schema.tables WHERE table_name=:table_name"),
        {"table_name": table_name},
    ).fetchone() is not None


def upgrade() -> None:
    conn = op.get_bind()
    if not _table_exists(conn, "korea_job_salary"):
        op.create_table(
            "korea_job_salary",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("city", sa.String(50), nullable=False),
            sa.Column("position_name", sa.String(128), nullable=False),
            sa.Column("monthly_salary_krw", sa.DECIMAL(14, 2), nullable=False),
            sa.Column("notes", sa.String(500), nullable=True),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
            sa.UniqueConstraint(
                "city",
                "position_name",
                name="uq_korea_job_salary_city_position",
            ),
        )
        op.create_index("ix_korea_job_salary_city", "korea_job_salary", ["city"])
        op.create_index(
            "ix_korea_job_salary_position_name",
            "korea_job_salary",
            ["position_name"],
        )

    conn.execute(
        sa.text(
            "INSERT INTO korea_job_salary "
            "(city, position_name, monthly_salary_krw, notes, is_active) "
            "SELECT :city, :position_name, :salary, :notes, TRUE "
            "WHERE NOT EXISTS ("
            "SELECT 1 FROM korea_job_salary "
            "WHERE city=:city AND position_name=:position_name"
            ")"
        ),
        {
            "city": "首尔",
            "position_name": "桌面运维（3年+）",
            "salary": 5640000,
            "notes": "韩国报价测算首期基准岗位",
        },
    )


def downgrade() -> None:
    conn = op.get_bind()
    if _table_exists(conn, "korea_job_salary"):
        op.drop_table("korea_job_salary")
