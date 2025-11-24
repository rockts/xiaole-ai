# Session Notes - 2025-11-24

## 🎯 Session Objectives
- Fix "Zombie Reminders" bug (reminders reappearing after confirmation).
- Implement mobile adaptation for the frontend.
- Fix "Sleep immediately" reminder issue.

## 🛠️ Changes Made

### 1. Bug Fix: Zombie Reminders
- **Issue**: Reminders would reappear after confirmation due to multi-tab synchronization lag causing "auto-snooze" to trigger in background tabs.
- **Fix**:
    - **Backend**: Updated `backend/reminder_manager.py` to broadcast `reminder_confirmed` event via WebSocket when a reminder is confirmed.
    - **Frontend**: Updated `frontend/src/components/common/ReminderNotification.vue` to listen for `reminder_confirmed` event and close the popup immediately across all tabs.

### 2. Feature: Mobile Adaptation
- **Objective**: Optimize UI for mobile devices (responsive layout, touch targets, viewport handling).
- **Changes**:
    - **Frontend Styles (`frontend/src/assets/styles/app.css`)**:
        - Added media queries for screens smaller than 768px.
        - Implemented a floating overlay sidebar for mobile.
        - Adjusted chat container padding and input container positioning (fixed to bottom).
        - Increased message bubble max-width and adjusted padding.
        - Ensured message toolbar is always visible on mobile.
    - **Sidebar Component (`frontend/src/components/layout/SidebarModern.vue`)**:
        - Added logic to default sidebar to collapsed on mobile.
        - Fixed overlay visibility and interaction.
    - **TopBar Component (`frontend/src/components/layout/TopBar.vue`)**:
        - Adjusted title input width and font size for mobile.
    - **HTML Template (`frontend/index.html`)**:
        - Updated viewport meta tag to include `interactive-widget=resizes-content` for better keyboard handling on mobile.

### 3. Bug Fix: "Sleep Immediately" Reminder
- **Issue**: A persistent reminder with content "立马睡觉" (ID 77) kept triggering.
- **Fix**:
    - Identified the reminder ID using `scripts/check_sleep_reminders.py`.
    - Created and ran `scripts/delete_reminder_77.py` to delete the specific reminder from the database.

## 📝 Key Files Modified
- `backend/reminder_manager.py`
- `frontend/src/components/common/ReminderNotification.vue`
- `frontend/src/assets/styles/app.css`
- `frontend/src/components/layout/SidebarModern.vue`
- `frontend/src/components/layout/TopBar.vue`
- `frontend/index.html`

## 🚀 Next Steps
- Verify mobile adaptation on actual devices.
- Continue monitoring reminder system stability.

## 🧾 本次会话快照（2025-11-21）

- **目标**：修复记忆"失忆"问题、前端会话显示不全问题，并解答用户关于记忆机制的疑问。
- **已完成**：
  - **前端修复**：
    - `frontend/src/stores/chat.js` & `frontend/src/services/api.js`：加载会话时请求 500 条消息（原默认 50），解决长对话截断问题。
    - `main.py`：后端接口 `get_session` 增加 `limit` 参数支持，默认提升至 200。
  - **记忆修复**：
    - 诊断出"幽灵记忆"问题：手动 SQL 插入的课程表记忆有 `schedule` 标签，但未建立向量索引，导致语义搜索失效。
    - `agent.py`：修改 `_think_with_context` 方法，**强制检索 `schedule` 标签**的记忆，并赋予高优先级（仅次于图片记忆）。
  - **机制澄清**：
    - 向用户解释了手动修复的原因（绕过失效索引）。
    - 解释了自动清理机制（只清理过期摘要，不清理 Facts/Schedule）。
    - 确认了图片记忆的"特权通道"逻辑。
  - **文档更新**：更新了 `PROGRESS.md` 和 `README.md`。

- **关键文件**：
  - `agent.py`（记忆检索逻辑）
  - `main.py`（API 接口）
  - `frontend/src/stores/chat.js`（前端状态）

- **快速恢复（重启后直接运行）**：
  ```bash
  # 后端
  cd /Users/rockts/Dev/xiaole-ai
  ./restart.sh

  # 前端
  source ~/.nvm/nvm.sh && nvm use 20
  cd /Users/rockts/Dev/xiaole-ai/frontend
  npm run dev
  ```

