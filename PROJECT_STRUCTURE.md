# 小乐 AI 项目结构

> 最后更新：2025-11-14

## 📁 目录结构

```
xiaole-ai/
├── 📄 核心应用代码
│   ├── main.py                    # FastAPI应用入口
│   ├── agent.py                   # AI代理核心逻辑
│   ├── conversation.py            # 对话管理器
│   ├── memory.py                  # 记忆管理器
│   ├── db_setup.py                # 数据库模型定义
│   └── error_handler.py           # 错误处理装饰器
│
├── 🧠 智能分析模块
│   ├── behavior_analytics.py      # 用户行为分析
│   ├── conflict_detector.py       # 记忆冲突检测
│   ├── proactive_qa.py            # 主动问答分析
│   ├── pattern_learning.py        # 模式学习
│   ├── learning.py                # 学习层管理器
│   ├── semantic_search.py         # 语义搜索引擎
│   ├── dialogue_enhancer.py       # 对话增强器
│   └── enhanced_intent.py         # 意图增强识别
│
├── 🎯 任务与提醒
│   ├── task_manager.py            # 任务管理器
│   ├── task_executor.py           # 任务执行引擎
│   ├── reminder_manager.py        # 提醒管理器
│   ├── scheduler.py               # 定时任务调度器
│   ├── proactive_chat.py          # 主动对话管理
│   └── document_summarizer.py     # 文档总结器
│
├── 🔧 工具系统
│   ├── tool_manager.py            # 工具调用管理器
│   ├── tools/                     # 工具模块目录
│   │   ├── weather_tool.py        # 天气查询工具
│   │   ├── system_tool.py         # 系统操作工具
│   │   ├── search_tool.py         # 网络搜索工具
│   │   ├── file_tool.py           # 文件操作工具
│   │   └── reminder_tool.py       # 提醒工具
│   ├── vision_tool.py             # 图片识别工具（Qwen-VL）
│   └── baidu_voice_tool.py        # 百度语音工具
│
├── 🌐 前端界面
│   └── static/
│       └── index.html             # Web界面（单页应用）
│
├── 📚 文档
│   ├── README.md                  # 文档总览
│   ├── INDEX.md                   # 文档索引
│   ├── QUICK_REFERENCE.md         # 快速参考
│   ├── DEVELOPMENT_LOG.md         # 开发日志
│   ├── PROJECT_STATUS.md          # 项目状态
│   ├── v0.8.0_RELEASE.md          # 最新版本说明
│   ├── NEXT_DEVELOPMENT.md        # 下一步计划
│   ├── archived/                  # 历史文档归档
│   │   ├── v0.5.0/               # v0.5.0文档
│   │   ├── v0.6.0/               # v0.6.0文档
│   │   ├── v0.7.0/               # v0.7.0文档
│   │   └── issues/               # 问题修复文档
│   └── ...（环境配置、测试指南等）
│
├── 🗄️ 数据库
│   └── db_migrations/             # 数据库迁移脚本
│       ├── 001_create_reminders_tables.sql
│       ├── 002_add_indexes_v0.6.0.sql
│       └── ...
│
├── 🧪 测试
│   ├── tests/                     # 单元测试
│   │   ├── test_agent.py
│   │   ├── test_api.py
│   │   └── ...
│   └── tests/temp/                # 临时测试文件（不提交）
│       ├── test_baidu_sdk.py
│       ├── check_result.py
│       └── ...
│
├── 🛠️ 脚本工具
│   └── scripts/
│       ├── start.sh               # 启动服务
│       ├── auto_commit.sh         # 交互式提交
│       ├── quick_commit.sh        # 快速提交
│       ├── init_reminder_tables.py
│       └── ...
│
├── 📦 数据目录
│   ├── uploads/                   # 用户上传文件
│   ├── files/                     # 文件操作工具目录
│   ├── logs/                      # 日志文件
│   └── archive/                   # 归档数据（不提交）
│
├── ⚙️ 配置文件
│   ├── .env                       # 环境变量（不提交）
│   ├── .env.example               # 环境变量示例
│   ├── .env.baidu.example         # 百度API配置示例
│   ├── requirements.txt           # Python依赖
│   ├── .gitignore                 # Git忽略规则
│   └── README.md                  # 项目说明
│
└── 📝 项目管理
    ├── CHANGELOG.md               # 变更日志
    ├── PROGRESS.md                # 进度跟踪
    └── PROJECT_STRUCTURE.md       # 本文档
```

## 📋 文件分类说明

### 核心文件（必需）
- `main.py` - 应用入口，启动服务
- `agent.py` - AI对话核心
- `memory.py` - 记忆系统
- `db_setup.py` - 数据库模型
- `requirements.txt` - 依赖管理

### 智能层（Learning层）
- `behavior_analytics.py` - 分析用户行为模式
- `conflict_detector.py` - 检测记忆冲突
- `proactive_qa.py` - 主动追问
- `pattern_learning.py` - 学习用户偏好

### 行动层（Action层）
- `task_manager.py` + `task_executor.py` - 任务系统
- `tool_manager.py` + `tools/` - 工具调用
- `reminder_manager.py` - 提醒系统
- `document_summarizer.py` - 文档总结

### 感知层（Active Perception层）
- `scheduler.py` - 定时调度
- `proactive_chat.py` - 主动对话
- `vision_tool.py` - 图片识别
- `baidu_voice_tool.py` - 语音交互

## 🗑️ 不提交到Git的文件

以下文件通过`.gitignore`排除：

### 环境和配置
- `.env` - 敏感配置
- `.venv/` - Python虚拟环境
- `__pycache__/` - Python缓存

### 数据和日志
- `uploads/*` - 用户上传（保留.gitkeep）
- `files/*` - 文件操作（保留.gitkeep）
- `logs/*.log` - 日志文件
- `archive/` - 归档数据

### 临时文件
- `tests/temp/` - 临时测试脚本
- `*_result.txt` - 测试结果
- `.DS_Store` - macOS系统文件
- `repo_structure.txt` - 临时结构文件

## 📖 重要文档

### 新用户必读
1. `README.md` - 项目介绍和快速开始
2. `docs/QUICK_REFERENCE.md` - 快速参考指南
3. `docs/DEEPSEEK_SETUP.md` - API配置
4. `docs/NAS_POSTGRESQL_SETUP.md` - 数据库配置

### 开发者必读
1. `docs/DEVELOPMENT_LOG.md` - 开发历程
2. `docs/PROJECT_STATUS.md` - 项目现状
3. `docs/v0.8.0_RELEASE.md` - 最新版本
4. `PROJECT_STRUCTURE.md` - 本文档

## 🔄 目录维护规则

### 定期清理
- `tests/temp/` - 临时测试文件（不提交）
- `logs/` - 旧日志文件（仅保留最近7天）
- `archive/` - 过期归档（不提交）

### 文档归档
- 旧版本文档 → `docs/archived/vX.X.X/`
- 问题修复文档 → `docs/archived/issues/`
- 保留最新版本文档在根目录

### 代码组织
- 核心代码：保持根目录简洁
- 工具模块：统一放在`tools/`目录
- 测试代码：放在`tests/`目录
- 脚本工具：放在`scripts/`目录

## 🎯 目录设计原则

1. **简洁性**：根目录只保留核心文件
2. **分类性**：按功能模块组织代码
3. **可维护性**：清晰的命名和文档
4. **版本控制**：只提交必要文件
5. **可扩展性**：预留扩展空间

---

**维护者**：高鹏  
**更新频率**：重大结构调整时更新
