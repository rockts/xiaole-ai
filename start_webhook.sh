#!/bin/bash
# Webhook 自动部署服务启动脚本 (群晖 DSM 6.2.3)

cd /volume2/docker/xiaole-ai

# 设置环境变量
export WEBHOOK_SECRET="change-this-to-your-secret"
export DB_USER="xiaole_user"
export DB_PASS="Xiaole2025User"
export DEEPSEEK_API_KEY="sk-2e77a6c7837b4e0badb17b86fa980098"
export QWEN_API_KEY="sk-69ef2e83e8f44fb58d35911b9ae51091"
export BAIDU_APP_ID="120791683"
export BAIDU_API_KEY="yq6CZ2dqQnGdevtiQgDa1vPW"
export BAIDU_SECRET_KEY="VcDVu97wz506w9TApXWURVkutCtJI49S"

# 启动服务
nohup python webhook_deploy.py > /var/log/webhook_deploy.log 2>&1 &
echo $! > /var/run/webhook_deploy.pid
echo "✅ Webhook 服务已启动,PID: $(cat /var/run/webhook_deploy.pid)"
echo "📋 查看日志: tail -f /var/log/webhook_deploy.log"
