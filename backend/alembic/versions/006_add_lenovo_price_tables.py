"""add 6 lenovo_price_* tables to alembic

Historical note: like lenovo_classification / lenovo_pattern_rule fixed in 005,
the 6 联想框架价格表 (tape / network / server / storage / minicomputer / inspection)
were originally created via SQLAlchemy `create_all()` in dev and never had a
corresponding alembic migration. As a result the 2026-06-03 production deploy
showed 500 errors on every `/lenovo/prices/*` endpoint because the tables
didn't exist on the production database.

This migration:
- Creates all 6 tables idempotently (CREATE TABLE IF NOT EXISTS)
- Adds unique constraints matching the ORM definitions

Note: this migration is schema-only. The actual price data must be imported
separately (one-time pg_dump from authoritative source).

Revision ID: 006
Revises: 005
Create Date: 2026-06-03
"""
from alembic import op
import sqlalchemy as sa

revision = "006"
down_revision = "005"
branch_labels = None
depends_on = None


def _table_exists(conn, table_name: str) -> bool:
    return conn.execute(sa.text(
        "SELECT 1 FROM information_schema.tables "
        "WHERE table_schema='public' AND table_name=:t"
    ), {"t": table_name}).fetchone() is not None


def upgrade() -> None:
    conn = op.get_bind()

    # ── 磁带库价格 ──────────────────────────────────────────
    if not _table_exists(conn, "lenovo_price_tape_library"):
        op.create_table(
            "lenovo_price_tape_library",
            sa.Column("id", sa.Integer, primary_key=True),
            sa.Column("end_type", sa.String(16), nullable=False),
            sa.Column("drive_config", sa.String(16), nullable=False),
            sa.Column("sla", sa.String(32), nullable=False),
            sa.Column("price", sa.Numeric(12, 2), nullable=False),
            sa.Column("notes", sa.Text, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True),
                      server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True),
                      server_default=sa.func.now(), onupdate=sa.func.now()),
            sa.UniqueConstraint("end_type", "drive_config", "sla",
                                name="uq_lenovo_price_tape"),
        )

    # ── 网络/光纤/IB 价格 ───────────────────────────────────
    if not _table_exists(conn, "lenovo_price_network"):
        op.create_table(
            "lenovo_price_network",
            sa.Column("id", sa.Integer, primary_key=True),
            sa.Column("device_category", sa.String(32), nullable=False),
            sa.Column("end_type", sa.String(16), nullable=False),
            sa.Column("sla", sa.String(32), nullable=False),
            sa.Column("price", sa.Numeric(12, 2), nullable=False),
            sa.Column("notes", sa.Text, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True),
                      server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True),
                      server_default=sa.func.now(), onupdate=sa.func.now()),
            sa.UniqueConstraint("device_category", "end_type", "sla",
                                name="uq_lenovo_price_network"),
        )

    # ── 服务器价格 ──────────────────────────────────────────
    if not _table_exists(conn, "lenovo_price_server"):
        op.create_table(
            "lenovo_price_server",
            sa.Column("id", sa.Integer, primary_key=True),
            sa.Column("end_type", sa.String(16), nullable=False),
            sa.Column("includes_ssd", sa.Boolean, nullable=False),
            sa.Column("package_type", sa.String(16), nullable=False),
            sa.Column("sla", sa.String(16), nullable=False),
            sa.Column("includes_disk", sa.Boolean, nullable=False),
            sa.Column("price", sa.Numeric(12, 2), nullable=False),
            sa.Column("notes", sa.Text, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True),
                      server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True),
                      server_default=sa.func.now(), onupdate=sa.func.now()),
            sa.UniqueConstraint("end_type", "includes_ssd", "package_type",
                                "sla", "includes_disk",
                                name="uq_lenovo_price_server"),
        )

    # ── 存储价格 ────────────────────────────────────────────
    if not _table_exists(conn, "lenovo_price_storage"):
        op.create_table(
            "lenovo_price_storage",
            sa.Column("id", sa.Integer, primary_key=True),
            sa.Column("end_type", sa.String(8), nullable=False),
            sa.Column("sla", sa.String(16), nullable=False),
            sa.Column("includes_disk_no_return", sa.Boolean, nullable=False),
            sa.Column("price", sa.Numeric(12, 2), nullable=False),
            sa.Column("notes", sa.Text, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True),
                      server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True),
                      server_default=sa.func.now(), onupdate=sa.func.now()),
            sa.UniqueConstraint("end_type", "sla", "includes_disk_no_return",
                                name="uq_lenovo_price_storage"),
        )

    # ── 小型机价格 ──────────────────────────────────────────
    if not _table_exists(conn, "lenovo_price_minicomputer"):
        op.create_table(
            "lenovo_price_minicomputer",
            sa.Column("id", sa.Integer, primary_key=True),
            sa.Column("end_type", sa.String(16), nullable=False),
            sa.Column("sla", sa.String(32), nullable=False),
            sa.Column("includes_disk", sa.Boolean, nullable=False),
            sa.Column("price", sa.Numeric(12, 2), nullable=False),
            sa.Column("notes", sa.Text, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True),
                      server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True),
                      server_default=sa.func.now(), onupdate=sa.func.now()),
            sa.UniqueConstraint("end_type", "sla", "includes_disk",
                                name="uq_lenovo_price_mini"),
        )

    # ── 巡检价格 ────────────────────────────────────────────
    if not _table_exists(conn, "lenovo_price_inspection"):
        op.create_table(
            "lenovo_price_inspection",
            sa.Column("id", sa.Integer, primary_key=True),
            sa.Column("unit", sa.String(16), nullable=False, unique=True),
            sa.Column("price", sa.Numeric(12, 2), nullable=False),
            sa.Column("tax_rate", sa.Numeric(6, 4), nullable=False,
                      server_default="0.06"),
            sa.Column("notes", sa.Text, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True),
                      server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True),
                      server_default=sa.func.now(), onupdate=sa.func.now()),
        )


def downgrade() -> None:
    conn = op.get_bind()
    for tbl in [
        "lenovo_price_inspection",
        "lenovo_price_minicomputer",
        "lenovo_price_storage",
        "lenovo_price_server",
        "lenovo_price_network",
        "lenovo_price_tape_library",
    ]:
        if _table_exists(conn, tbl):
            op.drop_table(tbl)
