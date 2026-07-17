"""add quote_live_snapshot table

按外部引用令牌保存"生成报价单"页面的实时快照（值 + 导出文件），
供 TopSales 等第三方系统在用户点击"完成报价"前实时同步报价结果。

Revision ID: 011
Revises: 010
Create Date: 2026-07-16
"""
from alembic import op
import sqlalchemy as sa

revision = "011"
down_revision = "010"
branch_labels = None
depends_on = None


def _table_exists(conn, table_name: str) -> bool:
    return conn.execute(sa.text(
        "SELECT 1 FROM information_schema.tables WHERE table_name=:t"
    ), {"t": table_name}).fetchone() is not None


def upgrade() -> None:
    conn = op.get_bind()
    if not _table_exists(conn, "quote_live_snapshot"):
        op.create_table(
            "quote_live_snapshot",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("external_ref", sa.String(64), nullable=False, unique=True),
            sa.Column("data", sa.JSON(), nullable=True),
            sa.Column("files", sa.JSON(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        )
        op.create_index("ix_quote_live_snapshot_external_ref", "quote_live_snapshot", ["external_ref"], unique=True)


def downgrade() -> None:
    op.drop_table("quote_live_snapshot")
