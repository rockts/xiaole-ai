# 小乐 AI 管家

> v0.8.0 - 智能交互版 🎉 | 当前稳定版本

> 🚧 develop 分支：v0.9.0 前端架构升级（Vue 3 + Vite）

个人 AI 助手，支持**语音交互**、**多轮任务规划**、**长文本总结**、长期记忆、对话管理、用户行为学习、工具调用和任务执行、主动提醒和实时推送、智能图片记忆、课程表管理。

## ✨ v0.9.0 开发中功能

### 🎨 前端架构全面升级
- **Vue 3 + Vite**：现代化前端框架，极速热更新
- **组件化架构**：5个核心组件（TopBar/Sidebar/ChatView/MemoryView/SettingsView）
- **状态管理**：Pinia统一管理应用状态（chat/memory/settings/tasks）
- **路由系统**：Vue Router动态路由，支持会话URL跳转
- **自动重连**：API自动重试（3次指数退避）+ 健康检查轮询（30秒）
- **用户体验优化**：
  - 浏览器标题自动显示会话名称
  - 记忆页面时间显示简化
  - 网络异常自动恢复
  - 侧边栏历史滚动条修复（全局样式 + 首屏自动分页）
  - 会话三点菜单传送到 body，点击坐标定位且不被裁剪
  - 置顶会话图钉标识，整体字号更接近 ChatGPT

### 🖼️ 分享预览（新）
- 优先使用服务端预览 `GET /api/share/preview/{id}.png`，失败回退前端生成
- 前端截图基于 `html-to-image`，自动等待样式与图片加载
- 分享卡片展示最近 5 条消息，支持图片消息与文本混排
- 自动规范图片路径（修复 `uploads/uploads/...` 重复）
- ChatGPT 风格卡片：头像、气泡、左侧色条、圆角与阴影、行数截断

## ✨ v0.8.0 已发布功能

### 🎤 语音交互功能
- **语音输入**：支持 Google Web Speech API 和百度语音识别
- **语音输出**：浏览器 TTS 和百度语音合成，4种音色可选
- **自动播放**：AI回复自动朗读，可视化播放状态
- **语音控制**：语速调节（0.5-2x）、音量控制（0-100%）
- **连续对话**：语音对话模式，自动识别和回复

### 📋 多轮任务规划
- **智能拆解**：自动识别复杂任务并拆解为多个步骤
- **步骤类型**：
  - 工具调用步骤（调用系统工具）
  - 用户确认步骤（等待用户确认）
  - 等待步骤（延时执行）
  - 信息展示步骤（提示信息）
- **顺序执行**：按步骤顺序执行，失败时可选择继续或中断
- **进度追踪**：实时显示执行进度、完成数量、失败数量
- **任务管理**：创建、查看、执行、取消、删除任务

### 📄 长文本总结
- **文档支持**：PDF、Word、TXT、Markdown文件上传
- **智能总结**：分块处理，多级总结算法
- **关键提取**：自动提取5-10个核心要点
- **导出功能**：Markdown格式导出，保留完整信息

### 🎨 界面焕新（2025-11-15 迭代）
- 顶部导航透明化及会话标题居中显示，保持桌面与移动端一致体验
- 侧边栏与聊天区重新布局，恢复“左侧导航、右侧对话”结构并优化折叠效果
- 聊天气泡、头像与删除按钮统一风格，提升 ChatGPT 风格的沉浸感
- 新建对话流程修复，确保自动跳转聊天页并同步浏览器地址

## 功能特性

✅ **智能记忆管理**
- 自动提取用户告知的关键事实
- 区分事实记忆和闲聊内容
- 支持关键词和标签搜索
- **语义搜索**：基于TF-IDF的轻量级语义理解
- **智能图片记忆**：自动识别并记忆重要图片（家人照片、课程表等）
- **记忆管理界面**：全部、搜索、编辑、删除功能
- **Markdown渲染**：记忆内容支持Markdown格式显示

✅ **对话上下文管理**
- 多会话支持，记录完整对话历史
- 上下文感知，连贯的对话体验
- **会话标题显示**：快速识别对话内容

