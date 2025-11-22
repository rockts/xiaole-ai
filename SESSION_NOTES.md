# 小乐 AI 开发会话记录

> **重要**: VS Code 重启后参考此文件恢复上下文

## 🧾 本次会话快照（2025-11-22 补充）

- **目标**：继续执行开发计划，重点修复已知问题并适配移动端。
- **已完成**：
  - **移动端适配**：
    - `TopBar.vue`：添加移动端汉堡菜单按钮（仅在小屏幕显示）。
    - `SidebarModern.vue`：实现移动端抽屉式侧边栏（固定定位 + 遮罩层 + 滑动动画）。
    - `ChatView.vue`：优化移动端布局（减少内边距、增加气泡宽度至 85%、图片自适应）。
  - **Bug 修复**：
    - 修复 `ChatView.vue` 中 `submitFeedback` 调用参数错误导致反馈无法提交的问题。
  - **依赖安装**：
    - 安装 `face_recognition` 和 `opencv-python-headless`，为后续人脸识别功能做准备。

- **待办事项 (Next Steps)**：
  - **人脸识别**：开始实现 Phase 1（本地离线识别）。
  - **测试**：验证移动端交互体验。

- **关键文件**：
  - `frontend/src/components/layout/SidebarModern.vue`
  - `frontend/src/views/ChatView.vue`

## 🧾 本次会话快照（2025-11-22）

- **目标**：修复分享卡片 UI、调试记忆丢失问题（子女信息、图片记忆）、规划人脸识别功能。
- **已完成**：
  - **UI 修复**：
    - `ShareDialog.vue`：关闭按钮尺寸增大至 56px，不透明度设为 1，修复 Markdown 渲染。
  - **记忆调试**：
    - 确认子女信息（姓名、体型）在数据库中缺失。
    - 优化 `agent.py` 提取逻辑，增加对性别和体型的关注。
    - 验证图片记忆机制：确认架构支持，但历史数据为空。
  - **功能规划**：
    - 确定采用 **方案 A（本地离线识别）** 实现未来的人脸/视频识别功能。
    - 添加了 `face_recognition` 和 `opencv-python-headless` 到依赖列表。
  - **文档更新**：更新了 `CHANGELOG.md` 和 `README.md`。

- **待办事项 (Next Steps)**：
  - **测试修复**：全面测试 Vue 重构后的功能（今日反馈"有用但有问题"）。
  - **移动端适配**：优化移动端布局和交互。
  - **人脸识别**：安装新依赖，搭建本地人脸库（Phase 1）。

- **关键文件**：
  - `backend/agent.py`
  - `frontend/src/components/common/ShareDialog.vue`
  - `requirements.txt`

- **快速恢复**：
  ```bash
  # 安装新依赖
  pip install -r requirements.txt
  
  # 重启后端
  ./restart.sh
  ```

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
