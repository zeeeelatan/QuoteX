"""fix: add missing JSONB columns to device_inventory

002 migration failed on production due to JSONB server_default quoting issue.
This migration re-applies the missing columns idempotently.

Revision ID: 003
Revises: 002
Create Date: 2026-03-28
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def _column_exists(conn, table_name: str, column_name: str) -> bool:
    result = conn.execute(sa.text(
        "SELECT 1 FROM information_schema.columns "
        "WHERE table_name=:t AND column_name=:c"
    ), {"t": table_name, "c": column_name})
    return result.fetchone() is not None


def _index_exists(conn, index_name: str) -> bool:
    result = conn.execute(sa.text(
        "SELECT 1 FROM pg_indexes WHERE indexname=:idx"
    ), {"idx": index_name})
    return result.fetchone() is not None


def _table_exists(conn, table_name: str) -> bool:
    result = conn.execute(sa.text(
        "SELECT 1 FROM information_schema.tables "
        "WHERE table_schema='public' AND table_name=:t"
    ), {"t": table_name})
    return result.fetchone() is not None


def upgrade() -> None:
    conn = op.get_bind()

    # 1. 确保 manufacturer 表存在
    if not _table_exists(conn, "manufacturer"):
        op.create_table(
            "manufacturer",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("name", sa.String(), nullable=False, unique=True),
            sa.Column("aliases", JSONB(), server_default=sa.text("'[]'")),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("updated_at", sa.DateTime(), nullable=True),
        )
        if not _index_exists(conn, "ix_manufacturer_id"):
            op.create_index("ix_manufacturer_id", "manufacturer", ["id"])
        if not _index_exists(conn, "ix_manufacturer_name"):
            op.create_index("ix_manufacturer_name", "manufacturer", ["name"])

    # 2. 确保 device_field_config 表存在
    if not _table_exists(conn, "device_field_config"):
        op.create_table(
            "device_field_config",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("device_type", sa.String(), nullable=True, index=True),
            sa.Column("field_key", sa.String(), nullable=False),
            sa.Column("field_label", sa.String(), nullable=False),
            sa.Column("field_type", sa.String(), server_default="string"),
            sa.Column("required", sa.Boolean(), server_default="false"),
            sa.Column("enum_options", JSONB(), nullable=True),
            sa.Column("default_value", sa.String(), nullable=True),
            sa.Column("display_order", sa.Integer(), server_default="0"),
            sa.Column("scope", sa.String(), server_default="type"),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("updated_at", sa.DateTime(), nullable=True),
        )
        if not _index_exists(conn, "ix_device_field_config_id"):
            op.create_index("ix_device_field_config_id", "device_field_config", ["id"])

    # 3. 确保 device_inventory 新列存在
    columns_to_add = [
        ("manufacturer_id", sa.Integer(), None),
        ("manufacturer_name", sa.String(), None),
        ("type_attributes", JSONB(), sa.text("'{}'")),
        ("custom_attributes", JSONB(), sa.text("'{}'")),
    ]
    for col_name, col_type, server_default in columns_to_add:
        if not _column_exists(conn, "device_inventory", col_name):
            op.add_column(
                "device_inventory",
                sa.Column(col_name, col_type, nullable=True, server_default=server_default),
            )

    # 4. 确保索引存在
    if not _index_exists(conn, "ix_device_inventory_manufacturer_id"):
        if _column_exists(conn, "device_inventory", "manufacturer_id"):
            op.create_index("ix_device_inventory_manufacturer_id", "device_inventory", ["manufacturer_id"])

    if not _index_exists(conn, "ix_device_inventory_manufacturer_name"):
        if _column_exists(conn, "device_inventory", "manufacturer_name"):
            op.create_index("ix_device_inventory_manufacturer_name", "device_inventory", ["manufacturer_name"])


def downgrade() -> None:
    pass  # 003 is a fix-up migration, no downgrade needed
