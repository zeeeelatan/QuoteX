"""add last_active_at to user_profile

Revision ID: 001
Revises:
Create Date: 2026-03-18
"""
from alembic import op
import sqlalchemy as sa

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 安全添加：列已存在时跳过，避免手动执行过 ALTER TABLE 后重复报错
    conn = op.get_bind()
    result = conn.execute(sa.text(
        "SELECT 1 FROM information_schema.columns "
        "WHERE table_name='user_profile' AND column_name='last_active_at'"
    ))
    if result.fetchone() is None:
        op.add_column(
            "user_profile",
            sa.Column("last_active_at", sa.DateTime(), nullable=True),
        )


def downgrade() -> None:
    op.drop_column("user_profile", "last_active_at")
