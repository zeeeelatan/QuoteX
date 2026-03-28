"""device inventory refactor: manufacturer dict + field config + JSONB dynamic fields

Creates manufacturer and device_field_config tables, adds new columns to
device_inventory for brand linking and dynamic attributes.

Revision ID: 002
Revises: 001
Create Date: 2026-03-28
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def _table_exists(conn, table_name: str) -> bool:
    result = conn.execute(sa.text(
        "SELECT 1 FROM information_schema.tables "
        "WHERE table_schema='public' AND table_name=:t"
    ), {"t": table_name})
    return result.fetchone() is not None


def _column_exists(conn, table_name: str, column_name: str) -> bool:
    result = conn.execute(sa.text(
        "SELECT 1 FROM information_schema.columns "
        "WHERE table_name=:t AND column_name=:c"
    ), {"t": table_name, "c": column_name})
    return result.fetchone() is not None


def upgrade() -> None:
    conn = op.get_bind()

    # 1. 创建品牌字典表 manufacturer
    if not _table_exists(conn, "manufacturer"):
        op.create_table(
            "manufacturer",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("name", sa.String(), nullable=False, unique=True),
            sa.Column("aliases", JSONB(), server_default="[]"),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("updated_at", sa.DateTime(), nullable=True),
        )
        op.create_index("ix_manufacturer_id", "manufacturer", ["id"])
        op.create_index("ix_manufacturer_name", "manufacturer", ["name"])

    # 2. 创建字段配置表 device_field_config
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
        op.create_index("ix_device_field_config_id", "device_field_config", ["id"])

    # 3. device_inventory 表添加新列
    new_columns = [
        ("manufacturer_id", sa.Integer(), None),
        ("manufacturer_name", sa.String(), None),
        ("type_attributes", JSONB(), sa.text("'{}'")),
        ("custom_attributes", JSONB(), sa.text("'{}'")),
    ]
    for col_name, col_type, server_default in new_columns:
        if not _column_exists(conn, "device_inventory", col_name):
            op.add_column(
                "device_inventory",
                sa.Column(col_name, col_type, nullable=True, server_default=server_default),
            )

    # 4. 为 manufacturer_id 添加索引（如果不存在）
    if _column_exists(conn, "device_inventory", "manufacturer_id"):
        # 检查索引是否已存在
        result = conn.execute(sa.text(
            "SELECT 1 FROM pg_indexes WHERE tablename='device_inventory' "
            "AND indexname='ix_device_inventory_manufacturer_id'"
        ))
        if result.fetchone() is None:
            op.create_index(
                "ix_device_inventory_manufacturer_id",
                "device_inventory",
                ["manufacturer_id"],
            )

    # 5. 为 manufacturer_name 添加索引（如果不存在）
    if _column_exists(conn, "device_inventory", "manufacturer_name"):
        result = conn.execute(sa.text(
            "SELECT 1 FROM pg_indexes WHERE tablename='device_inventory' "
            "AND indexname='ix_device_inventory_manufacturer_name'"
        ))
        if result.fetchone() is None:
            op.create_index(
                "ix_device_inventory_manufacturer_name",
                "device_inventory",
                ["manufacturer_name"],
            )


def downgrade() -> None:
    # 移除 device_inventory 新列
    op.drop_index("ix_device_inventory_manufacturer_name", table_name="device_inventory")
    op.drop_index("ix_device_inventory_manufacturer_id", table_name="device_inventory")
    op.drop_column("device_inventory", "custom_attributes")
    op.drop_column("device_inventory", "type_attributes")
    op.drop_column("device_inventory", "manufacturer_name")
    op.drop_column("device_inventory", "manufacturer_id")

    # 删除新表
    op.drop_table("device_field_config")
    op.drop_table("manufacturer")
