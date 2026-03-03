#!/usr/bin/env bash
#
# QuoteX 服务器首次部署脚本（Ubuntu）
#
# 功能：
#   1. 安装 Docker + Docker Compose（如未安装）
#   2. 克隆项目代码
#   3. 配置环境变量
#   4. 构建并启动 Docker 容器
#   5. 配置宿主机 nginx 反向代理（与现有 nginx+pm2 架构共存）
#
# 用法（在服务器上执行）：
#   curl -fsSL https://raw.githubusercontent.com/zeeeelatan/QuoteX/main/scripts/server-setup.sh | bash
#   或下载后：
#   chmod +x server-setup.sh && sudo ./server-setup.sh
#
# 前提：
#   - Ubuntu 20.04 / 22.04 / 24.04
#   - 已有 nginx 在运行（现有系统）
#   - 有 sudo 权限
set -euo pipefail

# ─── 配置项（按需修改） ───────────────────────────────────
PROJECT_DIR="/opt/quotex"
REPO_URL="https://github.com/zeeeelatan/QuoteX.git"
DOMAIN="quote.example.com"  # 修改为你的实际子域名
FRONTEND_PORT=8080           # Docker 前端容器映射到宿主机的端口

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

# ─── 检查 root ───────────────────────────────────────────
if [ "$(id -u)" -ne 0 ]; then
    log_error "请使用 sudo 执行此脚本"
    exit 1
fi

echo "========================================"
echo "  QuoteX 服务器部署"
echo "========================================"
echo ""

# ─── Step 1: 安装 Docker ─────────────────────────────────
install_docker() {
    if command -v docker &>/dev/null; then
        log_ok "Docker 已安装: $(docker --version)"
        return
    fi

    log_info "安装 Docker..."
    apt-get update -qq
    apt-get install -y -qq ca-certificates curl gnupg

    # 添加 Docker 官方 GPG key
    install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    chmod a+r /etc/apt/keyrings/docker.gpg

    # 添加 Docker 仓库
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
      $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
      tee /etc/apt/sources.list.d/docker.list > /dev/null

    apt-get update -qq
    apt-get install -y -qq docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

    # 启动 Docker 并设为开机自启
    systemctl enable docker
    systemctl start docker

    log_ok "Docker 安装完成: $(docker --version)"
}

# ─── Step 2: 克隆项目 ─────────────────────────────────────
clone_project() {
    if [ -d "$PROJECT_DIR/.git" ]; then
        log_info "项目目录已存在，拉取最新代码..."
        cd "$PROJECT_DIR"
        git pull origin main
    else
        log_info "克隆项目到 $PROJECT_DIR..."
        git clone "$REPO_URL" "$PROJECT_DIR"
        cd "$PROJECT_DIR"
    fi
    log_ok "代码就绪: $PROJECT_DIR"
}

# ─── Step 3: 配置环境变量 ──────────────────────────────────
setup_env() {
    cd "$PROJECT_DIR"

    if [ -f .env ]; then
        log_warn ".env 文件已存在，跳过生成（如需重新配置请手动编辑）"
        return
    fi

    log_info "生成 .env 配置文件..."

    # 生成随机密码
    DB_PASSWORD=$(openssl rand -base64 24 | tr -dc 'a-zA-Z0-9' | head -c 32)
    JWT_SECRET=$(openssl rand -base64 48 | tr -dc 'a-zA-Z0-9' | head -c 64)

    cat > .env << ENVEOF
# QuoteX 生产环境配置（由 server-setup.sh 自动生成）

# ---------- PostgreSQL ----------
POSTGRES_DB=ai_quote_prod
POSTGRES_USER=ai_quote_user
POSTGRES_PASSWORD=${DB_PASSWORD}

# ---------- 后端 ----------
JWT_SECRET_KEY=${JWT_SECRET}
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_QUOTE_MODEL=qwen:latest

# ---------- 前端 ----------
VITE_API_BASE_URL=/api
VITE_BAIDU_MAP_AK=

# ---------- 端口（宿主机 nginx 反向代理到此端口） ----------
FRONTEND_PORT=${FRONTEND_PORT}

# ---------- 镜像（首次部署用本地构建，后续可切换为 GHCR 镜像） ----------
# IMAGE_TAG=latest
# GHCR_IMAGE_BACKEND=ghcr.io/zeeeelatan/ai-quote-backend
# GHCR_IMAGE_FRONTEND=ghcr.io/zeeeelatan/ai-quote-frontend
ENVEOF

    chmod 600 .env
    log_ok ".env 已生成（密码已随机生成）"
}

