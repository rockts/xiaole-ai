# 小乐 AI 文档索引

> 更新时间：2025-12-01  
> 当前版本：v0.9.0

---

## 📋 目录结构

### 1️⃣ 快速开始

| 文档                                     | 说明           | 状态   |
| ---------------------------------------- | -------------- | ------ |
| [README.md](README.md)                   | 文档总览和导航 | ✅ 最新 |
| [QUICK_REFERENCE.md](QUICK_REFERENCE.md) | 快速参考指南   | ✅ 最新 |
| [../README.md](../README.md)             | 项目主README   | ✅ 最新 |

### 2️⃣ 环境配置

| 文档                                               | 说明                 | 状态     |
| -------------------------------------------------- | -------------------- | -------- |
| [DEEPSEEK_SETUP.md](DEEPSEEK_SETUP.md)             | DeepSeek API 配置    | ✅ 推荐   |
| [CLAUDE_INTEGRATION.md](CLAUDE_INTEGRATION.md)     | Claude API 集成      | ✅ 可选   |
| [NAS_POSTGRESQL_SETUP.md](NAS_POSTGRESQL_SETUP.md) | NAS PostgreSQL 配置  | ✅ 必读   |
| [QWEN_VISION_SETUP.md](QWEN_VISION_SETUP.md)       | Qwen-VL 图片识别配置 | ✅ v0.7.0 |

### 3️⃣ 功能测试指南

| 文档                                             | 说明         | 版本     |
| ------------------------------------------------ | ------------ | -------- |
| [TEST_GUIDE.md](TEST_GUIDE.md)                   | 通用测试指南 | ✅ 最新   |
| [FOLLOWUP_TEST_GUIDE.md](FOLLOWUP_TEST_GUIDE.md) | 追问功能测试 | ✅ v0.3.0 |
| [VISION_TEST_GUIDE.md](VISION_TEST_GUIDE.md)     | 图片识别测试 | ✅ v0.7.0 |
| [FILE_TOOL_GUIDE.md](FILE_TOOL_GUIDE.md)         | 文件工具使用 | ✅ v0.5.0 |

### 4️⃣ 版本发布记录

| 文档                                       | 说明            | 状态     |
| ------------------------------------------ | --------------- | -------- |
| [v0.8.0_RELEASE.md](v0.8.0_RELEASE.md)     | v0.8.0 发布说明 | ✅ 最新   |
| [v0.7.1_COMPLETED.md](v0.7.1_COMPLETED.md) | v0.7.1 完成报告 | ✅ 已完成 |
| [NEXT_DEVELOPMENT.md](NEXT_DEVELOPMENT.md) | 下一步开发计划  | 📋 规划中 |
| [archived/v0.7.0/](archived/v0.7.0/)       | v0.7.0 系列文档 | 📦 已归档 |
| [archived/v0.6.0/](archived/v0.6.0/)       | v0.6.0 系列文档 | 📦 已归档 |
| [archived/v0.5.0/](archived/v0.5.0/)       | v0.5.0 系列文档 | 📦 已归档 |

### 5️⃣ 开发日志与项目状态

| 文档                                     | 说明       | 类型       |
| ---------------------------------------- | ---------- | ---------- |
| [DEVELOPMENT_LOG.md](DEVELOPMENT_LOG.md) | 开发日志   | 📝 持续更新 |
| [PROJECT_STATUS.md](PROJECT_STATUS.md)   | 项目状态   | 📊 状态跟踪 |
| [archived/issues/](archived/issues/)     | 问题修复集 | 🐛 已归档   |

### 6️⃣ 技术方案与优化

