#!/usr/bin/env bash
#
# 智能报价系统 - 一键部署脚本
#
# 用法：
#   ./scripts/deploy.sh staging          # 部署到测试环境（使用 latest 镜像）
#   ./scripts/deploy.sh production       # 部署到正式环境（需指定版本号）
#   ./scripts/deploy.sh production v1.2.0  # 部署指定版本到正式环境
#   ./scripts/deploy.sh rollback v1.1.0    # 回滚到指定版本
#
# 前提：
#   - 目标机器已安装 Docker 和 Docker Compose
#   - 项目目录下已有 .env 文件（或 environments/.env.<env>）
#   - 已登录 GHCR：docker login ghcr.io
set -euo pipefail

# ─── 配置 ───────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
COMPOSE_BASE="$PROJECT_DIR/docker-compose.yml"
COMPOSE_PROD="$PROJECT_DIR/docker-compose.prod.yml"
ENVS_DIR="$PROJECT_DIR/environments"
BACKUP_DIR="$PROJECT_DIR/backups"
HEALTH_URL="http://localhost:${FRONTEND_PORT:-80}/health"
HEALTH_RETRIES=30
HEALTH_INTERVAL=2

# ─── 颜色输出 ───────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info()  { echo -e "${BLUE}[INFO]${NC}  $*"; }
log_ok()    { echo -e "${GREEN}[OK]${NC}    $*"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
log_error() { echo -e "${RED}[ERROR]${NC} $*"; }

# ─── 参数解析 ───────────────────────────────────────────
ENV="${1:-}"
VERSION="${2:-}"

usage() {
    echo "用法: $0 <environment> [version]"
    echo ""
    echo "  environment:  staging | production | rollback"
    echo "  version:      镜像版本标签 (如 v1.0.0, sha-abc1234)"
    echo ""
    echo "示例:"
    echo "  $0 staging              # 部署 latest 到测试环境"
    echo "  $0 production v1.2.0    # 部署 v1.2.0 到正式环境"
    echo "  $0 rollback v1.1.0      # 回滚到 v1.1.0"
    exit 1
}

if [[ -z "$ENV" ]]; then
    usage
fi

# ─── 环境检查 ───────────────────────────────────────────
check_prerequisites() {
    log_info "检查部署环境..."

    if ! command -v docker &>/dev/null; then
        log_error "未找到 docker 命令，请先安装 Docker"
        exit 1
    fi

    if ! docker compose version &>/dev/null; then
        log_error "未找到 docker compose，请升级 Docker 或安装 compose 插件"
        exit 1
    fi

    if [[ ! -f "$COMPOSE_BASE" ]]; then
        log_error "未找到 $COMPOSE_BASE"
        exit 1
    fi

    if [[ ! -f "$COMPOSE_PROD" ]]; then
        log_error "未找到 $COMPOSE_PROD"
        exit 1
    fi

    log_ok "环境检查通过"
}

# ─── 加载环境配置 ─────────────────────────────────────────
load_env() {
    local env_name="$1"
    local env_file="$ENVS_DIR/.env.$env_name"

    # 优先使用 environments/ 下的环境文件，其次用项目根目录的 .env
    if [[ -f "$env_file" ]]; then
        log_info "加载环境配置: $env_file"
        # 复制到项目根目录供 docker compose 读取
        cp "$env_file" "$PROJECT_DIR/.env"
    elif [[ -f "$PROJECT_DIR/.env" ]]; then
        log_warn "未找到 $env_file，使用项目根目录 .env"
    else
        log_error "未找到任何 .env 文件，请先配置环境变量"
        exit 1
    fi
}

# ─── 获取当前运行的镜像版本 ──────────────────────────────────
get_current_version() {
    local current
    current=$(docker inspect AI_Quote_Backend --format '{{.Config.Image}}' 2>/dev/null | grep -oP ':\K.*$' || echo "none")
    echo "$current"
}

# ─── 数据库备份 ──────────────────────────────────────────
backup_database() {
    log_info "备份数据库..."
    mkdir -p "$BACKUP_DIR"

    local timestamp
    timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_file="$BACKUP_DIR/db_backup_${timestamp}.sql"

    if docker ps --format '{{.Names}}' | grep -q 'AI_Quote_DB'; then
        # 从 .env 读取数据库配置
        local db_user db_name
        db_user=$(grep -E '^POSTGRES_USER=' "$PROJECT_DIR/.env" 2>/dev/null | cut -d= -f2 || echo "device_inventory_user")
        db_name=$(grep -E '^POSTGRES_DB=' "$PROJECT_DIR/.env" 2>/dev/null | cut -d= -f2 || echo "device_inventory_ai_quote_test")

        if docker exec AI_Quote_DB pg_dump -U "$db_user" "$db_name" > "$backup_file" 2>/dev/null; then
            log_ok "数据库备份完成: $backup_file"
            # 保留最近 10 个备份
            ls -t "$BACKUP_DIR"/db_backup_*.sql 2>/dev/null | tail -n +11 | xargs rm -f 2>/dev/null || true
        else
            log_warn "数据库备份失败（数据库可能未运行），继续部署..."
        fi
    else
        log_warn "数据库容器未运行，跳过备份"
    fi
}

# ─── 拉取镜像 ────────────────────────────────────────────
pull_images() {
    local tag="$1"
    log_info "拉取镜像 (版本: $tag)..."

    export IMAGE_TAG="$tag"
    docker compose -f "$COMPOSE_BASE" -f "$COMPOSE_PROD" pull backend frontend

    log_ok "镜像拉取完成"
}

# ─── 启动服务 ────────────────────────────────────────────
start_services() {
    local tag="$1"
    log_info "启动服务 (版本: $tag)..."

    export IMAGE_TAG="$tag"
    docker compose -f "$COMPOSE_BASE" -f "$COMPOSE_PROD" up -d

    log_ok "服务启动命令已执行"
}

# ─── 健康检查 ────────────────────────────────────────────
health_check() {
    log_info "执行健康检查 ($HEALTH_URL)..."

    for i in $(seq 1 $HEALTH_RETRIES); do
        if curl -sf "$HEALTH_URL" >/dev/null 2>&1; then
            log_ok "健康检查通过 (第 ${i} 次尝试)"
            return 0
        fi
        echo -n "."
        sleep $HEALTH_INTERVAL
    done

    echo ""
    log_error "健康检查失败（已重试 $HEALTH_RETRIES 次）"
    return 1
}

# ─── 回滚 ────────────────────────────────────────────────
rollback() {
    local target_version="$1"
    log_warn "回滚到版本: $target_version"
    pull_images "$target_version"
    start_services "$target_version"
    if health_check; then
        log_ok "回滚成功: $target_version"
    else
        log_error "回滚后健康检查仍然失败，请手动排查"
        docker compose -f "$COMPOSE_BASE" -f "$COMPOSE_PROD" logs --tail=50
        exit 1
    fi
}

# ─── 显示部署状态 ──────────────────────────────────────────
show_status() {
    echo ""
    log_info "当前服务状态:"
    docker compose -f "$COMPOSE_BASE" -f "$COMPOSE_PROD" ps
    echo ""
    log_info "后端镜像: $(docker inspect ai-quote-backend --format '{{.Config.Image}}' 2>/dev/null || echo 'N/A')"
    log_info "前端镜像: $(docker inspect ai-quote-frontend --format '{{.Config.Image}}' 2>/dev/null || echo 'N/A')"
}

# ─── 主流程 ──────────────────────────────────────────────
main() {
    echo "========================================"
    echo "  智能报价系统 - 部署工具"
    echo "========================================"
    echo ""

    check_prerequisites

    case "$ENV" in
        staging)
            local tag="${VERSION:-latest}"
            load_env "staging"
            log_info "部署环境: 测试环境 (staging)"
            log_info "镜像版本: $tag"
            echo ""

            # 记录当前版本，便于回滚
            local prev_version
            prev_version=$(get_current_version)

            backup_database
            pull_images "$tag"
            start_services "$tag"

            if health_check; then
                log_ok "测试环境部署成功!"
                show_status
            else
                log_error "部署失败，尝试回滚..."
                if [[ "$prev_version" != "none" ]]; then
                    rollback "$prev_version"
                else
                    log_error "无历史版本可回滚，请手动排查"
                    docker compose -f "$COMPOSE_BASE" -f "$COMPOSE_PROD" logs --tail=50
                    exit 1
                fi
            fi
            ;;

        production)
            if [[ -z "$VERSION" ]]; then
                log_error "正式环境部署必须指定版本号"
                echo "  用法: $0 production v1.2.0"
                exit 1
            fi

            load_env "production"
            log_info "部署环境: 正式环境 (production)"
            log_info "镜像版本: $VERSION"
            echo ""

            # 二次确认
            echo -e "${YELLOW}即将部署到正式环境，版本: $VERSION${NC}"
            read -rp "确认部署? (yes/no): " confirm
            if [[ "$confirm" != "yes" ]]; then
                log_warn "部署已取消"
                exit 0
            fi

            local prev_version
            prev_version=$(get_current_version)
            log_info "当前版本: $prev_version"

            backup_database
            pull_images "$VERSION"
            start_services "$VERSION"

            if health_check; then
                log_ok "正式环境部署成功! 版本: $VERSION"
                show_status
            else
                log_error "部署失败，自动回滚到: $prev_version"
                if [[ "$prev_version" != "none" ]]; then
                    rollback "$prev_version"
                else
                    log_error "无历史版本可回滚，请手动排查"
                    docker compose -f "$COMPOSE_BASE" -f "$COMPOSE_PROD" logs --tail=50
                    exit 1
                fi
            fi
            ;;

        rollback)
            if [[ -z "$VERSION" ]]; then
                log_error "回滚必须指定目标版本号"
                echo "  用法: $0 rollback v1.1.0"
                exit 1
            fi

            load_env "production"
            rollback "$VERSION"
            show_status
            ;;

        *)
            log_error "未知环境: $ENV"
            usage
            ;;
    esac
}

main
