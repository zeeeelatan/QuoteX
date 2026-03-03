# Docker 部署方式讨论

在不编写具体 Docker 文件的前提下，先厘清「怎么用 Docker 部署」以及「有哪几种做法」，便于选定最终方案后再实施。

---

## 一、系统组成回顾

- **前端**：Vue3 + Vite，构建后为静态资源，需 Web 服务器（或 dev server）。
- **后端**：FastAPI + Uvicorn，端口 5002，依赖 PostgreSQL。
- **数据库**：PostgreSQL，需持久化数据。
- **可选**：Ollama（大模型），可同机或独立部署。

---

## 二、Docker 部署的几种方式

### 方式 A：单机 Compose 全栈（推荐作为首选讨论）

**做法**：一个 `docker-compose.yml` 在同一台机器上起 4 个服务（或 3 个不含 Ollama）：

- **postgres**：官方镜像，挂载卷做数据持久化。
- **backend**：自建镜像（Dockerfile 基于 Python，装依赖、跑 uvicorn）。
- **frontend**：自建镜像，多阶段构建（Node 构建 + nginx 提供静态并反向代理 `/api` 到 backend）。
- **ollama**（可选）：官方镜像，用 `profiles` 或单独 compose 文件按需启动。

用户只访问前端端口（如 80），nginx 负责静态 + API 代理，后端不直接对外。

**优点**：一键启停、网络与依赖清晰、易复现、适合内网/单机/中小部署。  
**缺点**：单机资源上限；Ollama 吃内存/显存，可按需关掉或放别的机器。

---

### 方式 B：仅容器化后端 + 数据库，前端不容器化

**做法**：Compose 只起 **postgres** 和 **backend**。前端在宿主机用 `npm run build` 构建，静态文件由现有 Nginx/IIS 等提供，或直接 `npm run dev` 开发时连容器内后端。

**优点**：前端改版无需重做镜像，调试方便；后端与 DB 环境一致。  
**缺点**：交付物不「全在 Docker」；生产环境要自己管前端部署与 API 代理。

---

### 方式 C：前后端分别做镜像，不统一入口

**做法**：

- 后端镜像 + Postgres（Compose 或单独跑）。
- 前端镜像只做「构建阶段」产出 `dist`，运行时用宿主机 Nginx 挂载 `dist` 或把 `dist` 拷到已有 Web 服务器。
- 或前端也做成带 nginx 的镜像，但对外暴露两个端口（例如 80 给前端、5002 给后端），由前置 Nginx/负载均衡做路由。

**优点**：前后端可独立发版、扩展。  
**缺点**：要处理 CORS 或统一反向代理；浏览器请求需能访问后端或通过同一域名转发（否则要改 `VITE_API_BASE_URL`）。

---

### 方式 D：数据库不在 Docker 内

**做法**：Compose 只起 **backend**（+ 可选 **frontend**、**ollama**）。PostgreSQL 使用公司已有实例或 RDS，通过 `DB_HOST` / `DATABASE_URL` 指过去。

**优点**：数据库由 DBA/云厂商管，备份、高可用更成熟。  
**缺点**：依赖外网或专线连通；需提前建库、账号与白名单。

---

### 方式 E：生产环境多机 / K8s

**做法**：镜像与 Compose 仍可沿用，但部署到多台机或 Kubernetes：Postgres 可迁到云 RDS；backend/frontend 多副本 + Ingress/负载均衡。

**优点**：高可用、弹性伸缩。  
**缺点**：运维与配置复杂度高，一般在本系统「先能跑起来」之后再考虑。

---

## 三、方案对比小结

| 方式 | 适用场景 | 复杂度 | 前端在容器内 | 数据库在容器内 |
|------|----------|--------|----------------|------------------|
| A. Compose 全栈 | 内网/单机/演示/中小部署 | 低 | 是（nginx） | 是 |
| B. 仅后端+DB 容器化 | 前端习惯在宿主机部署 | 低 | 否 | 是 |
| C. 前后端分离镜像 | 需独立发版、多端口或前置网关 | 中 | 可选 | 可选 |
| D. 数据库外置 | 已有 PG 或云 RDS | 低 | 可选 | 否 |
| E. 多机/K8s | 生产高可用、扩容 | 高 | 可选 | 常外置 |

---

## 四、推荐讨论路径（确定最终方案）

1. **是否「一键全栈」**
   - 若是 → 倾向 **方式 A**（Compose 含 postgres + backend + frontend，Ollama 可选）。
   - 若否 → 在 B/C 中选：要简单就 B，要前后端独立镜像就 C。

2. **数据库是否用 Docker 里的 Postgres**
   - 是 → 方式 A/B 的默认。
   - 否 → 采用 **方式 D**，Compose 不启 postgres，只配 `DB_HOST`/`DATABASE_URL`。

3. **Ollama 是否同机**
   - 同机 → Compose 加 ollama 服务（profile 或单独文件），backend 用服务名连。
   - 不同机/宿主机已有 → 不启 ollama 容器，只设 `OLLAMA_BASE_URL` 指向外部。

4. **前端 API 地址**
   - 若采用「nginx 反向代理 /api」（方式 A 或 C 中 nginx 镜像）：构建时 `VITE_API_BASE_URL=/api`，浏览器同源。
   - 若前端直连后端域名/端口：构建时填完整后端地址（如 `https://api.xxx.com`）。

确定上述 4 点后，即可定下「最终方案」（例如：A + 数据库在容器内 + Ollama 用 profile 可选），再据此编写具体 Dockerfile 与 docker-compose.yml 并实施。
