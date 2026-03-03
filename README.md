# 智能报价系统

## 项目简介

智能报价系统是一个用于设备匹配和自动报价的工具，它可以：
- 智能识别Excel表格中的设备信息
- 匹配设备型号和厂商
- 生成设备报价单

## 目录结构

```
├── backend/            # 后端服务目录
├── frontend/           # 前端服务目录
├── start.sh            # 全系统启动脚本
├── stop.sh             # 停止所有服务脚本
├── start_backend.sh    # 仅启动后端服务脚本
├── start_frontend.sh   # 仅启动前端服务脚本
├── DOCKER_DEPLOYMENT.md # Docker 部署方式讨论与方案选择
└── README.md           # 使用说明
```

- **Docker 部署与 GitHub / CI/CD**：使用 Docker 开发、部署到 GitHub、版本与回滚及后续 CI/CD 自动化，请阅读 [docs/DOCKER_GITHUB_CICD.md](docs/DOCKER_GITHUB_CICD.md)。  
- 部署方式选型（单机 Compose、仅后端容器化、数据库外置等）可参考 [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md)。

## 快速启动

### 使用 Docker 启动（推荐）

```bash
cp .env.example .env
# 编辑 .env 设置 POSTGRES_PASSWORD、JWT_SECRET_KEY 等（生产必改）
docker compose up -d
```

访问前端：<http://localhost:80>（端口可在 `.env` 的 `FRONTEND_PORT` 修改）。生产部署与版本回滚见 [docs/DOCKER_GITHUB_CICD.md](docs/DOCKER_GITHUB_CICD.md)。

### 本地开发启动（非 Docker）
使用以下命令启动整个系统（前端+后端）：

```bash
./start.sh
```

该脚本会自动:
1. 检查是否有已运行的服务
2. 启动后端API服务 (端口5001)
3. 启动前端开发服务器 (端口3006)

### 单独启动服务

如果只需启动后端或前端，可以使用以下命令：

**仅启动后端**
```bash
./start_backend.sh
```
- 自动检测并停止占用5001端口的进程
- 启动后端API服务（非后台运行，便于观察日志）

**仅启动前端**
```bash
./start_frontend.sh
```
- 自动检测并停止已运行的前端服务
- 检查依赖是否已安装
- 启动前端开发服务器

### 停止服务
使用以下命令停止所有服务：

```bash
./stop.sh
```

## 服务访问

启动后，可以通过以下地址访问：
- 前端页面: http://localhost:3008（新版入口带路径 `/new`，如 http://localhost:3008/new）
- 后端API: http://localhost:5002

## 手动启动服务（推荐顺序）

**必须先启动后端，再启动前端**，否则前端会出现 Network Error / 连接超时。

### 1. 启动后端（端口 5002）

```bash
cd backend
# 使用当前要运行 uvicorn 的 Python 安装依赖（避免 No module named 'jose'）
pip install -r requirements.txt
# 或：python3 -m pip install -r requirements.txt

# 如有虚拟环境先激活
# source venv/bin/activate   # Linux/Mac
# venv\Scripts\activate      # Windows

uvicorn app.main:app --reload --port 5002 --host 0.0.0.0
```

### 2. 启动前端（端口 3008）

```bash
cd frontend
npm run dev
```

开发环境下，前端已配置为通过 Vite 代理访问后端（`/api` → `http://localhost:5002`），请求会发往当前页面域名，由 dev server 转发，避免浏览器直连 5002 超时。修改 `frontend/.env.development` 后需重启前端生效。

## 常见问题

1. **Network Error / ERR_CONNECTION_TIMED_OUT（后台数据全部连接报错）**
   - **先确认后端已启动**：在终端执行 `cd backend && uvicorn app.main:app --reload --port 5002 --host 0.0.0.0`，看到 "Uvicorn running on ..." 后再访问前端。
   - 前端开发时使用代理：确保存在 `frontend/.env.development` 且含 `VITE_API_BASE_URL=/api`，然后重启前端（`npm run dev`）。
   - 用浏览器访问 http://localhost:5002/ 若打不开，说明后端未运行或端口被占。

2. **端口被占用**
   - 后端 5002、前端 3008 若被占用，可结束占用进程或修改对应配置中的端口。

3. **无法连接到后端**
   - 确保先启动后端再访问前端
   - 检查前端的 API 配置（开发环境使用 `frontend/.env.development` 中的 `VITE_API_BASE_URL`）

4. **ModuleNotFoundError: No module named 'jose'**
   - 说明当前用来运行 uvicorn 的 Python 环境里没有安装后端依赖。请在 `backend` 目录下用**同一个 Python** 安装依赖后再启动，例如：
     - `pip install -r requirements.txt`（若 `pip` 对应的是你用来运行 uvicorn 的 Python）
     - 或 `python3 -m pip install -r requirements.txt`（若用 `python3` 启动 uvicorn，则用 `python3 -m pip`）
   - 若系统里同时有多个 Python（如 Homebrew 3.11 与 Anaconda 3.12），务必用**运行 uvicorn 的那一个**执行上述安装。

4. **搜索功能不工作**
   - 确保后端已启动，可用 `curl 'http://localhost:5002/devices/search/?model=关键词'` 测试
   - 查看浏览器控制台与后端终端日志