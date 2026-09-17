"""add quote_type to quote_history

Revision ID: 017
Revises: 016
Create Date: 2026-09-17
"""

from alembic import op
import sqlalchemy as sa


revision = "017"
down_revision = "016"
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
    if not _column_exists(conn, "quote_history", "quote_type"):
        op.add_column(
            "quote_history",
            sa.Column(
                "quote_type",
                sa.String(32),
                nullable=False,
                server_default="maintenance",
            ),
        )
        op.create_index(
            "ix_quote_history_quote_type",
            "quote_history",
            ["quote_type"],
        )


def downgrade() -> None:
    conn = op.get_bind()
    if _column_exists(conn, "quote_history", "quote_type"):
        op.drop_index("ix_quote_history_quote_type", table_name="quote_history")
        op.drop_column("quote_history", "quote_type")
