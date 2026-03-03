#!/usr/bin/env bash
# 启动前端（端口 3008）
cd "$(dirname "$0")/frontend"
echo "正在启动前端 http://localhost:3008 ..."
exec npm run dev
