#!/usr/bin/env bash
# 同时启动后端和前端（各开一个子进程，共两个终端窗口需手动开）
set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"
echo "项目目录: $ROOT"
echo ""
echo "请开两个终端分别执行："
echo "  终端1 后端:  cd $ROOT && ./start_backend.sh"
echo "  终端2 前端:  cd $ROOT && ./start_frontend.sh"
echo ""
echo "或先在本终端启动后端（后台），再启动前端："
(cd "$ROOT/backend" && uvicorn app.main:app --reload --port 5002 --host 0.0.0.0) &
sleep 3
cd "$ROOT/frontend" && npm run dev
