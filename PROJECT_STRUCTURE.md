# 小乐 AI 项目结构

> 最后更新：2025-11-21

## 📁 目录结构

```
xiaole-ai/
├── 🖥️ 后端应用 (backend/)
│   ├── main.py                    # FastAPI应用入口
│   ├── agent.py                   # AI代理核心逻辑
│   ├── conversation.py            # 对话管理器
│   ├── memory.py                  # 记忆管理器
│   ├── db_setup.py                # 数据库模型定义
│   ├── error_handler.py           # 错误处理装饰器
│   │
│   ├── 🧠 智能分析模块
│   │   ├── behavior_analytics.py      # 用户行为分析
│   │   ├── conflict_detector.py       # 记忆冲突检测
│   │   ├── proactive_qa.py            # 主动问答分析
│   │   ├── pattern_learning.py        # 模式学习
│   │   ├── learning.py                # 学习层管理器
│   │   ├── semantic_search.py         # 语义搜索引擎
│   │   ├── dialogue_enhancer.py       # 对话增强器
│   │   └── enhanced_intent.py         # 意图增强识别
│   │
│   ├── 🎯 任务与提醒
│   │   ├── task_manager.py            # 任务管理器
│   │   ├── task_executor.py           # 任务执行引擎
│   │   ├── reminder_manager.py        # 提醒管理器
│   │   ├── scheduler.py               # 定时任务调度器
│   │   ├── proactive_chat.py          # 主动对话管理
│   │   └── document_summarizer.py     # 文档总结器
│   │
│   ├── 🔧 工具系统
│   │   ├── tool_manager.py            # 工具调用管理器
│   │   ├── tools/                     # 工具模块目录 (待移动)
│   │   ├── vision_tool.py             # 图片识别工具（Qwen-VL）
│   │   └── baidu_voice_tool.py        # 百度语音工具
│   │
│   ├── 🗄️ 数据与资源
│   │   ├── db_migrations/             # 数据库迁移脚本
│   │   ├── static/                    # 静态资源
│   │   ├── uploads/                   # 用户上传文件
│   │   ├── files/                     # 文件操作工具目录
│   │   └── archive/                   # 归档数据
│
├── 🌐 前端应用 (frontend/)
│   ├── src/                       # Vue源码
│   ├── public/                    # 公共资源
│   ├── package.json               # 前端依赖
│   └── vite.config.js             # Vite配置
│
├── 📚 文档 (docs/)
│   ├── README.md                  # 文档总览
│   ├── INDEX.md                   # 文档索引
│   ├── QUICK_REFERENCE.md         # 快速参考
│   ├── DEVELOPMENT_LOG.md         # 开发日志
│   ├── PROJECT_STATUS.md          # 项目状态
│   ├── v0.8.0_RELEASE.md          # 最新版本说明
│   ├── NEXT_DEVELOPMENT.md        # 下一步计划
│   ├── archived/                  # 历史文档归档
│   └── ...
│
├── 🧪 测试 (tests/)
│   ├── tests/                     # 单元测试
│   └── temp/                      # 临时测试文件和调试脚本
│
├── 🛠️ 脚本工具 (scripts/)
│   ├── init_reminder_tables.py    # 初始化表
│   ├── auto_commit.sh             # 交互式提交
│   └── ...
│
├── ⚙️ 根目录配置
│   ├── start.sh                   # 统一启动脚本
│   ├── stop.sh                    # 停止脚本
│   ├── restart.sh                 # 重启脚本
│   ├── .env                       # 环境变量
│   ├── requirements.txt           # Python依赖
│   ├── .gitignore                 # Git忽略规则
│   ├── README.md                  # 项目说明
│   ├── CHANGELOG.md               # 变更日志
│   ├── PROGRESS.md                # 进度跟踪
│   └── PROJECT_STRUCTURE.md       # 本文档
│
└── 📦 日志 (logs/)
    ├── backend.log                # 后端日志
    └── frontend.log               # 前端日志
```

## 📋 文件分类说明

### 后端 (backend/)
所有 Python 核心代码已移动至 `backend/` 目录，保持根目录整洁。
- `main.py` - 应用入口
- `agent.py` - AI核心
- `db_migrations/` - 数据库迁移文件

### 前端 (frontend/)
Vue 3 + Vite 前端项目。

### 脚本 (scripts/)
维护和工具脚本。注意：部分脚本可能需要更新路径以指向 `backend/` 目录。

## 🗑️ 不提交到Git的文件

以下文件通过`.gitignore`排除：

### 环境和配置
- `.env` - 敏感配置
- `.venv/` - Python虚拟环境
- `__pycache__/` - Python缓存

### 数据和日志
- `backend/uploads/*` - 用户上传
- `backend/files/*` - 文件操作
- `logs/*.log` - 日志文件
- `backend/archive/` - 归档数据

### 临时文件
- `tests/temp/` - 临时测试脚本
- `*_result.txt` - 测试结果
- `.DS_Store` - macOS系统文件

## 📖 重要文档

### 新用户必读
1. `README.md` - 项目介绍和快速开始
2. `docs/QUICK_REFERENCE.md` - 快速参考指南

### 开发者必读
1. `docs/DEVELOPMENT_LOG.md` - 开发历程
2. `PROJECT_STRUCTURE.md` - 本文档

## 🔄 目录维护规则

### 代码组织
- **后端代码**：全部放入 `backend/`
- **前端代码**：全部放入 `frontend/`
- **文档**：全部放入 `docs/` (除了根目录的几个关键文档)
- **脚本**：全部放入 `scripts/`

### 路径引用
- 在 `backend/` 内部引用文件时，使用相对路径或 `os.path.dirname(__file__)`。
- 在根目录脚本引用后端文件时，需指向 `backend/`。

---

**维护者**：高鹏
**更新频率**：重大结构调整时更新