## 📌 标准启动流程（已验证）

### 后端启动
```bash
cd /Users/rockts/Dev/xiaole-ai
./restart.sh
```
- 端口: 8000
- 虚拟环境: `.venv` (Python 3.13.5)
- 依赖: requirements.txt

### 前端启动
```bash
source ~/.nvm/nvm.sh && nvm use 20
cd /Users/rockts/Dev/xiaole-ai/frontend
npm run dev
```
- 端口: 3000
- Node 版本: v20.17.0
- 包管理器: npm v11.3.0

---

## 🔧 当前项目结构

### 后端关键文件
- `main.py` - FastAPI 主入口
- `conversation.py` - 对话管理
- `memory.py` - 记忆系统
- `agent.py` - AI 代理（核心逻辑）
- `tool_manager.py` - 工具管理
- `db_setup.py` - 数据库初始化

### 前端关键目录
- `frontend/src/views/ChatView.vue` - 聊天主视图
- `frontend/src/components/` - 组件库
- `frontend/src/stores/chat.js` - Pinia 状态管理
- `frontend/src/services/api.js` - API 封装

---

## 📝 最近改动记录

### 2025-11-22 分享卡片 UI 修复与记忆调试
**主要文件**: `frontend/src/components/common/ShareDialog.vue`, `backend/agent.py`

#### ✅ 分享卡片 UI 修复
- 增大关闭按钮尺寸至 56px，确保触控友好。
- 设置关闭按钮不透明度为 1，修复视觉问题。
- 修复 Markdown 渲染问题，确保内容正确显示。

#### ✅ 记忆丢失问题调试
- 确认子女信息（姓名、体型）在数据库中缺失，需后续数据填充。
- 优化 `agent.py` 中的记忆提取逻辑，增加对性别和体型的关注。
- 验证图片记忆机制，确认架构支持但历史数据为空。

#### 🔧 技术细节
```js
// agent.py 片段
if '子女' in memory_tags:
    # 提取子女相关信息
    pass
```
```css
/* ShareDialog.vue 样式修复 */
.close-button {
  width: 56px;
  height: 56px;
  opacity: 1;
}
```

---

**最后更新**: 2025-11-22
**会话状态**: 小乐正常运行，分享卡片 UI 修复，记忆调试中

## 🧾 本次会话快照（2025-11-24）

- **目标**：修复记忆混淆问题（儿子/女儿名字混淆），并提交所有代码变更。
- **已完成**：
  - **记忆修复**：
    - 诊断出数据库中存在冲突的记忆条目（儿子名字被错误关联到女儿）。
    - 创建并运行 `scripts/fix_memory_data.py` 清理了错误的记忆条目，并确认了正确的家庭成员信息。
    - 优化 `backend/agent.py` 中的家庭成员关键词提取逻辑，增加对"姑娘"、"闺女"等口语词汇的支持。
  - **调试工具**：
    - 创建 `scripts/debug_chat_session.py` 用于快速查看特定会话的完整历史。
    - 创建 `scripts/check_daughter_name.py` 用于诊断特定记忆问题。
  - **前端优化**（上一轮）：
    - 完成了拖拽上传功能的 UI 实现。

- **关键文件**：
  - `backend/agent.py`（逻辑优化）
  - `scripts/fix_memory_data.py`（数据修复脚本）
  - `scripts/debug_chat_session.py`（调试工具）

