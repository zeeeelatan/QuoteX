# 智能报价系统 - 前端 (Vue3 + Vite) 多阶段构建：Node 构建 + nginx 提供静态与 API 代理
# 构建阶段：需传入 VITE_API_BASE_URL（生产建议 /api），可选 VITE_BAIDU_MAP_AK
ARG NODE_VERSION=20
FROM node:${NODE_VERSION}-alpine AS builder

WORKDIR /app

# 国内镜像加速（阿里云）：Alpine apk 源 + npm 源
RUN sed -i 's|dl-cdn.alpinelinux.org|mirrors.aliyun.com|g' /etc/apk/repositories

COPY package.json package-lock.json* ./
RUN npm ci --registry=https://registry.npmmirror.com

COPY . .

# 构建时注入：浏览器请求 API 的基地址（与 nginx 代理一致用 /api）
ARG VITE_API_BASE_URL=/api
ARG VITE_BAIDU_MAP_AK=
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}
ENV VITE_BAIDU_MAP_AK=${VITE_BAIDU_MAP_AK}

RUN npm run build

# 运行阶段：nginx 提供静态文件并代理 /api 到后端
FROM nginx:alpine

# nginx 容器也使用国内源
RUN sed -i 's|dl-cdn.alpinelinux.org|mirrors.aliyun.com|g' /etc/apk/repositories

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
