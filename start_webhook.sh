#!/bin/bash
# Webhook 自动部署服务启动脚本 (群晖 DSM 6.2.3)

cd /volume2/docker/xiaole-ai

# 设置环境变量
export WEBHOOK_SECRET="change-this-to-your-secret"
export DB_USER="your_db_user"
export DB_PASS="your_db_password"
export DEEPSEEK_API_KEY="your_deepseek_api_key"
export QWEN_API_KEY="your_qwen_api_key"
export BAIDU_APP_ID="your_baidu_app_id"
export BAIDU_API_KEY="your_baidu_api_key"
export BAIDU_SECRET_KEY="your_baidu_secret_key"

# 启动服务
nohup python webhook_deploy.py > /var/log/webhook_deploy.log 2>&1 &
echo $! > /var/run/webhook_deploy.pid
echo "✅ Webhook 服务已启动,PID: $(cat /var/run/webhook_deploy.pid)"
echo "📋 查看日志: tail -f /var/log/webhook_deploy.log"
