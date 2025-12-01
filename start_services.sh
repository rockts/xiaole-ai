#!/bin/bash
# 在容器内同时启动 FastAPI 和 Webhook 服务

# 禁用 Python 输出缓冲
export PYTHONUNBUFFERED=1

# 启动 webhook 服务(后台,输出重定向到 stderr)
python3 webhook_deploy.py 2>&1 &

# 启动 FastAPI 服务(前台)
exec uvicorn backend.main:app --host 0.0.0.0 --port 8000
