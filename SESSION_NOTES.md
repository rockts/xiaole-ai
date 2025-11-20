# 小乐 AI 开发会话记录

> **重要**: VS Code 重启后参考此文件恢复上下文

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

### 2025-11-21 记忆与会话修复
**主要文件**: `agent.py`, `main.py`, `frontend/src/stores/chat.js`

#### ✅ 记忆检索增强
- 在 `agent.py` 中增加对 `schedule` 标签的显式检索。
- 解决了手动 SQL 插入数据无法被语义搜索召回的问题。

#### ✅ 会话历史完整性
- 前端加载历史消息数量从 50 提升至 500。
- 后端接口支持自定义 limit 参数。

---

**最后更新**: 2025-11-21
**会话状态**: 小乐正常运行，记忆功能已修复，前端显示正常。

## 🧾 本次会话快照（2025-11-20）

- 目标：保存当前对话与实现进度，便于重启恢复。
- 已完成：
  - 发送图标改为白底黑色向上箭头，提升对比度
  - 三态主按钮：语音/发送/停止，智能切换
  - 思考阶段白色扩张圆点动画（status=thinking）
  - 逐字打字显示与闪烁光标（status=typing→done）
  - 停止生成：立即结束动画并填充完整内容
  - 文档更新：`README.md` 与本文件追加交互说明
  - 代码已推送到 `develop`（commit: `1def7de`）
- 关键文件：
  - `frontend/src/views/ChatView.vue`（模板渲染与样式、主按钮、动画）
  - `frontend/src/stores/chat.js`（思考占位、逐字打字、停止生成逻辑）
  - `README.md`、`SESSION_NOTES.md`
- 快速恢复（重启后直接运行）：
  ```bash
  # 后端
  cd /Users/rockts/Dev/xiaole-ai
  /Users/rockts/Dev/xiaole-ai/.venv/bin/python main.py

  # 前端
  source ~/.nvm/nvm.sh && nvm use 20
  cd /Users/rockts/Dev/xiaole-ai/frontend
  npm run dev
  ```
- 快速验证：
  1) 输入框输入文字 → 按钮变“发送(↑)”并显眼
  2) 点击发送 → 立即插入用户消息并滚动到底部
  3) AI 回复时 → 按钮变“停止”，消息先显示白点思考后进入逐字打字
  4) 点击“停止” → 立刻显示完整内容，动画结束

## 📌 标准启动流程（已验证）

### 后端启动
```bash
cd /Users/rockts/Dev/xiaole-ai
/Users/rockts/Dev/xiaole-ai/.venv/bin/python main.py
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

### 快速检查命令
```bash
# 检查服务状态
lsof -i :8000 -i :3000 | grep LISTEN

# 验证健康
curl http://localhost:8000/docs
curl http://localhost:3000
```

---

## 🔧 当前项目结构

### 后端关键文件
- `main.py` - FastAPI 主入口
- `conversation.py` - 对话管理
- `memory.py` - 记忆系统
- `agent.py` - AI 代理
- `tool_manager.py` - 工具管理
- `db_setup.py` - 数据库初始化

### 前端关键目录
- `frontend/src/views/ChatView.vue` - 聊天主视图
- `frontend/src/components/` - 组件库
- `frontend/src/stores/chat.js` - Pinia 状态管理
- `frontend/src/services/api.js` - API 封装

---

## 📝 最近改动记录

### 2025-11-20 ChatGPT 风格对话界面优化
**主要文件**: `frontend/src/views/ChatView.vue`

#### ✅ 代码块样式优化
- 添加深色头部栏（渐变背景 + 毛玻璃效果）
- 左侧语言标签：大写胶囊样式，背景色区分
- 右侧复制按钮：带图标和"复制代码"文字，hover 悬浮效果
- 代码区域内边距：16px 20px，行高 1.75
- 自定义滚动条样式
- 修复代码高亮双重转义问题（添加 `sanitize: false`）
- 使用 `:deep()` 穿透选择器确保动态元素样式生效

#### ✅ 对话宽度统一
- 对话区域 `.chat-inner`: 768px → 680px
- 输入框 `.input-wrapper`: 768px → 680px
- 欢迎页输入框: 同步调整为 680px

#### ✅ 列表样式增强
- 左侧缩进：1.6em → 2em
- 添加 `list-style-position: outside`
- 明确指定项目符号类型（实心圆、数字、空心圆、方块）
- li 元素增加 0.3em padding-left

#### ✅ 回到底部按钮优化
- 改为圆形按钮：44px 直径
- 在对话区域内居中（`.chat-inner` 添加 `position: relative`）
- 位置：`position: absolute, bottom: 120px`
- 添加淡入动画和 hover 悬浮效果
- hover 时边框变为品牌色
- 图标：向下箭头（已有）

#### 🔧 技术细节
```css
/* 代码块头部 */
.md-content :deep(.code-header) {
  background: linear-gradient(180deg, rgba(0,0,0,0.4) 0%, rgba(0,0,0,0.3) 100%);
  backdrop-filter: blur(10px);
}

