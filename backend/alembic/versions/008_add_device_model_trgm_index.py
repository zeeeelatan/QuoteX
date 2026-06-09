"""add pg_trgm extension + GiST trigram index on device_inventory.model_number

把设备型号匹配的「召回」下推到数据库：用 pg_trgm 的 GiST trigram 索引做
KNN 近邻召回（ORDER BY lower(model_number) <-> lower(:q) LIMIT K），将模糊
匹配的候选集从全表 9.5 万行缩小到 top-K，单次匹配从 ~750ms 降到 ~10ms。

索引建在 lower(model_number) 表达式上，保证大小写无关。

幂等：CREATE EXTENSION / INDEX IF NOT EXISTS。pg_trgm 为 trusted extension，
普通用户在有 CREATE 权限的库内即可安装；若环境不允许，应用层会自动退回
全量匹配（见 matching._recall_candidates 的异常兜底）。

Revision ID: 008
Revises: 007
Create Date: 2026-06-09
"""
from alembic import op
import sqlalchemy as sa

revision = "008"
down_revision = "007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_dev_model_trgm_gist "
        "ON device_inventory USING gist (lower(model_number) gist_trgm_ops)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_dev_model_trgm_gist")
    # 不删除 pg_trgm 扩展：可能被其他对象依赖