- **快速恢复**：
  - 记忆已修复，无需额外操作。
  - 如需再次检查记忆，可运行：
   
  # 后端
  cd /Users/rockts/Dev/xiaole-ai
  ./restart.sh

  # 前端
  source ~/.nvm/nvm.sh && nvm use 20
  cd /Users/rockts/Dev/xiaole-ai/frontend
  npm run dev
  ```

## 📌 标准启动流程（已验证）

### 后端启动
```bash
cd /Users/rockts/Dev/xiaole-ai
./restart.sh
```
- 端口: 8000
- 虚拟环境: `.venv` (Python 3.13.5)
- 依赖: requirements.txt

### 前端启动
```bash
source ~/.nvm/nvm.sh && nvm use 20
cd /Users/rockts/Dev/xiaole-ai/frontend
npm run dev
```
- 端口: 3000
- Node 版本: v20.17.0
- 包管理器: npm v11.3.0

---

## 🔧 当前项目结构

### 后端关键文件
- `main.py` - FastAPI 主入口
- `conversation.py` - 对话管理
- `memory.py` - 记忆系统
- `agent.py` - AI 代理（核心逻辑）
- `tool_manager.py` - 工具管理
- `db_setup.py` - 数据库初始化

### 前端关键目录
- `frontend/src/views/ChatView.vue` - 聊天主视图
- `frontend/src/components/` - 组件库
- `frontend/src/stores/chat.js` - Pinia 状态管理
- `frontend/src/services/api.js` - API 封装

---

## 📝 最近改动记录

### 2025-11-22 分享卡片 UI 修复与记忆调试
**主要文件**: `frontend/src/components/common/ShareDialog.vue`, `backend/agent.py`

#### ✅ 分享卡片 UI 修复
- 增大关闭按钮尺寸至 56px，确保触控友好。
- 设置关闭按钮不透明度为 1，修复视觉问题。
- 修复 Markdown 渲染问题，确保内容正确显示。

#### ✅ 记忆丢失问题调试
- 确认子女信息（姓名、体型）在数据库中缺失，需后续数据填充。
- 优化 `agent.py` 中的记忆提取逻辑，增加对性别和体型的关注。
- 验证图片记忆机制，确认架构支持但历史数据为空。

#### 🔧 技术细节
```js
// agent.py 片段
if '子女' in memory_tags:
    # 提取子女相关信息
    pass
```
```css
/* ShareDialog.vue 样式修复 */
.close-button {
  width: 56px;
  height: 56px;
  opacity: 1;
}
```

---

**最后更新**: 2025-11-22
**会话状态**: 小乐正常运行，分享卡片 UI 修复，记忆调试中

## 🧾 本次会话快照（2025-11-21）

- **目标**：修复记忆"失忆"问题、前端会话显示不全问题，并解答用户关于记忆机制的疑问。
- **已完成**：
  - **前端修复**：
    - `frontend/src/stores/chat.js` & `frontend/src/services/api.js`：加载会话时请求 500 条消息（原默认 50），解决长对话截断问题。
    - `main.py`：后端接口 `get_session` 增加 `limit` 参数支持，默认提升至 200。
  - **记忆修复**：
    - 诊断出"幽灵记忆"问题：手动 SQL 插入的课程表记忆有 `schedule` 标签，但未建立向量索引，导致语义搜索失效。
    - `agent.py`：修改 `_think_with_context` 方法，**强制检索 `schedule` 标签**的记忆，并赋予高优先级（仅次于图片记忆）。
  - **机制澄清**：
    - 向用户解释了手动修复的原因（绕过失效索引）。
    - 解释了自动清理机制（只清理过期摘要，不清理 Facts/Schedule）。
    - 确认了图片记忆的"特权通道"逻辑。
  - **文档更新**：更新了 `PROGRESS.md` 和 `README.md`。

- **关键文件**：
  - `agent.py`（记忆检索逻辑）
  - `main.py`（API 接口）
  - `frontend/src/stores/chat.js`（前端状态）

- **快速恢复（重启后直接运行）**：
  ```bash
  # 后端
  cd /Users/rockts/Dev/xiaole-ai
  ./restart.sh

  # 前端
  source ~/.nvm/nvm.sh && nvm use 20
  cd /Users/rockts/Dev/xiaole-ai/frontend
  npm run dev
  ```

## 📌 标准启动流程（已验证）

### 后端启动
```bash
cd /Users/rockts/Dev/xiaole-ai
./restart.sh
```
- 端口: 8000
- 虚拟环境: `.venv` (Python 3.13.5)
- 依赖: requirements.txt

### 前端启动
```bash
source ~/.nvm/nvm.sh && nvm use 20
cd /Users/rockts/Dev/xiaole-ai/frontend
npm run dev
```
- 端口: 3000
- Node 版本: v20.17.0
- 包管理器: npm v11.3.0

---

## 🔧 当前项目结构

### 后端关键文件
- `main.py` - FastAPI 主入口
- `conversation.py` - 对话管理
- `memory.py` - 记忆系统
- `agent.py` - AI 代理（核心逻辑）
- `tool_manager.py` - 工具管理
- `db_setup.py` - 数据库初始化

### 前端关键目录
- `frontend/src/views/ChatView.vue` - 聊天主视图
- `frontend/src/components/` - 组件库
- `frontend/src/stores/chat.js` - Pinia 状态管理
- `frontend/src/services/api.js` - API 封装

---

## 📝 最近改动记录

### 2025-11-22 分享卡片 UI 修复与记忆调试
**主要文件**: `frontend/src/components/common/ShareDialog.vue`, `backend/agent.py`

#### ✅ 分享卡片 UI 修复
- 增大关闭按钮尺寸至 56px，确保触控友好。
- 设置关闭按钮不透明度为 1，修复视觉问题。
- 修复 Markdown 渲染问题，确保内容正确显示。

#### ✅ 记忆丢失问题调试
- 确认子女信息（姓名、体型）在数据库中缺失，需后续数据填充。
- 优化 `agent.py` 中的记忆提取逻辑，增加对性别和体型的关注。
- 验证图片记忆机制，确认架构支持但历史数据为空。

#### 🔧 技术细节
```js
// agent.py 片段
if '子女' in memory_tags:
    # 提取子女相关信息
    pass
