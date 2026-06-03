"""add legacy lenovo_classification + lenovo_pattern_rule tables to alembic

Historical note: these two tables were originally created in dev environments
via SQLAlchemy `Base.metadata.create_all()` and never had a corresponding
alembic migration. As a result the 2026-06-03 production deploy ran 004
(which depends on them being non-empty) without the tables existing at all.

This migration backfills the schema so any fresh environment (staging /
disaster recovery / new server) gets the same structure deterministically.

It is **idempotent**: existing production instances already have these tables
(filled in via manual SQL after the 004 incident), so CREATE TABLE IF NOT
EXISTS is a no-op there.

Revision ID: 005
Revises: 004
Create Date: 2026-06-03
"""
from alembic import op
import sqlalchemy as sa

revision = "005"
down_revision = "004"
branch_labels = None
depends_on = None


def _table_exists(conn, table_name: str) -> bool:
    return conn.execute(sa.text(
        "SELECT 1 FROM information_schema.tables "
        "WHERE table_schema='public' AND table_name=:t"
    ), {"t": table_name}).fetchone() is not None


def upgrade() -> None:
    conn = op.get_bind()

    if not _table_exists(conn, "lenovo_classification"):
        op.create_table(
            "lenovo_classification",
            sa.Column("id", sa.Integer, primary_key=True),
            sa.Column("device_category", sa.String(32), nullable=False),
            sa.Column("brand", sa.String(128), nullable=True),
            sa.Column("series", sa.String(255), nullable=True),
            sa.Column("model", sa.String(255), nullable=False),
            sa.Column("mt_code", sa.String(64), nullable=True),
            sa.Column("end_type", sa.String(32), nullable=False),
            sa.Column("sub_category", sa.String(32), nullable=True),
            sa.Column("source_sheet", sa.String(64), nullable=True),
            sa.Column("notes", sa.Text, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True),
                      server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True),
                      server_default=sa.func.now(), onupdate=sa.func.now()),
        )
        op.create_index("ix_lenovo_classification_device_category",
                        "lenovo_classification", ["device_category"])
        op.create_index("ix_lenovo_classification_model",
                        "lenovo_classification", ["model"])
        op.create_index("ix_lenovo_classification_lookup",
                        "lenovo_classification",
                        ["device_category", "brand", "model"])

    if not _table_exists(conn, "lenovo_pattern_rule"):
        op.create_table(
            "lenovo_pattern_rule",
            sa.Column("id", sa.Integer, primary_key=True),
            sa.Column("device_category", sa.String(32), nullable=False),
            sa.Column("brand", sa.String(128), nullable=False),
            sa.Column("pattern_raw", sa.String(512), nullable=False),
            sa.Column("pattern_regex", sa.String(1024), nullable=False),
            sa.Column("end_type", sa.String(32), nullable=False),
            sa.Column("priority", sa.Integer, nullable=False,
                      server_default="100"),
            sa.Column("notes", sa.Text, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True),
                      server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True),
                      server_default=sa.func.now(), onupdate=sa.func.now()),
        )
        op.create_index("ix_lenovo_pattern_rule_device_category",
                        "lenovo_pattern_rule", ["device_category"])
        op.create_index("ix_lenovo_pattern_rule_brand",
                        "lenovo_pattern_rule", ["brand"])


def downgrade() -> None:
    conn = op.get_bind()
    if _table_exists(conn, "lenovo_pattern_rule"):
        op.drop_index("ix_lenovo_pattern_rule_brand",
                      table_name="lenovo_pattern_rule")
        op.drop_index("ix_lenovo_pattern_rule_device_category",
                      table_name="lenovo_pattern_rule")
        op.drop_table("lenovo_pattern_rule")
    if _table_exists(conn, "lenovo_classification"):
        op.drop_index("ix_lenovo_classification_lookup",
                      table_name="lenovo_classification")
        op.drop_index("ix_lenovo_classification_model",
                      table_name="lenovo_classification")
        op.drop_index("ix_lenovo_classification_device_category",
                      table_name="lenovo_classification")
        op.drop_table("lenovo_classification")