| 文档                                                   | 说明            | 领域       |
| ------------------------------------------------------ | --------------- | ---------- |
| [FRONTEND_OPTIMIZATION.md](FRONTEND_OPTIMIZATION.md)   | 前端性能优化    | ⚡ 性能     |
| [AUTO_RELOAD_GUIDE.md](AUTO_RELOAD_GUIDE.md)           | 自动重载指南    | 🔧 开发工具 |
| [KEYBOARD_SHORTCUTS.md](KEYBOARD_SHORTCUTS.md)         | 键盘快捷键      | ⌨️ 用户体验 |
| [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)               | 数据库迁移      | 💾 数据库   |
| [SEMANTIC_SEARCH_REPORT.md](SEMANTIC_SEARCH_REPORT.md) | 语义搜索报告    | 🔍 搜索     |
| [DUCKDUCKGO_LIMITATIONS.md](DUCKDUCKGO_LIMITATIONS.md) | DuckDuckGo 限制 | 🌐 搜索     |

### 7️⃣ 已归档文档

| 目录                                 | 说明             | 位置        |
| ------------------------------------ | ---------------- | ----------- |
| [archived/v0.7.0/](archived/v0.7.0/) | v0.7.0 版本文档  | 📦 已归档    |
| [archived/v0.6.0/](archived/v0.6.0/) | v0.6.0 版本文档  | 📦 已归档    |
| [archived/v0.5.0/](archived/v0.5.0/) | v0.5.0 版本文档  | 📦 已归档    |
| [archived/issues/](archived/issues/) | 历史问题修复文档 | 📦 已归档    |
| [archived/](archived/)               | 其他历史文档     | 📦 archived/ |

### 8️⃣ 架构图

| 文件                                 | 说明           |
| ------------------------------------ | -------------- |
| [architecture.png](architecture.png) | 三层智能架构图 |

---

## 🗂️ 按功能模块分类

### 💬 对话系统
- TEST_GUIDE.md
- FOLLOWUP_TEST_GUIDE.md
- v0.7.1_COMPLETED.md（追问功能优化）

### 🧠 记忆管理
- SEMANTIC_SEARCH_REPORT.md
- v0.8.0_RELEASE.md（记忆层优化）
- archived/v0.7.0/（记忆和课程表开发）

### 🔧 工具系统
- FILE_TOOL_GUIDE.md
- DUCKDUCKGO_LIMITATIONS.md
- SEARCH_INTENT_ISSUE.md

### 🖼️ 图片识别
- QWEN_VISION_SETUP.md
- VISION_TEST_GUIDE.md
- v0.8.0_RELEASE.md（图片记忆优化）

### 🗣️ 语音功能
- BAIDU_VOICE_SETUP.md
- VOICE_USER_GUIDE.md
- VOICE_QUICK_TEST.md
- archived/issues/VOICE_NETWORK_ERROR_SOLUTION.md

### ⚙️ 配置部署
- DEEPSEEK_SETUP.md
- CLAUDE_INTEGRATION.md
- NAS_POSTGRESQL_SETUP.md
- MIGRATION_GUIDE.md

---

## 📌 推荐阅读顺序

### 新用户入门
1. ../README.md（项目介绍）
2. QUICK_REFERENCE.md（快速参考）
3. DEEPSEEK_SETUP.md（API配置）
4. NAS_POSTGRESQL_SETUP.md（数据库配置）
5. TEST_GUIDE.md（功能测试）

### 开发者深入
1. architecture.png（架构理解）
2. DEVELOPMENT_LOG.md（开发历程）
3. v0.8.0_RELEASE.md（最新版本）
4. PROJECT_STATUS.md（项目现状）
5. NEXT_DEVELOPMENT.md（未来计划）

---

## 🔄 文档维护说明

- ✅ **最新**：内容准确，与当前版本一致
- 🚧 **部分实现**：规划部分已实现，部分待开发
- 📋 **规划中**：未来版本的开发计划
- 📦 **已归档**：历史文档，仅供参考
- ⚠️ **已废弃**：不再使用，建议查看新文档

---

## 📝 文档贡献

如需添加或更新文档，请：
1. 在对应目录创建 Markdown 文件
2. 更新本索引文件
3. 提交时说明文档用途和版本
4. 遵循现有文档的格式规范
