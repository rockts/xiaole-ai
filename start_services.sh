#!/bin/bash
# 在容器内同时启动 FastAPI 和 Webhook 服务

# 启动 webhook 服务(后台)
python webhook_deploy.py &

# 启动 FastAPI 服务(前台)
exec uvicorn backend.main:app --host 0.0.0.0 --port 8000
