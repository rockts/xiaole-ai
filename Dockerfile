# 基于 Python 3.11 slim 镜像
FROM python:3.11-slim

# 设置非交互模式
ENV DEBIAN_FRONTEND=noninteractive

# 安装构建 dlib 所需依赖
RUN apt-get update && apt-get install -y \
    cmake \
    build-essential \
    libboost-all-dev \
    libopenblas-dev \
    libatlas-base-dev \
    libgtk-3-dev \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制整个项目
COPY . .

# 安装 Python 依赖（使用清华镜像）
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --no-cache-dir -r requirements.txt

# 暴露端口
EXPOSE 8000

# 启动 FastAPI 后端
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
