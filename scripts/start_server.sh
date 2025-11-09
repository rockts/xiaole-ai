#!/bin/bash
# 启动小乐AI服务器

echo "🚀 正在启动小乐AI服务器..."
cd /Users/rockts/Dev/xiaole-ai
/Users/rockts/Dev/xiaole-ai/.venv/bin/uvicorn main:app --reload --host 0.0.0.0 --port 8000