```
```css
/* ShareDialog.vue 样式修复 */
.close-button {
  width: 56px;
  height: 56px;
  opacity: 1;
}
```

---

**最后更新**: 2025-11-22
**会话状态**: 小乐正常运行，分享卡片 UI 修复，记忆调试中

## 🧾 本次会话快照（2025-11-21）

- **目标**：修复记忆"失忆"问题、前端会话显示不全问题，并解答用户关于记忆机制的疑问。
- **已完成**：
  - **前端修复**：
    - `frontend/src/stores/chat.js` & `frontend/src/services/api.js`：加载会话时请求 500 条消息（原默认 50），解决长对话截断问题。
    - `main.py`：后端接口 `get_session` 增加 `limit` 参数支持，默认提升至 200。
  - **记忆修复**：
    - 诊断出"幽灵记忆"问题：手动 SQL 插入的课程表记忆有 `schedule` 标签，但未建立向量索引，导致语义搜索失效。
    - `agent.py`：修改 `_think_with_context` 方法，**强制检索 `schedule` 标签**的记忆，并赋予高优先级（仅次于图片记忆）。
  - **机制澄清**：
    - 向用户解释了手动修复的原因（绕过失效索引）。
    - 解释了自动清理机制（只清理过期摘要，不清理 Facts/Schedule）。
    - 确认了图片记忆的"特权通道"逻辑。
  - **文档更新**：更新了 `PROGRESS.md` 和 `README.md`。

- **关键文件**：
  - `agent.py`（记忆检索逻辑）
  - `main.py`（API 接口）
  - `frontend/src/stores/chat.js`（前端状态）

- **快速恢复（重启后直接运行）**：
  ```bash
  # 后端
  cd /Users/rockts/Dev/xiaole-ai
  ./restart.sh

  # 前端
  source ~/.nvm/nvm.sh && nvm use 20
  cd /Users/rockts/Dev/xiaole-ai/frontend
  npm run dev
  ```

## 📌 标准启动流程（已验证）

### 后端启动
```bash
cd /Users/rockts/Dev/xiaole-ai
./restart.sh
```
- 端口: 8000
- 虚拟环境: `.venv` (Python 3.13.5)
- 依赖: requirements.txt

### 前端启动
```bash
source ~/.nvm/nvm.sh && nvm use 20
cd /Users/rockts/Dev/xiaole-ai/frontend
npm run dev
```
- 端口: 3000
- Node 版本: v20.17.0
- 包管理器: npm v11.3.0

---

## 🔧 当前项目结构

### 后端关键文件
- `main.py` - FastAPI 主入口
- `conversation.py` - 对话管理
- `memory.py` - 记忆系统
- `agent.py` - AI 代理（核心逻辑）
- `tool_manager.py` - 工具管理
- `db_setup.py` - 数据库初始化

### 前端关键目录
- `frontend/src/views/ChatView.vue` - 聊天主视图
- `frontend/src/components/` - 组件库
- `frontend/src/stores/chat.js` - Pinia 状态管理
- `frontend/src/services/api.js` - API 封装

---

## 📝 最近改动记录

### 2025-11-22 分享卡片 UI 修复与记忆调试
**主要文件**: `frontend/src/components/common/ShareDialog.vue`, `backend/agent.py`

#### ✅ 分享卡片 UI 修复
- 增大关闭按钮尺寸至 56px，确保触控友好。
- 设置关闭按钮不透明度为 1，修复视觉问题。
- 修复 Markdown 渲染问题，确保内容正确显示。

#### ✅ 记忆丢失问题调试
- 确认子女信息（姓名、体型）在数据库中缺失，需后续数据填充。
- 优化 `agent.py` 中的记忆提取逻辑，增加对性别和体型的关注。
- 验证图片记忆机制，确认架构支持但历史数据为空。

#### 🔧 技术细节
```js
// agent.py 片段
if '子女' in memory_tags:
    # 提取子女相关信息
    pass
