# 小乐 AI 管家

> v0.4.0 - Action层开发中 | v0.3.0 - Learning层完成 | v0.2.0 - 语义搜索

个人 AI 助手，支持长期记忆、对话管理、用户行为学习、**工具调用和任务执行**。

## 功能特性

✅ **智能记忆管理**
- 自动提取用户告知的关键事实
- 区分事实记忆和闲聊内容
- 支持关键词和标签搜索
- **语义搜索**：基于TF-IDF的轻量级语义理解

✅ **对话上下文管理**
- 多会话支持，记录完整对话历史
- 上下文感知，连贯的对话体验
- **会话标题显示**：快速识别对话内容

✅ **Learning层 - 用户行为学习** (v0.3.0)
- **行为分析**：
  - 活跃时间分析（小时/星期分布）
  - 话题偏好分析（关注的主题）
  - 对话统计（会话数、消息数、平均长度）
- **冲突检测**：
  - 自动识别矛盾的关键信息（姓名、年龄、生日、性别、地址）
  - 智能判断逻辑（昵称容忍、年龄±2岁）
  - 详细冲突报告和摘要
- **主动问答**：
  - 识别未完整回答的问题
  - 主动追问缺失信息
  - 置信度评分系统（0-100）
  - 追问历史记录
- **模式学习**：
  - 高频词汇识别（置信度分级）
  - 常见问题自动归类（6大类：天气查询、时间日期、个人信息、功能咨询、推荐建议、闲聊）
  - 用户偏好模型构建
  - 学习统计洞察

✅ **Action层 - 工具调用与任务执行** (v0.4.0)
- **工具调用框架**：
  - 统一的工具接口和参数验证
  - 工具注册中心和生命周期管理
  - 自动执行追踪和性能统计
- **系统工具**：
  - 系统信息查询（CPU、内存、磁盘）
  - 时间日期查询
  - 数学计算器（支持基本运算和数学函数）
- **天气工具**：
  - 实时天气查询
  - 3天/7天天气预报
  - 和风天气API集成
- **工具执行历史**：
  - 完整的执行记录和结果追踪
  - 性能指标统计

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
- **行为分析面板**：可视化展示用户行为数据、冲突检测、主动问答和学习模式
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
├── agent.py                # AI 代理核心逻辑
├── memory.py               # 记忆管理器
├── conversation.py         # 对话管理器
├── behavior_analytics.py   # 用户行为分析器
├── conflict_detector.py    # 记忆冲突检测器
├── proactive_qa.py         # 主动问答分析器
├── pattern_learning.py     # 模式学习器
├── tool_manager.py         # 工具调用管理器 (v0.4.0)
├── semantic_search.py      # 语义搜索引擎
├── error_handler.py        # 错误处理装饰器
├── db_setup.py             # 数据库模型定义
├── main.py                 # FastAPI 应用入口
├── requirements.txt        # Python 依赖
├── tools/                  # 工具模块 (v0.4.0)
│   ├── __init__.py
│   ├── weather_tool.py     # 天气查询工具
│   └── system_tool.py      # 系统操作工具
├── static/                 # 前端静态文件
│   └── index.html          # Web 界面
├── docs/                   # 文档
├── tests/                  # 测试文件
├── scripts/                # 启动脚本
└── logs/                   # 日志文件
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

### 行为分析接口 (v0.3.0)

```bash
# 用户行为统计
GET /analytics/behavior?user_id=default_user&days=30

# 活跃时间分布
GET /analytics/activity?user_id=default_user&days=30

# 话题偏好
GET /analytics/topics?user_id=default_user&days=30

# 记忆冲突检测
GET /memory/conflicts?tag=facts&limit=100

# 冲突摘要
GET /memory/conflicts/summary

# 冲突详细报告
GET /memory/conflicts/report

# 主动问答历史
GET /proactive/history?user_id=default_user&limit=10

# 待追问列表
GET /proactive/pending/{session_id}

# 分析会话
GET /proactive/analyze/{session_id}

# 标记已追问
POST /proactive/mark_asked/{question_id}

# 高频词列表
GET /patterns/frequent?user_id=default_user&limit=20

# 常见问题分类
GET /patterns/common_questions?user_id=default_user&limit=10

# 学习统计洞察
GET /patterns/insights?user_id=default_user
```

