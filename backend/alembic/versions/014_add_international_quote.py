"""add international onsite quote tables

Revision ID: 014
Revises: 013
Create Date: 2026-07-22
"""

from alembic import op
import sqlalchemy as sa


revision = "014"
down_revision = "013"
branch_labels = None
depends_on = None


def _table_exists(conn, table_name: str) -> bool:
    return conn.execute(
        sa.text("SELECT 1 FROM information_schema.tables WHERE table_name=:table_name"),
        {"table_name": table_name},
    ).fetchone() is not None


def upgrade() -> None:
    conn = op.get_bind()
    if not _table_exists(conn, "international_country_rule"):
        op.create_table(
            "international_country_rule",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("country_code", sa.String(32), nullable=False, unique=True),
            sa.Column("country_name", sa.String(64), nullable=False),
            sa.Column("default_city", sa.String(64), nullable=False),
            sa.Column("currency", sa.String(8), nullable=False),
            sa.Column("currency_symbol", sa.String(12), nullable=False),
            sa.Column("currency_precision", sa.Integer(), nullable=False, server_default="2"),
            sa.Column("exchange_rate_cny", sa.DECIMAL(18, 8), nullable=False),
            sa.Column("exchange_rate_date", sa.Date(), nullable=False),
            sa.Column("eor_rate", sa.DECIMAL(8, 4), nullable=False, server_default="12"),
            sa.Column("management_rate", sa.DECIMAL(8, 4), nullable=False, server_default="12"),
            sa.Column("profit_rate", sa.DECIMAL(8, 4), nullable=False, server_default="8"),
            sa.Column("vat_rate", sa.DECIMAL(8, 4), nullable=False, server_default="6"),
            sa.Column("local_vat_rate", sa.DECIMAL(8, 4), nullable=False, server_default="0"),
            sa.Column("local_vat_enabled", sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column("effective_label", sa.String(128), nullable=False),
            sa.Column("employee_profile", sa.String(200), nullable=False),
            sa.Column("parameter_config", sa.JSON(), nullable=False),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
        )
        op.create_index("ix_international_country_rule_country_code", "international_country_rule", ["country_code"])

    if not _table_exists(conn, "international_job_salary"):
        op.create_table(
            "international_job_salary",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("country_code", sa.String(32), nullable=False),
            sa.Column("country_name", sa.String(64), nullable=False),
            sa.Column("region", sa.String(128), nullable=False, server_default=""),
            sa.Column("city", sa.String(64), nullable=False),
            sa.Column("currency", sa.String(8), nullable=False),
            sa.Column("sequence_type", sa.String(32), nullable=False),
            sa.Column("category", sa.String(64), nullable=False),
            sa.Column("position_name", sa.String(128), nullable=False),
            sa.Column("level_name", sa.String(128), nullable=False),
            sa.Column("level_rank", sa.Integer(), nullable=False),
            sa.Column("monthly_salary", sa.DECIMAL(18, 2), nullable=False),
            sa.Column("notes", sa.String(500), nullable=True),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
            sa.UniqueConstraint(
                "country_code", "region", "city", "sequence_type", "position_name", "level_name",
                name="uq_international_salary_location_position_level",
            ),
        )
        op.create_index("ix_international_job_salary_country_code", "international_job_salary", ["country_code"])
        op.create_index("ix_international_job_salary_city", "international_job_salary", ["city"])
        op.create_index("ix_international_job_salary_position_name", "international_job_salary", ["position_name"])


def downgrade() -> None:
    conn = op.get_bind()
    if _table_exists(conn, "international_job_salary"):
        op.drop_table("international_job_salary")
    if _table_exists(conn, "international_country_rule"):
        op.drop_table("international_country_rule")