```
```css
/* ShareDialog.vue 样式修复 */
.close-button {
  width: 56px;
  height: 56px;
  opacity: 1;
}
```

---

**最后更新**: 2025-11-22
**会话状态**: 小乐正常运行，分享卡片 UI 修复，记忆调试中

## 🧾 本次会话快照（2025-11-21）

- **目标**：修复记忆"失忆"问题、前端会话显示不全问题，并解答用户关于记忆机制的疑问。
- **已完成**：
  - **前端修复**：
    - `frontend/src/stores/chat.js` & `frontend/src/services/api.js`：加载会话时请求 500 条消息（原默认 50），解决长对话截断问题。
    - `main.py`：后端接口 `get_session` 增加 `limit` 参数支持，默认提升至 200。
  - **记忆修复**：
    - 诊断出"幽灵记忆"问题：手动 SQL 插入的课程表记忆有 `schedule` 标签，但未建立向量索引，导致语义搜索失效。
    - `agent.py`：修改 `_think_with_context` 方法，**强制检索 `schedule` 标签**的记忆，并赋予高优先级（仅次于图片记忆）。
  - **机制澄清**：
    - 向用户解释了手动修复的原因（绕过失效索引）。
    - 解释了自动清理机制（只清理过期摘要，不清理 Facts/Schedule）。
    - 确认了图片记忆的"特权通道"逻辑。
  - **文档更新**：更新了 `PROGRESS.md` 和 `README.md`。

- **关键文件**：
  - `agent.py`（记忆检索逻辑）
  - `main.py`（API 接口）
  - `frontend/src/stores/chat.js`（前端状态）

- **快速恢复（重启后直接运行）**：
  ```bash
  # 后端
  cd /Users/rockts/Dev/xiaole-ai
  ./restart.sh

  # 前端
  source ~/.nvm/nvm.sh && nvm use 20
  cd /Users/rockts/Dev/xiaole-ai/frontend
  npm run dev
  ```

## 📌 标准启动流程（已验证）

### 后端启动
```bash
cd /Users/rockts/Dev/xiaole-ai
./restart.sh
```
- 端口: 8000
- 虚拟环境: `.venv` (Python 3.13.5)
- 依赖: requirements.txt

### 前端启动
```bash
source ~/.nvm/nvm.sh && nvm use 20
cd /Users/rockts/Dev/xiaole-ai/frontend
npm run dev
```
- 端口: 3000
- Node 版本: v20.17.0
- 包管理器: npm v11.3.0

---

## 🔧 当前项目结构

### 后端关键文件
- `main.py` - FastAPI 主入口
- `conversation.py` - 对话管理
- `memory.py` - 记忆系统
- `agent.py` - AI 代理（核心逻辑）
- `tool_manager.py` - 工具管理
- `db_setup.py` - 数据库初始化

### 前端关键目录
- `frontend/src/views/ChatView.vue` - 聊天主视图
- `frontend/src/components/` - 组件库
- `frontend/src/stores/chat.js` - Pinia 状态管理
- `frontend/src/services/api.js` - API 封装

---

## 📝 最近改动记录

### 2025-11-22 分享卡片 UI 修复与记忆调试
**主要文件**: `frontend/src/components/common/ShareDialog.vue`, `backend/agent.py`

#### ✅ 分享卡片 UI 修复
- 增大关闭按钮尺寸至 56px，确保触控友好。
- 设置关闭按钮不透明度为 1，修复视觉问题。
- 修复 Markdown 渲染问题，确保内容正确显示。

#### ✅ 记忆丢失问题调试
- 确认子女信息（姓名、体型）在数据库中缺失，需后续数据填充。
- 优化 `agent.py` 中的记忆提取逻辑，增加对性别和体型的关注。
- 验证图片记忆机制，确认架构支持但历史数据为空。

#### 🔧 技术细节
```js
// agent.py 片段
if '子女' in memory_tags:
    # 提取子女相关信息
    pass
