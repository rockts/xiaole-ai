# ============================================
# Stage 1: 构建前端
# ============================================
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

# 复制前端依赖文件
COPY frontend/package*.json ./

# 安装依赖
RUN npm ci

# 复制前端源码
COPY frontend/ ./

# 构建前端
RUN npm run build

# ============================================
# Stage 2: Python 后端 + 前端静态文件
# ============================================
FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    cmake \
    build-essential \
    libboost-all-dev \
    libopenblas-dev \
    libgtk-3-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# 工作目录
WORKDIR /app

# 复制后端代码
COPY backend/ ./backend/
COPY tools/ ./tools/
COPY scripts/ ./scripts/
COPY requirements.txt ./
COPY start_services.sh ./
COPY webhook_deploy.py ./

# 复制前端构建产物(从 frontend-builder stage)
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# 安装 Python 依赖
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --no-cache-dir -r requirements.txt

# 添加执行权限
RUN chmod +x start_services.sh

# 暴露端口
EXPOSE 8000 9000

# 启动服务
CMD ["bash", "start_services.sh"]