/* 对话宽度 */
.chat-inner { max-width: 680px; }
.input-wrapper { max-width: 680px; }

/* 列表缩进 */
.md-content :deep(ul), .md-content :deep(ol) {
  padding-left: 2em;
  list-style-position: outside;
}

/* 回到底部按钮 */
.scroll-to-bottom {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  border-radius: 50%;
}
```

#### ✅ 已验证完成
- 代码块复制按钮样式正确应用
- 代码高亮集成完成（highlight.js + marked-highlight）
- 回到顶部按钮工作正常
- 思考与打字动画流畅
- 停止生成功能正常

### 2025-11-19 性能优化
- ✅ 添加 VS Code 性能配置 (`.vscode/settings.json`)
- ✅ 排除大文件夹监听减少 CPU 占用
- ✅ 优化终端滚动缓冲
- ✅ 启用自动保存

### 🎯 待优化功能（可选）
- [ ] 消息淡入动画增强（已有基础动画）
- [ ] 复制成功轻量 Toast 提示（当前已有"已复制"文字提示）
- [ ] 图片懒加载优化
- [ ] 代码块行号支持
- [ ] 代码块智能折叠（长代码）
- [ ] 语音识别 API 集成（待后端支持）
- [ ] 流式传输改造（替换当前定时器打字方案）

---

## 🐛 已知问题

1. **FastAPI 警告**: `on_event` 已弃用（不影响功能）
   - 位置: `main.py:139, 152`
   - 建议迁移到 `lifespan` 事件处理器

2. **待验证功能**
   - 历史对话切换（需实际测试多个会话）
   - 长消息滚动行为稳定性

---

## 💡 开发提示

### 热更新
- 前端: Vite 自动热更新
- 后端: 需手动重启（或使用 `uvicorn --reload`）

### 数据库
- 类型: PostgreSQL (NAS 部署)
- 连接配置: 环境变量或 `db_setup.py`
- 迁移: `db_migrations/` 目录

### API 文档
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## 🚀 快速命令备忘

```bash
# 停止所有服务
pkill -f "python.*main.py"
pkill -f "vite"

# 查看日志
tail -f logs/backend.log
tail -f logs/frontend.log

# 清理缓存
rm -rf frontend/node_modules/.vite
rm -rf __pycache__

# 依赖安装
pip install -r requirements.txt
cd frontend && npm install
```

---

**最后更新**: 2025-11-20 01:30
**会话状态**: 小乐正常运行，ChatGPT 风格界面优化完成
**当前任务**: 对话界面美化，代码块样式优化

---

### 2025-11-20 智能主按钮与回复动画增强（第二阶段）
**主要文件**: `frontend/src/views/ChatView.vue`, `frontend/src/stores/chat.js`

#### ✅ 三态主按钮
- 空输入：语音模式（圆形声波图标）
- 有输入：发送模式（白底黑色向上箭头，提升对比度）
- AI 回复中：停止模式（红色方形，可立即终止生成）

#### ✅ 思考与打字动画
- 思考占位：白色小圆点扩张脉冲动画（status = thinking）
- 打字过程：逐字填充内容（16ms ~60fps），状态从 typing → done
- 闪烁光标：在打字阶段通过伪元素实现（CSS caretBlink）
- 停止生成：立即清空定时器，直接填充完整内容并状态置为 done

#### ✅ 技术实现要点
```js
// stores/chat.js 片段
messages.value.push({ id: placeholderId, role: 'assistant', content: '', status: 'thinking' });
// 请求返回后：status = 'typing'，逐步写入 content
```
```css
.thinking-dot { animation: thinkingPulse 1s ease-in-out infinite; }
.md-content.typing:after { animation: caretBlink .9s steps(2,start) infinite; }
```

#### ✅ 停止生成逻辑
- 新增 `stopGeneration()`（store + view）统一结束打字并展示完整结果
- 释放定时器防止内存泄漏

#### 🧪 已验证
- 消息立即显示用户输入再异步处理 AI 回复
- 停止按钮在打字阶段可用，点击后光标消失
- 长回复按长度动态 step（约 60 步完成）

#### 📌 后续可选优化
- 流式传输改造：后端支持分片 SSE/WebSocket 时替换当前定时器方案
- 打字速度自定义：加入设置面板调节速度/是否启用动画
- 思考阶段提示文案：可加“正在思考…”下方灰色轻提示

**最后更新**: 2025-11-20  XX:XX （请刷新后端若需校准时间）
**当前状态**: 主按钮交互与回复动画上线
