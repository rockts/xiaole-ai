# 生产环境部署指南

## 问题分析

### 1. Node 版本问题
**原因**: 
- 终端会话中 nvm 没有自动加载
- 不同终端启动方式导致环境变量丢失

**解决方案**:
- ✅ 已创建 `.nvmrc` 文件锁定版本
- ✅ 已优化 `start.sh` 自动加载 nvm
- ✅ 已创建 `clean-restart.sh` 清理脚本

**生产环境**:
- 使用 Docker 容器固定 Node 版本
- 或使用 PM2 配置固定环境
- 不依赖 nvm,直接安装指定版本 Node

### 2. 前端转圈问题
**原因**:
- 浏览器缓存了旧版本 JavaScript
- Vite 开发服务器有时响应慢

**开发环境解决**:
```bash
# 方法1: 硬刷新
Cmd + Shift + R (macOS)
Ctrl + Shift + R (Windows)

# 方法2: 清理缓存重启
cd frontend
./clean-restart.sh

# 方法3: 清除浏览器缓存
开发者工具 > Application > Clear storage
```

**生产环境**:
- ✅ 构建产物有版本哈希,自动缓存刷新
- ✅ 配置 Service Worker 缓存策略
- ✅ CDN 配置合理的缓存时间

## 生产环境配置

### Docker 部署 (推荐)

```dockerfile
# Dockerfile.frontend
FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=0 /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
```

### PM2 部署

```json
// ecosystem.config.js
module.exports = {
  apps: [{
    name: 'xiaole-frontend',
    script: 'npm',
    args: 'run preview',
    cwd: './frontend',
    interpreter: '/path/to/node20/bin/node',
    env: {
      NODE_ENV: 'production',
      PORT: 3000
    }
  }]
}
```

### Nginx 配置

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    root /var/www/xiaole-ai/dist;
    index index.html;
    
    # 禁用缓存(开发环境)
    # add_header Cache-Control "no-cache, no-store, must-revalidate";
    
    # 生产环境缓存配置
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # API 反向代理
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

## 开发环境最佳实践

### 启动顺序

```bash
# 1. 启动后端
cd backend
source ../.venv/bin/activate
python main.py

# 2. 启动前端(新终端)
cd frontend
./start.sh

# 3. 访问
open http://localhost:3000
```

### 常见问题

#### Q: 前端一直转圈
A: 
1. 硬刷新浏览器 (Cmd+Shift+R)
2. 检查后端是否启动: `lsof -i :8000`
3. 检查浏览器控制台错误
4. 运行 `./clean-restart.sh`

#### Q: Node 版本错误
A:
1. 运行 `nvm use 20`
2. 或使用 `./start.sh` 自动切换

#### Q: 端口被占用
A:
```bash
# 清理端口
lsof -ti :3000 | xargs kill -9

# 重启
./start.sh
```

## 性能监控

生产环境建议添加:
- Sentry 错误追踪
- Google Analytics 用户行为
- 后端响应时间日志(已添加)

## 自动化部署

```bash
# deploy.sh
#!/bin/bash
set -e

echo "🚀 部署小乐 AI..."

# 1. 拉取最新代码
git pull origin main

# 2. 构建前端
cd frontend
npm ci
npm run build

# 3. 重启服务
pm2 restart xiaole-frontend
pm2 restart xiaole-backend

echo "✅ 部署完成"
```