```
```css
/* ShareDialog.vue 样式修复 */
.close-button {
  width: 56px;
  height: 56px;
  opacity: 1;
}
```

---

**最后更新**: 2025-11-22
**会话状态**: 小乐正常运行，分享卡片 UI 修复，记忆调试中

## 🧾 本次会话快照（2025-11-21）

- **目标**：修复记忆"失忆"问题、前端会话显示不全问题，并解答用户关于记忆机制的疑问。
- **已完成**：
  - **前端修复**：
    - `frontend/src/stores/chat.js` & `frontend/src/services/api.js`：加载会话时请求 500 条消息（原默认 50），解决长对话截断问题。
    - `main.py`：后端接口 `get_session` 增加 `limit` 参数支持，默认提升至 200。
  - **记忆修复**：
    - 诊断出"幽灵记忆"问题：手动 SQL 插入的课程表记忆有 `schedule` 标签，但未建立向量索引，导致语义搜索失效。
    - `agent.py`：修改 `_think_with_context` 方法，**强制检索 `schedule` 标签**的记忆，并赋予高优先级（仅次于图片记忆）。
  - **机制澄清**：
    - 向用户解释了手动修复的原因（绕过失效索引）。
    - 解释了自动清理机制（只清理过期摘要，不清理 Facts/Schedule）。
    - 确认了图片记忆的"特权通道"逻辑。
  - **文档更新**：更新了 `PROGRESS.md` 和 `README.md`。

- **关键文件**：
  - `agent.py`（记忆检索逻辑）
  - `main.py`（API 接口）
  - `frontend/src/stores/chat.js`（前端状态）

- **快速恢复（重启后直接运行）**：
  ```bash
  # 后端
  cd /Users/rockts/Dev/xiaole-ai
  ./restart.sh

  # 前端
  source ~/.nvm/nvm.sh && nvm use 20
  cd /Users/rockts/Dev/xiaole-ai/frontend
  npm run dev
  ```

## 📌 标准启动流程（已验证）

### 后端启动
```bash
cd /Users/rockts/Dev/xiaole-ai
./restart.sh
```
- 端口: 8000
- 虚拟环境: `.venv` (Python 3.13.5)
- 依赖: requirements.txt

### 前端启动
```bash
source ~/.nvm/nvm.sh && nvm use 20
cd /Users/rockts/Dev/xiaole-ai/frontend
npm run dev
```
- 端口: 3000
- Node 版本: v20.17.0
- 包管理器: npm v11.3.0

---

## 🔧 当前项目结构

### 后端关键文件
- `main.py` - FastAPI 主入口
- `conversation.py` - 对话管理
- `memory.py` - 记忆系统
- `agent.py` - AI 代理（核心逻辑）
- `tool_manager.py` - 工具管理
- `db_setup.py` - 数据库初始化

### 前端关键目录
- `frontend/src/views/ChatView.vue` - 聊天主视图
- `frontend/src/components/` - 组件库
- `frontend/src/stores/chat.js` - Pinia 状态管理
- `frontend/src/services/api.js` - API 封装

---

## 📝 最近改动记录

### 2025-11-22 分享卡片 UI 修复与记忆调试
**主要文件**: `frontend/src/components/common/ShareDialog.vue`, `backend/agent.py`

#### ✅ 分享卡片 UI 修复
- 增大关闭按钮尺寸至 56px，确保触控友好。
- 设置关闭按钮不透明度为 1，修复视觉问题。
- 修复 Markdown 渲染问题，确保内容正确显示。

#### ✅ 记忆丢失问题调试
- 确认子女信息（姓名、体型）在数据库中缺失，需后续数据填充。
- 优化 `agent.py` 中的记忆提取逻辑，增加对性别和体型的关注。
- 验证图片记忆机制，确认架构支持但历史数据为空。

#### 🔧 技术细节
```js
// agent.py 片段
if '子女' in memory_tags:
    # 提取子女相关信息
    pass
