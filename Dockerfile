# 基于官方 Node 镜像和 Python 镜像
FROM python:3.11-slim AS backend-build


# 设置工作目录
WORKDIR /app

# 复制整个项目
COPY . .


# 安装编译依赖


RUN echo "deb http://mirrors.aliyun.com/debian/ trixie main contrib non-free" > /etc/apt/sources.list \
 && echo "deb http://mirrors.aliyun.com/debian/ trixie-updates main contrib non-free" >> /etc/apt/sources.list \
  && apt-get update \
   && apt-get install -y build-essential cmake libgtk-3-dev libboost-all-dev \
    && rm -rf /var/lib/apt/lists/*




# 安装后端依赖
#RUN pip install --no-cache-dir -r requirements.txt
# 安装后端依赖，使用国内 PyPI 镜像
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --no-cache-dir -r requirements.txt


# 构建前端
RUN apt-get update && apt-get install -y nodejs npm
RUN cd frontend && npm install && npm run build

# =====================
# 生产镜像
FROM caddy:latest

# 将前端 build 输出复制到 caddy 默认目录
COPY --from=backend-build /app/frontend/dist /srv

# 后端 API 使用 FastAPI，在容器内运行 uvicorn
COPY --from=backend-build /app /app

WORKDIR /app

# 暴露端口
EXPOSE 80 8000

# 启动后端 + Caddy
# 使用后台运行方式，Caddy 负责前端静态，后端通过 uvicorn 启动
CMD bash -c "uvicorn backend.main:app --host 0.0.0.0 --port 8000 & caddy run --config /etc/caddy/Caddyfile"

