# 基于 Python 3.11 slim 镜像
FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive

# 安装 dlib 依赖（简化、适配 Debian Trixie）
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

# 复制项目
COPY . .

# 安装 Python 依赖
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --no-cache-dir -r requirements.txt

# 添加执行权限
RUN chmod +x start_services.sh

# 暴露端口
EXPOSE 8000 9000

# 启动服务
CMD ["bash", "start_services.sh"]
