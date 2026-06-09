"""add semantic_noise_term table (语义噪声词候选)

存储从手动匹配已确认记录挖掘出的设备类型/噪声词候选，经审核后进入
语义抽取运行期词典。幂等：CREATE TABLE IF NOT EXISTS 语义，已存在则跳过。

Revision ID: 007
Revises: 006
Create Date: 2026-06-09
"""
from alembic import op
import sqlalchemy as sa

revision = "007"
down_revision = "006"
branch_labels = None
depends_on = None


def _table_exists(conn, table_name: str) -> bool:
    return conn.execute(sa.text(
        "SELECT 1 FROM information_schema.tables "
        "WHERE table_schema='public' AND table_name=:t"
    ), {"t": table_name}).fetchone() is not None


def upgrade() -> None:
    conn = op.get_bind()
    if not _table_exists(conn, "semantic_noise_term"):
        op.create_table(
            "semantic_noise_term",
            sa.Column("id", sa.Integer, primary_key=True),
            sa.Column("term", sa.String(128), nullable=False, unique=True),
            sa.Column("term_type", sa.String(32), server_default="device_type"),
            sa.Column("lang", sa.String(8), server_default="cn"),
            sa.Column("frequency", sa.Integer, server_default="0"),
            sa.Column("status", sa.String(16), server_default="pending"),
            sa.Column("source", sa.String(32), server_default="miner"),
            sa.Column("notes", sa.Text, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True),
                      server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True),
                      server_default=sa.func.now(), onupdate=sa.func.now()),
        )
        op.create_index("ix_semantic_noise_term_status",
                        "semantic_noise_term", ["status"])
        op.create_index("ix_semantic_noise_term_status_type",
                        "semantic_noise_term", ["status", "term_type"])


def downgrade() -> None:
    conn = op.get_bind()
    if _table_exists(conn, "semantic_noise_term"):
        op.drop_index("ix_semantic_noise_term_status_type",
                      table_name="semantic_noise_term")
        op.drop_index("ix_semantic_noise_term_status",
                      table_name="semantic_noise_term")
        op.drop_table("semantic_noise_term")