# ─── Step 4: 构建并启动 Docker ─────────────────────────────
start_docker() {
    cd "$PROJECT_DIR"
    log_info "构建 Docker 镜像（首次较慢）..."
    docker compose build

    log_info "启动服务..."
    docker compose up -d

    # 等待健康检查
    log_info "等待服务启动..."
    for i in $(seq 1 30); do
        if curl -sf "http://localhost:${FRONTEND_PORT}/health" >/dev/null 2>&1; then
            log_ok "服务启动成功 (第 ${i} 次检查)"
            return
        fi
        sleep 2
    done

    log_error "服务启动超时，检查日志："
    docker compose logs --tail=20
    exit 1
}

# ─── Step 5: 配置宿主机 nginx ──────────────────────────────
setup_nginx() {
    local nginx_conf="/etc/nginx/sites-available/quotex"
    local nginx_link="/etc/nginx/sites-enabled/quotex"

    if [ -f "$nginx_conf" ]; then
        log_warn "nginx 配置 $nginx_conf 已存在，跳过（如需重新配置请手动编辑）"
        return
    fi

    log_info "创建 nginx 反向代理配置..."

    cat > "$nginx_conf" << 'NGINXEOF'
# QuoteX 智能报价系统 - 宿主机 nginx 反向代理
# 将子域名请求转发到 Docker 容器（端口 FRONTEND_PORT）
#
# Docker 容器内的 nginx 负责：
#   - 静态文件服务
#   - /api/ 转发到 FastAPI 后端
# 宿主机 nginx 只做一层透明代理
server {
    listen 80;
    server_name DOMAIN_PLACEHOLDER;

    # 客户端上传文件大小限制（Excel 导入等）
    client_max_body_size 50M;

    location / {
        proxy_pass http://127.0.0.1:FRONTEND_PORT_PLACEHOLDER;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        # 超时设置（报价生成可能较慢）
        proxy_connect_timeout 60s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;
    }

    # 健康检查（可选，供监控使用）
    location /nginx-health {
        access_log off;
        return 200 "ok\n";
        add_header Content-Type text/plain;
    }
}
NGINXEOF

    # 替换占位符
    sed -i "s/DOMAIN_PLACEHOLDER/${DOMAIN}/g" "$nginx_conf"
    sed -i "s/FRONTEND_PORT_PLACEHOLDER/${FRONTEND_PORT}/g" "$nginx_conf"

    # 启用站点
    ln -sf "$nginx_conf" "$nginx_link"

    # 检查 nginx 配置是否正确
    if nginx -t 2>&1; then
        systemctl reload nginx
        log_ok "nginx 配置已生效: ${DOMAIN} → localhost:${FRONTEND_PORT}"
    else
        log_error "nginx 配置语法错误，请手动检查 $nginx_conf"
        rm -f "$nginx_link"
        exit 1
    fi
}

# ─── Step 6: 显示结果 ────────────────────────────────────
show_result() {
    echo ""
    echo "========================================"
    echo "  部署完成!"
    echo "========================================"
    echo ""
    echo "  项目目录:  $PROJECT_DIR"
    echo "  访问地址:  http://${DOMAIN}"
    echo "  默认账号:  admin / admin123"
    echo ""
    echo "  Docker 容器:"
    docker compose -f "$PROJECT_DIR/docker-compose.yml" ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"
    echo ""
    echo "  常用命令:"
    echo "    cd $PROJECT_DIR"
    echo "    docker compose logs -f         # 查看日志"
    echo "    docker compose restart         # 重启服务"
    echo "    docker compose down            # 停止服务"
    echo "    docker compose up -d --build   # 更新代码后重新构建"
    echo ""
    echo "  注意："
    echo "    1. 请将域名 ${DOMAIN} 的 DNS A 记录指向本服务器 IP"
    echo "    2. 建议配置 HTTPS: sudo certbot --nginx -d ${DOMAIN}"
    echo "    3. 修改默认密码: 登录后在「个人设置」中修改"
    echo ""
}

# ─── 主流程 ──────────────────────────────────────────────
main() {
    install_docker
    clone_project
    setup_env
    start_docker
    setup_nginx
    show_result
}

main