```
```css
/* ShareDialog.vue 样式修复 */
.close-button {
  width: 56px;
  height: 56px;
  opacity: 1;
}
```

---

**最后更新**: 2025-11-22
**会话状态**: 小乐正常运行，分享卡片 UI 修复，记忆调试中

## 🧾 本次会话快照（2025-11-21）

- **目标**：修复记忆"失忆"问题、前端会话显示不全问题，并解答用户关于记忆机制的疑问。
- **已完成**：
  - **前端修复**：
    - `frontend/src/stores/chat.js` & `frontend/src/services/api.js`：加载会话时请求 500 条消息（原默认 50），解决长对话截断问题。
    - `main.py`：后端接口 `get_session` 增加 `limit` 参数支持，默认提升至 200。
  - **记忆修复**：
    - 诊断出"幽灵记忆"问题：手动 SQL 插入的课程表记忆有 `schedule` 标签，但未建立向量索引，导致语义搜索失效。
    - `agent.py`：修改 `_think_with_context` 方法，**强制检索 `schedule` 标签**的记忆，并赋予高优先级（仅次于图片记忆）。
  - **机制澄清**：
    - 向用户解释了手动修复的原因（绕过失效索引）。
    - 解释了自动清理机制（只清理过期摘要，不清理 Facts/Schedule）。
    - 确认了图片记忆的"特权通道"逻辑。
  - **文档更新**：更新了 `PROGRESS.md` 和 `README.md`。

- **关键文件**：
  - `agent.py`（记忆检索逻辑）
  - `main.py`（API 接口）
  - `frontend/src/stores/chat.js`（前端状态）

- **快速恢复（重启后直接运行）**：
  ```bash
  # 后端
  cd /Users/rockts/Dev/xiaole-ai
  ./restart.sh

  # 前端
  source ~/.nvm/nvm.sh && nvm use 20
  cd /Users/rockts/Dev/xiaole-ai/frontend
  npm run dev
  ```

## 📌 标准启动流程（已验证）

### 后端启动
```bash
cd /Users/rockts/Dev/xiaole-ai
./restart.sh
```
- 端口: 8000
- 虚拟环境: `.venv` (Python 3.13.5)
- 依赖: requirements.txt

### 前端启动
```bash
source ~/.nvm/nvm.sh && nvm use 20
cd /Users/rockts/Dev/xiaole-ai/frontend
npm run dev
```
- 端口: 3000
- Node 版本: v20.17.0
- 包管理器: npm v11.3.0

---

## 🔧 当前项目结构

### 后端关键文件
- `main.py` - FastAPI 主入口
- `conversation.py` - 对话管理
- `memory.py` - 记忆系统
- `agent.py` - AI 代理（核心逻辑）
- `tool_manager.py` - 工具管理
- `db_setup.py` - 数据库初始化

### 前端关键目录
- `frontend/src/views/ChatView.vue` - 聊天主视图
- `frontend/src/components/` - 组件库
- `frontend/src/stores/chat.js` - Pinia 状态管理
- `frontend/src/services/api.js` - API 封装

---

## 📝 最近改动记录

### 2025-11-22 分享卡片 UI 修复与记忆调试
**主要文件**: `frontend/src/components/common/ShareDialog.vue`, `backend/agent.py`

#### ✅ 分享卡片 UI 修复
- 增大关闭按钮尺寸至 56px，确保触控友好。
- 设置关闭按钮不透明度为 1，修复视觉问题。
- 修复 Markdown 渲染问题，确保内容正确显示。

#### ✅ 记忆丢失问题调试
- 确认子女信息（姓名、体型）在数据库中缺失，需后续数据填充。
- 优化 `agent.py` 中的记忆提取逻辑，增加对性别和体型的关注。
- 验证图片记忆机制，确认架构支持但历史数据为空。

#### 🔧 技术细节
```js
// agent.py 片段
if '子女' in memory_tags:
    # 提取子女相关信息
    pass
