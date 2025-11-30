
# 基于 Python 3.11 slim 镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 复制整个项目
COPY . .

# 安装后端依赖，使用国内 PyPI 镜像
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --no-cache-dir -r requirements.txt

# 暴露端口
EXPOSE 8000

# 启动 FastAPI 后端
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
