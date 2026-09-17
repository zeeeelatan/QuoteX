"""add exchange rate source

Revision ID: 016
Revises: 015
Create Date: 2026-08-07
"""

from alembic import op
import sqlalchemy as sa


revision = "016"
down_revision = "015"
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
    if not _column_exists(conn, "international_country_rule", "exchange_rate_source"):
        op.add_column(
            "international_country_rule",
            sa.Column(
                "exchange_rate_source",
                sa.String(32),
                nullable=False,
                server_default="manual",
            ),
        )
    if not _column_exists(conn, "international_country_rule", "exchange_rate_checked_at"):
        op.add_column(
            "international_country_rule",
            sa.Column("exchange_rate_checked_at", sa.DateTime(), nullable=True),
        )


def downgrade() -> None:
    conn = op.get_bind()
    if _column_exists(conn, "international_country_rule", "exchange_rate_checked_at"):
        op.drop_column("international_country_rule", "exchange_rate_checked_at")
    if _column_exists(conn, "international_country_rule", "exchange_rate_source"):
        op.drop_column("international_country_rule", "exchange_rate_source")
