# 小乐 AI 管家

个人 AI 助手，支持长期记忆、对话上下文管理和智能记忆提取。

## 功能特性

✅ **智能记忆管理**
- 自动提取用户告知的关键事实
- 区分事实记忆和闲聊内容
- 支持关键词和标签搜索

✅ **对话上下文管理**
- 多会话支持，记录完整对话历史
- 上下文感知，连贯的对话体验

✅ **远程数据存储**
- 使用 NAS PostgreSQL 存储数据
- 多设备数据同步
- 自动备份机制

✅ **错误处理和重试**
- API 调用自动重试（指数退避）
- 完整的错误日志记录
- 降级处理机制

✅ **Web 界面**
- 支持 Markdown 渲染
- 会话管理和记忆查看
- 实时对话体验

## 技术栈

- **后端**: FastAPI + SQLAlchemy
- **数据库**: PostgreSQL (Synology NAS)
- **AI**: DeepSeek API / Claude API
- **前端**: HTML + JavaScript + Marked.js

## 快速开始

### 1. 环境配置

```bash
# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的配置
```

### 2. 数据库设置

确保 NAS PostgreSQL 已配置并可访问：

```bash
# 测试数据库连接
python tests/test_nas_connection.py
```

### 3. 启动服务

```bash
# 启动 FastAPI 服务
./scripts/start.sh

# 或手动启动
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 4. 访问界面

打开浏览器访问：http://localhost:8000/static/index.html

## 项目结构

```
xiaole-ai/
├── agent.py              # AI 代理核心逻辑
├── memory.py             # 记忆管理器
├── conversation.py       # 对话管理器
├── error_handler.py      # 错误处理装饰器
├── db_setup.py           # 数据库模型定义
├── main.py               # FastAPI 应用入口
├── requirements.txt      # Python 依赖
├── static/               # 前端静态文件
│   └── index.html        # Web 界面
├── docs/                 # 文档
├── tests/                # 测试文件
├── scripts/              # 启动脚本
└── logs/                 # 日志文件
```

## API 接口

### 对话接口

```bash
# 发送消息
POST /chat?prompt=你好

# 获取会话列表
GET /sessions?user_id=default_user

# 获取会话历史
GET /session/{session_id}

# 删除会话
DELETE /session/{session_id}
```

### 记忆接口

```bash
# 获取记忆
GET /memory?tag=facts&limit=10

# 搜索记忆
GET /memory/search?keywords=高鹏,生日

# 最近记忆
GET /memory/recent?hours=24

# 记忆统计
GET /memory/stats
```

## 配置说明

### 环境变量 (.env)

```env
# 数据库配置
DB_HOST=192.168.88.188
DB_PORT=5432
DB_NAME=xiaole_ai
DB_USER=your_user
DB_PASS=your_password

# AI API 配置
DEEPSEEK_API_KEY=your_deepseek_key
# 或使用 Claude
CLAUDE_API_KEY=your_claude_key
USE_CLAUDE=false
```

## 开发指南

### 添加新功能

1. 在 `agent.py` 中添加新方法
2. 在 `main.py` 中添加 API 端点
3. 更新 `static/index.html` 界面（如需要）

### 运行测试

```bash
python tests/test_agent.py
python tests/test_api.py
```

### 查看日志

```bash
tail -f logs/xiaole_ai.log
```

## 已知限制

- 暂不支持向量语义搜索（依赖安装复杂）
- 无法访问互联网获取实时信息
- 不支持语音交互

## 路线图

- [ ] 向量语义搜索（使用 API 方式）
- [ ] 天气查询功能
- [ ] 定时提醒功能
- [ ] 语音交互支持
- [ ] 移动端适配

## 许可证

MIT License

## 作者

高鹏 - 个人项目

---

**注意**: 本项目仅供个人学习使用，请勿用于商业用途。

