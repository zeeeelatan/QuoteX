# Docker + GitHub + CI/CD 指南

本文说明如何将智能报价系统通过 Docker 部署到 GitHub，并实现基于镜像的版本管理与回滚，以及后续可扩展的 CI/CD 自动化运维与发布。

---

## 一、仓库与首次推送

### 1. 初始化 Git 并推送到 GitHub

在项目根目录执行：

```bash
git init
git add .
git commit -m "chore: Docker + CI/CD 初版"
git branch -M main
git remote add origin https://github.com/你的用户名/你的仓库名.git
git push -u origin main
```

- 若仓库已存在且非空，可先 `git pull origin main --rebase` 再 push。
- 推送前请确认已复制 `.env.example` 为 `.env` 并修改敏感项；`.env` 已被 `.gitignore` 忽略，不会提交。

### 2. 本地使用 Docker 开发（不依赖 GitHub）

不推代码也可在本地用 Docker 跑全栈：

```bash
cp .env.example .env
# 编辑 .env，至少设置 POSTGRES_PASSWORD、JWT_SECRET_KEY（生产必改）
docker compose up -d
```

- 前端：<http://localhost:80>（或 `.env` 中 `FRONTEND_PORT`）
- 后端健康检查：<http://localhost:80/api/health>（经 nginx 代理）

仅构建不拉镜像，使用当前代码；适合日常开发与联调。

---

## 二、CI/CD 流程说明

### 1. 触发方式

| 事件 | 行为 |
|------|------|
| 推送到 `main` / `master` | 构建 backend、frontend 镜像并推送到 GitHub Container Registry (GHCR)，打 tag：`sha-<短 SHA>`、`latest` |
| 创建 Release 并发布 | 使用 Release 的 tag（如 `v1.0.0`）构建并推送镜像 |
| Pull Request | 仅构建与测试，不推送镜像 |

### 2. 镜像命名

- 后端：`ghcr.io/<你的 GitHub 用户名或组织>/ai-quote-backend:<tag>`
- 前端：`ghcr.io/<你的 GitHub 用户名或组织>/ai-quote-frontend:<tag>`

示例：用户名为 `mycompany` 时，镜像为  
`ghcr.io/mycompany/ai-quote-backend:latest`、  
`ghcr.io/mycompany/ai-quote-frontend:v1.0.0`。

### 3. 查看与拉取镜像

- 在 GitHub 仓库页面：**Packages** 中可看到 `ai-quote-backend`、`ai-quote-frontend`。
- 拉取（需登录）：

```bash
echo $GITHUB_TOKEN | docker login ghcr.io -u 你的用户名 --password-stdin
docker pull ghcr.io/你的用户名/ai-quote-backend:latest
docker pull ghcr.io/你的用户名/ai-quote-frontend:latest
```

---

## 三、生产部署与版本管理

### 1. 使用“已构建镜像”部署（推荐）

生产环境使用 CI 已推送到 GHCR 的镜像，不在此机器上构建：

```bash
# 1. 配置环境变量（至少设置密码与密钥，以及镜像地址与版本）
cp .env.example .env
# 编辑 .env，设置：
#   POSTGRES_PASSWORD=强密码
#   JWT_SECRET_KEY=强随机密钥
#   GHCR_IMAGE_BACKEND=ghcr.io/你的用户名/ai-quote-backend
#   GHCR_IMAGE_FRONTEND=ghcr.io/你的用户名/ai-quote-frontend
#   IMAGE_TAG=v1.0.0   # 或 sha-abc1234、latest

# 2. 使用“基础 compose + 生产 override”启动
IMAGE_TAG=v1.0.0 docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

- `docker-compose.yml`：提供 postgres、网络与卷等基础定义。
- `docker-compose.prod.yml`：将 backend、frontend 改为使用 `image`（来自 GHCR），不再本地 build。
- 数据库仍由 compose 中的 postgres 服务提供；若改用外置数据库，需修改 `backend` 的 `DB_*` 或 `DATABASE_URL`，并可按需从 compose 中去掉 postgres 服务。

### 2. 版本与回滚

- **版本**：每次推 main 或发布 Release 后，CI 会打出新 tag（如 `sha-abc1234`、`v1.0.0`）。部署时通过 `IMAGE_TAG` 指定要跑的版本。
- **回滚**：将 `IMAGE_TAG` 改为上一版本（或任意历史 tag），重新执行 `up -d` 即可。

```bash
# 当前为 v1.0.1，要回滚到 v1.0.0
export IMAGE_TAG=v1.0.0
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

- 建议：重要发布前在 GitHub 打 Release（如 `v1.0.0`），部署与回滚都使用 Release tag，便于审计。

---

## 四、后续可扩展的 CI/CD 体系

当前已具备：

- 代码推送 / Release 触发构建
- 自动构建并推送 backend、frontend 镜像到 GHCR
- 基于 tag 的版本与回滚

后续可在此基础上扩展：

1. **自动化测试**：在 CI 中增加 `pytest`、前端单元测试/ E2E，未通过则禁止合并或打 release。
2. **安全扫描**：在 workflow 中加入镜像漏洞扫描（如 Trivy）、依赖检查。
3. **自动部署**：在 `main` 或 Release 后，通过 SSH 或 K8s 在目标服务器执行拉取镜像 + `docker compose ... up -d`（需在 repo 中配置 secrets，如 `DEPLOY_HOST`、`SSH_KEY`）。
4. **多环境**：通过不同 compose 或 env 文件区分 staging / production，CI 按分支或 tag 部署到对应环境。
5. **通知与审计**：在 workflow 中增加 Slack/钉钉/邮件通知，并保留“谁在何时部署了哪个 tag”的记录。

以上均可通过在同一 `.github/workflows/ci-cd.yml` 中增加 job 或新 workflow 文件实现，无需改变当前 Docker 与 compose 结构。

---

## 五、文件与配置速查

| 文件 | 用途 |
|------|------|
| `docker-compose.yml` | 本地/开发：postgres + 本地 build 的 backend、frontend |
| `docker-compose.prod.yml` | 生产：backend、frontend 使用 GHCR 镜像，版本由 `IMAGE_TAG` 控制 |
| `.env.example` | 环境变量模板；复制为 `.env` 并修改后使用 |
| `.github/workflows/ci-cd.yml` | CI：构建、测试、推送镜像到 GHCR |
| `backend/Dockerfile` | 后端镜像构建 |
| `frontend/Dockerfile` | 前端镜像构建（多阶段：Node 构建 + nginx） |
| `backend/app/main.py` 中 `/health` | 健康检查，供负载均衡/编排使用 |

---

## 六、常见问题

1. **GHCR 镜像拉取 404 / 未授权**  
   镜像为私有时，需在服务器上对 `ghcr.io` 做 `docker login`（使用 PAT 或 GITHUB_TOKEN），并将仓库 Package 权限授予该账号。

2. **生产 compose 仍在使用本地构建**  
   确保使用：`docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d`，且 `.env` 中已设置 `GHCR_IMAGE_BACKEND`、`GHCR_IMAGE_FRONTEND`、`IMAGE_TAG`。

3. **回滚后数据不一致**  
   回滚只替换 backend/frontend 镜像，数据库（postgres 卷）未变；若数据库 schema 或迁移不兼容旧版本，需在发布流程中考虑迁移与回滚策略。

4. **想改用自建 Registry**  
   在 CI 中把 `REGISTRY` 和镜像前缀改为自建地址，并在 `docker-compose.prod.yml` 的 `GHCR_IMAGE_*` 中写完整镜像名即可。
