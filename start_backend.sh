#!/usr/bin/env bash
# 启动后端（端口 5002）
cd "$(dirname "$0")/backend"
echo "正在启动后端 http://0.0.0.0:5002 ..."
exec uvicorn app.main:app --reload --port 5002 --host 0.0.0.0
