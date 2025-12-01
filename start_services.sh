#!/bin/bash
# 在容器内启动 FastAPI 服务

# 禁用 Python 输出缓冲
export PYTHONUNBUFFERED=1

# 启动 FastAPI 服务(前台)
exec uvicorn backend.main:app --host 0.0.0.0 --port 8000