```
```css
/* ShareDialog.vue 样式修复 */
.close-button {
  width: 56px;
  height: 56px;
  opacity: 1;
}
```

---

**最后更新**: 2025-11-22
**会话状态**: 小乐正常运行，分享卡片 UI 修复，记忆调试中

## 🧾 本次会话快照（2025-11-21）

- **目标**：修复记忆"失忆"问题、前端会话显示不全问题，并解答用户关于记忆机制的疑问。
- **已完成**：
  - **前端修复**：
    - `frontend/src/stores/chat.js` & `frontend/src/services/api.js`：加载会话时请求 500 条消息（原默认 50），解决长对话截断问题。
    - `main.py`：后端接口 `get_session` 增加 `limit` 参数支持，默认提升至 200。
  - **记忆修复**：
    - 诊断出"幽灵记忆"问题：手动 SQL 插入的课程表记忆有 `schedule` 标签，但未建立向量索引，导致语义搜索失效。
    - `agent.py`：修改 `_think_with_context` 方法，**强制检索 `schedule` 标签**的记忆，并赋予高优先级（仅次于图片记忆）。
  - **机制澄清**：
    - 向用户解释了手动修复的原因（绕过失效索引）。
    - 解释了自动清理机制（只清理过期摘要，不清理 Facts/Schedule）。
    - 确认了图片记忆的"特权通道"逻辑。
  - **文档更新**：更新了 `PROGRESS.md` 和 `README.md`。

- **关键文件**：
  - `agent.py`（记忆检索逻辑）
  - `main.py`（API 接口）
  - `frontend/src/stores/chat.js`（前端状态）

- **快速恢复（重启后直接运行）**：
  ```bash
  # 后端
  cd /Users/rockts/Dev/xiaole-ai
  ./restart.sh

  # 前端
  source ~/.nvm/nvm.sh && nvm use 20
  cd /Users/rockts/Dev/xiaole-ai/frontend
  npm run dev
  ```

## 📌 标准启动流程（已验证）

### 后端启动
```bash
cd /Users/rockts/Dev/xiaole-ai
./restart.sh
```
- 端口: 8000
- 虚拟环境: `.venv` (Python 3.13.5)
- 依赖: requirements.txt

### 前端启动
```bash
source ~/.nvm/nvm.sh && nvm use 20
cd /Users/rockts/Dev/xiaole-ai/frontend
npm run dev
```
- 端口: 3000
- Node 版本: v20.17.0
- 包管理器: npm v11.3.0

---

## 🔧 当前项目结构

### 后端关键文件
- `main.py` - FastAPI 主入口
- `conversation.py` - 对话管理
- `memory.py` - 记忆系统
- `agent.py` - AI 代理（核心逻辑）
- `tool_manager.py` - 工具管理
- `db_setup.py` - 数据库初始化

### 前端关键目录
- `frontend/src/views/ChatView.vue` - 聊天主视图
- `frontend/src/components/` - 组件库
- `frontend/src/stores/chat.js` - Pinia 状态管理
- `frontend/src/services/api.js` - API 封装

## 🧾 本次会话快照（2025-11-24）

- **目标**：修复记忆混淆问题，完善移动端交互体验。
- **已完成**：
  - **记忆修复**：
    - 诊断并修复了儿子/女儿名字混淆的记忆数据 (`scripts/fix_memory_data.py`)。
    - 优化 `backend/agent.py` 家庭成员关键词提取逻辑，增加对"姑娘"、"闺女"等口语词汇的支持。
  - **前端交互优化**：
    - **移动端图片预览**：在 `ChatView.vue` 中实现了双指缩放 (Pinch-to-zoom) 和单指拖拽 (Pan) 的触摸手势支持，完善了移动端图片查看体验。
  - **调试工具**：
    - 创建 `scripts/debug_chat_session.py` 用于快速查看特定会话的完整历史。
    - 创建 `scripts/check_daughter_name.py` 用于诊断特定记忆问题。

- **关键文件**：
  - `frontend/src/views/ChatView.vue`（触摸手势）
  - `backend/agent.py`（逻辑优化）
  - `scripts/fix_memory_data.py`（数据修复脚本）

- **快速恢复**：
  - 记忆已修复，无需额外操作。
  - 前端已更新，需确保开发服务器运行中。
