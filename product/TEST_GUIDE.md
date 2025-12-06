# 小乐AI - API测试指南

## 📋 测试前准备

确保服务正在运行：
```bash
uvicorn main:app --reload
```

## 🔥 测试方法

### 方法1️⃣: 浏览器测试（最简单）

直接在浏览器打开：
- **Swagger文档**: http://localhost:8000/docs
- **首页**: http://localhost:8000/

在 `/docs` 页面可以直接点击测试所有API！

### 方法2️⃣: Python测试脚本

```bash
# 安装requests库（如果还没装）
pip install requests

# 运行测试
python test_api.py
```

### 方法3️⃣: curl命令行测试

```bash
# 1. 测试首页
curl http://localhost:8000/

# 2. 测试思考功能
curl -X POST "http://localhost:8000/think?prompt=你好，小乐"

# 3. 执行任务（会保存到记忆）
curl -X POST "http://localhost:8000/act?command=记住我喜欢编程"

# 4. 查看记忆
curl "http://localhost:8000/memory?tag=task"

# 5. 查看general标签的记忆
curl "http://localhost:8000/memory?tag=general"
```

### 方法4️⃣: 使用测试脚本

```bash
# 运行bash脚本（需要安装jq）
./test_simple.sh
```

## 📝 API端点说明

### GET /
- **功能**: 欢迎信息
- **示例**: `curl http://localhost:8000/`

### POST /think
- **功能**: AI思考（返回简单回复）
- **参数**: `prompt` (字符串)
- **示例**: `curl -X POST "http://localhost:8000/think?prompt=你好"`

### POST /act
- **功能**: 执行任务并保存到记忆
- **参数**: `command` (字符串)
- **示例**: `curl -X POST "http://localhost:8000/act?command=学习Python"`

### GET /memory
- **功能**: 查看指定标签的记忆
- **参数**: `tag` (字符串, 默认"general")
- **示例**: `curl "http://localhost:8000/memory?tag=task"`

## 🎯 测试流程示例

1. **启动服务**
   ```bash
   uvicorn main:app --reload
   ```

2. **打开浏览器访问** http://localhost:8000/docs

3. **测试think接口**
   - 点击 `/think` 
   - 点击 "Try it out"
   - 输入 prompt: "你好，小乐"
   - 点击 "Execute"

4. **测试act接口**
   - 点击 `/act`
   - 点击 "Try it out"
   - 输入 command: "记住我喜欢喝咖啡"
   - 点击 "Execute"

5. **查看记忆**
   - 点击 `/memory`
   - 点击 "Try it out"
   - 输入 tag: "task"
   - 点击 "Execute"

## 🐛 常见问题

### Q: 提示连接失败？
A: 确保服务正在运行 `uvicorn main:app --reload`

### Q: 端口被占用？
A: 修改端口 `uvicorn main:app --reload --port 8001`

### Q: 没有看到记忆？
A: 先使用 `/act` 接口保存一些记忆，然后再查看

## 💡 提示

- Swagger文档（/docs）是最方便的测试方式！
- 所有通过 `/act` 执行的命令都会保存到 `tag=task` 的记忆中
- 数据保存在 `xiaole_ai.db` SQLite数据库文件中