### 工具调用接口 (v0.4.0)

```bash
# 列出所有工具
GET /tools/list?category=system&enabled_only=true

# 执行工具
POST /tools/execute?tool_name=time&user_id=default_user
Body: {"format": "full"}

# 工具执行历史
GET /tools/history?user_id=default_user&limit=20
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

# 工具API配置 (v0.4.0)
QWEATHER_API_KEY=your_qweather_key  # 和风天气API密钥（可选）
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

## Git 工作流

本项目使用 Git Flow 分支策略：

### 分支说明
- `main`: 稳定版本分支
- `develop`: 开发分支（日常开发在此进行）
- `feature/*`: 功能分支
- `hotfix/*`: 紧急修复分支

### 自动提交工具

项目提供了两个自动提交工具，会自动更新 CHANGELOG.md：

#### 1. 交互式提交（推荐）

```bash
./scripts/auto_commit.sh
```

功能：
- 🔍 自动检测修改文件
- 🤖 智能推荐提交类型和范围
- 📝 交互式输入提交信息
- 📋 自动更新 CHANGELOG
- 🚀 可选推送到远程

#### 2. 快速提交

```bash
# 基本用法
./scripts/quick_commit.sh "提交描述" [类型] [范围]

# 示例
./scripts/quick_commit.sh "修复记忆查询bug" fix memory
./scripts/quick_commit.sh "添加语音功能" feat agent
./scripts/quick_commit.sh "更新文档" docs
```

#### 提交类型
- `feat`: ✨ 新功能
- `fix`: 🐛 Bug修复
- `docs`: 📝 文档更新
- `style`: 🎨 代码格式/样式
- `refactor`: ♻️ 代码重构
- `perf`: ⚡ 性能优化
- `test`: 🧪 测试相关
- `chore`: 🔧 构建/工具
- `config`: ⚙️ 配置修改

### 开发流程

```bash
# 1. 切换到 develop 分支
git checkout develop

# 2. 拉取最新代码
git pull origin develop

# 3. 进行开发...

# 4. 使用自动提交工具
./scripts/auto_commit.sh

# 5. 功能完成后合并到 main
git checkout main
git merge develop
git push origin main
```

## 已知限制

- 语义搜索对短查询效果有限（可通过同义词词典改进）
- 天气查询需配置和风天气API密钥
- 部分工具功能需要相应的API权限

## 🗺️ 发展路线图

> 详细规划请查看 [docs/README.md](docs/README.md)

### ✅ v0.2.0 - 语义搜索版本
- [x] 轻量级语义搜索（TF-IDF + jieba）
- [x] 会话标题自动生成

### ✅ v0.3.0 - Learning层
- [x] 用户行为分析（对话模式、话题偏好）
- [x] 记忆冲突检测（自动识别矛盾信息）
- [x] 行为分析可视化面板
- [x] 主动问答（识别未完整问题并追问）
- [x] 模式学习（高频词汇、常见问题分类）

### 🚧 v0.4.0 - Action层（已完成 ✅）
- [x] 工具调用框架（统一接口、参数验证）
- [x] 系统工具（CPU/内存/磁盘/时间/计算器）
- [x] 天气工具（实时天气、预报查询）
- [x] 工具执行历史追踪
- [x] 智能工具选择（Agent自动识别意图）
- [x] 记忆系统集成（从记忆提取参数）
- [x] Open-Meteo API集成（免费无需key）
- [x] 前端工具面板展示
- [ ] 网络搜索工具（延后到v0.5.0）
- [ ] 文件操作工具（延后到v0.5.0）

### 🔮 v0.5.0+ - Active Perception层
- [ ] 语音交互（TTS/STT）
- [ ] 多模态输入（图片、文件）
- [ ] 主动提醒（基于记忆的智能提醒）

**架构参考**：[三层智能架构图](docs/architecture.png)

## 许可证

MIT License

## 作者

高鹏 - 个人项目

---

**注意**: 本项目仅供个人学习使用，请勿用于商业用途。