✅ **Learning层 - 用户行为学习** (v0.3.0)
- **主动问答**：
  - 识别未完整回答的问题
  - 主动追问缺失信息
  - 置信度评分系统（0-100）
  - 追问历史记录

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
  - Open-Meteo API集成（免费）
- **搜索工具**：
  - DuckDuckGo网络搜索
  - 搜索结果解析和展示
- **文件工具**：
  - 文件读写操作
  - 文件列表和搜索
✅ **Active Perception层 - 主动感知与响应** (v0.5.0) 🆕
  - 提醒优先级系统（1-5级）
  - 重复提醒支持
  - 服务端连接池管理
  - 自动重连机制（5秒间隔）
  - 实时弹窗通知
  - 浏览器原生通知
  - 提醒声音（双响"叮咚"）
- **定时任务调度** ⏰：
  - APScheduler集成
  - 提醒定时检查（每分钟）
  - 行为提醒检查
  - 后台任务管理
- **主动对话发起** 💬：
  - 4种触发场景（待追问、长时间未聊天、活跃时间、有趣话题）
  - 优先级系统（2-5级）
  - 渐变紫色通知卡片
  - 滑入/滑出动画
  - 每小时检查一次
- **追问提示** 🤔：
  - 实时追问提示（粉色渐变卡片）
  - 点击自动发送追问
  - 800Hz提示音
  - 8秒后自动消失

✅ **课程表管理** (v0.7.0) 📅
- **智能课程解析**：从图片自动提取课程表信息
- **课程查询优化**：包含第4节在上午时段，跳过无课显示
- **在线编辑**：可视化表格编辑课程
- **自动保存**：编辑后一键保存到记忆

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
- 实时对话体验，左侧边栏 + 右侧聊天的响应式布局
- 深色模式支持
- 快捷键支持（Ctrl+Enter发送）

## 技术栈

- **后端**: FastAPI + SQLAlchemy
- **数据库**: PostgreSQL (Synology NAS)
- **AI**: DeepSeek API / Claude API
- **前端**: Vue 3 + Vite + Pinia + Vue Router + Marked.js

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
# 推荐使用虚拟环境
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 启动 FastAPI 服务
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 4. 前端开发与访问

开发阶段推荐使用 Vite：

```bash
# 使用 Node 20（建议）
cd frontend
source ~/.nvm/nvm.sh && nvm use 20
npm install
npm run dev
```

打开浏览器访问：

- Vite 本地地址：`http://localhost:3000`
- 旧版静态页（如需）：`http://localhost:8000/static/index.html`（已不再作为主界面）

## 项目结构

