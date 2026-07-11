"""add 2025 city social insurance fund fields

Revision ID: 009
Revises: 008
Create Date: 2026-07-07
"""
from alembic import op
import sqlalchemy as sa

revision = "009"
down_revision = "008"
branch_labels = None
depends_on = None


def _column_exists(conn, table_name: str, column_name: str) -> bool:
    return conn.execute(sa.text(
        "SELECT 1 FROM information_schema.columns "
        "WHERE table_name=:t AND column_name=:c"
    ), {"t": table_name, "c": column_name}).fetchone() is not None


def upgrade() -> None:
    conn = op.get_bind()
    columns = [
        ("fund_lower_limit", sa.Integer()),
        ("fund_upper_limit", sa.Integer()),
        ("fund_rate_min", sa.Float()),
        ("fund_rate_max", sa.Float()),
        ("fund_default_rate", sa.Float()),
    ]
    for name, column_type in columns:
        if not _column_exists(conn, "city_social_insurance", name):
            op.add_column(
                "city_social_insurance",
                sa.Column(name, column_type, nullable=True),
            )

    op.execute(
        "UPDATE city_social_insurance "
        "SET fund_lower_limit = COALESCE(fund_lower_limit, lower_limit), "
        "fund_upper_limit = COALESCE(fund_upper_limit, upper_limit), "
        "fund_default_rate = COALESCE(fund_default_rate, corp_fund_rate, indiv_fund_rate), "
        "fund_rate_min = COALESCE(fund_rate_min, corp_fund_rate, indiv_fund_rate), "
        "fund_rate_max = COALESCE(fund_rate_max, corp_fund_rate, indiv_fund_rate) "
        "WHERE fund_lower_limit IS NULL "
        "OR fund_upper_limit IS NULL "
        "OR fund_default_rate IS NULL "
        "OR fund_rate_min IS NULL "
        "OR fund_rate_max IS NULL"
    )


def downgrade() -> None:
    conn = op.get_bind()
    for name in [
        "fund_default_rate",
        "fund_rate_max",
        "fund_rate_min",
        "fund_upper_limit",
        "fund_lower_limit",
    ]:
        if _column_exists(conn, "city_social_insurance", name):
            op.drop_column("city_social_insurance", name)
