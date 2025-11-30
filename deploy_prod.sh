#!/bin/bash
set -e

REPO_DIR="/volume2/docker/xiaole-ai"
LOGS_DIR="$REPO_DIR/logs"

cd $REPO_DIR

echo "🚀 拉取最新 main"
git fetch origin main
git reset --hard origin/main

echo "🚀 创建 .env"
cp -f .env.example .env
: "${DEEPSEEK_API_KEY:?必须设置 DEEPSEEK_API_KEY 环境变量}"
sed -i "s/DB_HOST=.*/DB_HOST=192.168.88.188/" .env
sed -i "s/USE_CLAUDE=.*/USE_CLAUDE=false/" .env
sed -i "s/DEEPSEEK_API_KEY=.*/DEEPSEEK_API_KEY=${DEEPSEEK_API_KEY}/" .env

mkdir -p $LOGS_DIR

echo "🚀 构建镜像"
docker build -t xiaole-ai:prod .

echo "🚀 启动小乐容器"
docker rm -f xiaole-ai 2>/dev/null || true
docker run -d --name xiaole-ai \
  --restart=always \
  -p 127.0.0.1:8080:80 -p 127.0.0.1:8000:8000 \
  -v $LOGS_DIR:/app/logs \
  --env-file .env \
  xiaole-ai:prod

echo "✅ 小乐容器启动完成（本地 8080 / 8000）"