```
xiaole-ai/
├── agent.py                # AI 代理核心逻辑
├── memory.py               # 记忆管理器
├── conversation.py         # 对话管理器
├── behavior_analytics.py   # 用户行为分析器 (v0.3.0)
├── conflict_detector.py    # 记忆冲突检测器 (v0.3.0)
├── proactive_qa.py         # 主动问答分析器 (v0.3.0)
├── pattern_learning.py     # 模式学习器 (v0.3.0)
├── tool_manager.py         # 工具调用管理器 (v0.4.0)
├── reminder_manager.py     # 提醒管理器 (v0.5.0) 🆕
├── scheduler.py            # 定时任务调度器 (v0.5.0) 🆕
├── proactive_chat.py       # 主动对话管理器 (v0.5.0) 🆕
├── semantic_search.py      # 语义搜索引擎
├── error_handler.py        # 错误处理装饰器
├── db_setup.py             # 数据库模型定义
├── main.py                 # FastAPI 应用入口
├── requirements.txt        # Python 依赖
├── tools/                  # 工具模块 (v0.4.0+)
│   ├── __init__.py
│   ├── weather_tool.py     # 天气查询工具
│   ├── system_tool.py      # 系统操作工具
│   ├── search_tool.py      # 网络搜索工具 🆕
│   ├── file_tool.py        # 文件操作工具 🆕
│   └── reminder_tool.py    # 提醒工具 🆕
├── frontend/               # 新前端（Vue 3 + Vite + Pinia + Router）
│   ├── src/
│   │   ├── views/          # 视图（ChatView/MemoryView/SettingsView 等）
│   │   ├── components/     # 组件
│   │   └── stores/         # Pinia 状态
│   └── vite.config.ts      # Vite 配置
├── static/                 # 旧静态页面（保留/兼容，非主界面）
│   └── index.html
├── docs/                   # 文档
│   ├── v0.5.0_PLAN.md      # v0.5.0开发计划 🆕
│   ├── v0.5.0_COMPLETED.md # v0.5.0完成报告 🆕
│   ├── v0.6.0_PLAN.md      # v0.6.0开发计划 🆕
│   └── FOLLOWUP_TEST_GUIDE.md  # 追问测试指南 🆕
├── tests/                  # 测试文件
├── scripts/                # 脚本
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
# 主动问答历史
GET /proactive/history?user_id=default_user&limit=10

# 待追问列表
GET /proactive/pending/{session_id}

# 分析会话
GET /proactive/analyze/{session_id}

# 标记已追问
POST /proactive/mark_asked/{question_id}
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

1. 在 `agent.py` 中添加业务/工具逻辑
2. 在 `main.py` 中添加或调整 API 端点
3. 在前端 `frontend/src/` 中更新相应视图与组件（例如 `views/ChatView.vue`）

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
- `main`: 稳定版本分支（生产环境）
- `develop`: 开发分支（日常开发）
- `feature/*`: 功能分支
- `hotfix/*`: 紧急修复分支

### 开发流程

```bash
# 1. 从develop分支创建功能分支
git checkout develop
git checkout -b feature/new-feature

# 2. 开发并提交
git add .
git commit -m "feat: 添加新功能"

# 3. 完成后合并到develop
git checkout develop
git merge feature/new-feature

# 4. 测试稳定后合并到main
git checkout main
git merge develop --no-ff -m "release: v0.x.0"
git tag v0.x.0
git push origin main --tags
```

### 提交规范

使用语义化提交信息：

```bash
feat: ✨ 新功能
fix: 🐛 Bug修复
docs: 📝 文档更新
style: 🎨 代码格式
refactor: ♻️ 代码重构
perf: ⚡ 性能优化
test: 🧪 测试相关
chore: 🔧 构建/工具
```

### 自动提交工具

```bash
# 交互式提交（推荐）
./scripts/auto_commit.sh

# 快速提交
./scripts/quick_commit.sh "提交描述" [类型] [范围]
```

## 已知限制

- 语义搜索对短查询效果有限（可通过同义词词典改进）
- 天气查询需配置和风天气API密钥
- 部分工具功能需要相应的API权限
- 前端开发建议 Node.js 20+；分享卡片回退截图依赖 `html-to-image`

## 🗺️ 发展路线图

> 详细规划请查看 [docs/README.md](docs/README.md)

### 🚧 v0.9.0 - 前端组件化与界面统一（开发中）
- 拆分 `static/index.html`，构建可复用的布局、侧边栏、聊天与设置组件
- 抽离样式到 `static/css/`，脚本到 `static/js/`，建立统一加载策略
- 统一对话入口（欢迎页、新建对话、聊天窗口）视觉与交互体验
- 完成组件化后的回归测试、文档与迁移指南

### ✅ v0.2.0 - 语义搜索版本
- [x] 轻量级语义搜索（TF-IDF + jieba）
- [x] 会话标题自动生成

### ✅ v0.3.0 - Learning层
- [x] 主动问答（识别未完整问题并追问）

### ✅ v0.4.0 - Action层（已完成）
- [x] 工具调用框架（统一接口、参数验证）
- [x] 系统工具（CPU/内存/磁盘/时间/计算器）
- [x] 天气工具（实时天气、预报查询）
- [x] 工具执行历史追踪
- [x] 智能工具选择（Agent自动识别意图）
- [x] 记忆系统集成（从记忆提取参数）
- [x] Open-Meteo API集成（免费无需key）
- [x] 前端工具面板展示

### ✅ v0.5.0 - Active Perception层（已完成）
- [x] 主动提醒系统（基于记忆和行为模式）
- [x] 定时任务调度器（APScheduler）
- [x] 网络搜索工具（DuckDuckGo API）
- [x] 文件操作工具（安全限制）
- [x] 主动对话发起（智能触发）
- [x] WebSocket推送通知
- [x] 追问提示功能（实时粉色卡片提示）
- [x] 提醒管理界面（创建/查看/删除）
- [x] 稍后提醒功能（5分钟延迟）
- [x] 浏览器原生通知支持

### ✅ v0.6.0 - 智能增强版（已完成）

**Phase 1: 问题修复** ✅
- [x] 搜索工具网络优化（代理支持、超时处理、结果缓存）
- [x] 主动问答策略优化（去重、冷却时间）
- [x] 性能优化（数据库索引、查询优化）

**Phase 2: 用户体验提升** ✅
- [x] 深色模式支持
- [x] 快捷键支持（Ctrl+Enter发送）
- [x] 快捷键提示栏
- [x] 会话导出（Markdown/JSON）
- [x] 消息编辑功能
- [x] 消息删除功能
- [x] 消息搜索功能（高亮显示）

> 详细规划：[v0.6.0_PLAN.md](docs/v0.6.0_PLAN.md)

### ✅ v0.7.0 - 课程表管理（已完成）
- [x] 课程表图片上传和智能解析（Qwen-VL）
- [x] 课程表可视化编辑界面
- [x] 课程信息记忆存储
- [x] 课程查询API

### ✅ v0.7.1 - 记忆和图片智能优化（已完成）
- [x] 修复记忆管理bug（Memory.user_id字段问题）
- [x] 智能图片记忆（自动识别重要图片）
- [x] 记忆Markdown渲染
- [x] 课程表查询优化（包含第4节、跳过无课）
- [x] 事实提取增强（区分用户和家人信息）
- [x] 记忆删除确认对话框
- [x] 前端事件绑定优化
- [x] 课程表页面自动加载
- [x] 无课显示空白优化

### ✅ v0.8.0 - 智能交互版（已完成）🎉

**Phase 1: 语音交互功能** ✅
- [x] Web Speech API语音输入/输出
- [x] 百度语音识别和语音合成
- [x] 麦克风按钮和语音波形动画
- [x] 自动播放开关和语速调节
- [x] 4种音色选择和音量控制

**Phase 2: 多轮任务规划** ✅
- [x] AI自动拆解复杂任务
- [x] 任务执行引擎和进度追踪
- [x] 任务可视化界面
- [x] 7个任务管理API端点

**Phase 3: 长文本总结** ✅
- [x] PDF/Word/TXT/Markdown文档上传
- [x] 智能分段总结（分块+多级总结）
- [x] 关键信息提取（5-10个要点）
- [x] Markdown格式导出功能

> 详细说明：[v0.8.0_RELEASE.md](docs/v0.8.0_RELEASE.md)

### 🚀 v0.9.0 - 下一步计划（规划中）

**UI优化计划：**
- [ ] 现代化界面设计（卡片式布局、圆角、阴影）
- [ ] 响应式布局优化（移动端适配）
- [ ] 组件化重构（Vue/React）
- [ ] 主题系统增强（多主题支持）
- [ ] 动画效果优化（流畅过渡）

**功能扩展计划：**
- [ ] 系统操作工具增强（启动应用、控制音量等）
- [ ] 智能家居控制（HomeAssistant集成）
- [ ] 日程管理增强（日历同步、会议纪要）
- [ ] 知识库问答（RAG + pgvector）
- [ ] 多模态交互优化（图片+语音+文本联动）

**已知问题（v0.8.0）：**
- UI样式较为陈旧，需要现代化改造
- 网络搜索工具偶尔超时（需要代理优化）

**架构参考**：[三层智能架构图](docs/architecture.png)

## 许可证

MIT License

## 作者

高鹏 - 个人项目

---

**注意**: 本项目仅供个人学习使用，请勿用于商业用途。

