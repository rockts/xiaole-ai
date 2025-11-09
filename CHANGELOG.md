# 开发日志 (Changelog)

本文件记录 xiaole-ai 项目的详细开发历史。

## 格式说明
- 📝 文档更新
- ✨ 新功能
- 🐛 Bug修复
- 🔧 配置修改
- ♻️ 代码重构
- 🎨 样式优化
- ⚡ 性能优化
- 🔒 安全修复
- 🧪 测试相关

---

## [Unreleased] - develop 分支

### 2025-11-10

#### ✨ 新功能
- ✨ **提醒系统增强**
  - 实现聊天中自动创建提醒（ReminderTool）
  - 支持智能时间解析（"明天下午3点"、"2小时后"等12种格式）
  - 添加稍后提醒功能（延迟5分钟）
  - 添加提醒声音（双响"叮咚"提示音）
  
- ✨ **提醒界面重构**
  - 合并"提醒列表"和"提醒历史"为单一界面
  - 添加"显示已过期"切换按钮
  - 实时统计：活跃/已禁用/已触发提醒数量
  - 已触发提醒灰色显示，视觉区分明显

- ✨ **WebSocket实时推送系统**
  - WebSocket服务端（/ws端点）
  - 提醒触发时实时推送到前端
  - 前端自动重连机制（5秒间隔）
  - 实时提醒弹窗（支持"已知道"和"稍后提醒"）
  - 浏览器原生通知（页面不在前台时）
  - 提醒声音播放（Web Audio API）

#### 🔧 技术改进
- ♻️ 重构提醒显示逻辑（过滤已触发提醒）
- 🔧 修复Tool系统user_id传递问题
- 🔧 添加API端点：`/api/reminders/{id}/snooze`
- ⚡ 优化提醒列表加载性能

#### 🧪 测试
- 🧪 创建WebSocket推送测试脚本
- 🧪 验证提醒创建、触发、延迟功能

### 2025-11-09

#### � Bug修复
- 🐛 修复记忆搜索功能：完善API返回格式和前端交互

#### ✨ 新功能
- ✨ 添加自动提交工具和开发日志系统

#### �🔧 项目初始化
- 创建开发分支 `develop`
- 设置自动提交工具
- 建立开发日志系统

---

## [0.1.0] - 2025-11-09 - 初始版本

### ✨ 核心功能
- **智能对话系统**
  - DeepSeek API 集成
  - 上下文理解和连贯对话
  - 错误重试机制（3次重试，指数退避）

- **记忆管理系统**
  - PostgreSQL 持久化存储
  - 智能记忆提取（区分事实与闲聊）
  - 标签分类（facts/general）
  - 记忆优先级（事实 > 语义 > 时间）
  - 关键词搜索功能

- **对话历史管理**
  - 会话（Session）管理
  - 消息历史记录
  - 上下文窗口控制

- **Web 界面**
  - 响应式设计
  - Markdown 渲染支持
  - 实时对话交互

### 🔧 基础设施
- **数据库**
  - NAS PostgreSQL 9.3.25 远程连接
  - 连接池管理
  - 自动重连机制

- **API 服务**
  - FastAPI 框架
  - CORS 跨域支持
  - 静态文件服务
  - RESTful API 端点

- **错误处理**
  - 装饰器模式的错误处理
  - 详细日志记录
  - 优雅降级

### 📝 文档
- README.md - 项目说明和快速开始
- NAS_POSTGRESQL_SETUP.md - 数据库设置指南
- DEEPSEEK_SETUP.md - DeepSeek API 配置
- CLAUDE_INTEGRATION.md - Claude API 集成文档
- TEST_GUIDE.md - 测试指南

### 🧪 测试
- test_agent.py - Agent 功能测试
- test_api.py - API 端点测试
- test_claude.py - Claude 集成测试
- test_nas_connection.py - 数据库连接测试
- test_retry.py - 重试机制测试

### 🔧 开发工具
- scripts/start.sh - 启动服务脚本
- scripts/setup_nas_postgresql.sh - 数据库设置脚本
- scripts/setup_api_key.sh - API 密钥配置脚本
- .gitignore - Git 忽略规则
- .env.example - 环境变量模板

### 🐛 已知问题修复
- ✅ 修复记忆污染问题（AI 存储对话记录而非事实）
- ✅ 修复记忆优先级问题（改为事实优先）
- ✅ 修复 SSH 推送问题（多账户配置）
- ✅ 清理 43 条错误的对话记录

### ⏳ 待实现功能
- 向量语义搜索（sentence-transformers 依赖问题待解决）
- 天气 API 集成
- 定时提醒功能
- 语音交互（TTS/STT）
- 移动端适配
- 多用户支持

---

## 版本说明

### 版本号规则
遵循语义化版本 (Semantic Versioning 2.0.0)：
- MAJOR.MINOR.PATCH
- MAJOR: 不兼容的 API 修改
- MINOR: 向后兼容的功能性新增
- PATCH: 向后兼容的问题修正

### 分支策略
- `main`: 稳定版本分支，只接受 PR
- `develop`: 开发分支，日常开发在此进行
- `feature/*`: 功能分支
- `hotfix/*`: 紧急修复分支

---

*本日志使用 [Keep a Changelog](https://keepachangelog.com/) 格式*
