#!/usr/bin/env bash
#
# 数据库迁移便捷脚本
#
# 用法：
#   ./scripts/db-migrate.sh generate "添加xx字段"   # 自动生成迁移脚本
#   ./scripts/db-migrate.sh upgrade                 # 执行迁移到最新版本
#   ./scripts/db-migrate.sh downgrade               # 回退一个版本
#   ./scripts/db-migrate.sh history                 # 查看迁移历史
#   ./scripts/db-migrate.sh current                 # 查看当前版本
#   ./scripts/db-migrate.sh init                    # 对已有数据库标记为已迁移
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/../backend"

cd "$BACKEND_DIR"

ACTION="${1:-help}"
MESSAGE="${2:-}"

case "$ACTION" in
    generate|gen)
        if [[ -z "$MESSAGE" ]]; then
            echo "用法: $0 generate \"迁移描述\""
            exit 1
        fi
        alembic revision --autogenerate -m "$MESSAGE"
        echo "迁移脚本已生成，请检查 alembic/versions/ 目录下的新文件"
        ;;
    upgrade|up)
        TARGET="${MESSAGE:-head}"
        alembic upgrade "$TARGET"
        echo "迁移完成: $TARGET"
        ;;
    downgrade|down)
        TARGET="${MESSAGE:--1}"
        alembic downgrade "$TARGET"
        echo "回退完成: $TARGET"
        ;;
    history)
        alembic history --verbose
        ;;
    current)
        alembic current
        ;;
    init)
        # 对已有数据库（已通过 create_all 创建表）标记为最新迁移版本
        alembic stamp head
        echo "已将当前数据库标记为最新迁移版本"
        ;;
    help|*)
        echo "数据库迁移工具"
        echo ""
        echo "用法: $0 <action> [args]"
        echo ""
        echo "  generate \"描述\"   自动生成迁移脚本（对比 model 与数据库差异）"
        echo "  upgrade [版本]    执行迁移（默认到最新 head）"
        echo "  downgrade [版本]  回退迁移（默认回退 1 步）"
        echo "  history           查看迁移历史"
        echo "  current           查看当前数据库迁移版本"
        echo "  init              对已有数据库标记为已迁移（首次引入 Alembic 时使用）"
        ;;
esac
