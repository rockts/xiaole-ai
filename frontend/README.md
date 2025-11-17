# 小乐 AI 管家 - Vue 3 前端

## 项目结构

```
frontend/
├── src/
│   ├── assets/          # 静态资源
│   ├── components/      # 组件
│   │   └── layout/      # 布局组件
│   ├── composables/     # 组合式函数
│   ├── router/          # 路由配置
│   ├── services/        # API 服务
│   ├── stores/          # Pinia 状态管理
│   ├── views/           # 页面组件
│   ├── App.vue          # 根组件
│   └── main.js          # 入口文件
├── index.html
├── package.json
└── vite.config.js
```

## 路由配置

- `/` - 首页（重定向到 /chat）
- `/chat/:sessionId?` - 聊天页面（可选会话ID）
- `/memory` - 记忆查看
- `/reminders` - 提醒管理
- `/tasks` - 任务列表
- `/task/:id` - 任务详情
- `/documents` - 文档列表
- `/documents/:id` - 文档详情
- `/schedule` - 课程表
- `/tools` - 工具管理
- `/settings` - 设置

## 安装和运行

### 1. 安装依赖

```bash
cd frontend
npm install
```

### 2. 开发模式

```bash
npm run dev
```

前端将运行在 http://localhost:3000，自动代理后端 API (http://localhost:8000)

### 3. 构建生产版本

```bash
npm run build
```

构建产出将生成到 `../static/dist` 目录

## 技术栈

- **Vue 3** - 渐进式 JavaScript 框架
- **Vue Router 4** - 官方路由管理器
- **Pinia** - Vue 状态管理
- **Vite** - 下一代前端构建工具
- **Axios** - HTTP 客户端
- **Marked** - Markdown 解析器

## 主要功能

### 1. 聊天功能
- 实时消息发送和接收
- Markdown 渲染
- 图片上传
- 会话历史

### 2. 记忆管理
- 记忆统计
- 关键词搜索
- 语义搜索
- 记忆删除

### 3. 任务管理
- 任务列表
- 任务详情
- 状态筛选

### 4. 文档管理
- 文档上传
- 文档列表
- 文档详情查看

### 5. WebSocket 连接
- 实时消息推送
- 自动重连机制

## API 代理配置

开发环境下，所有 API 请求自动代理到后端服务器：

```javascript
// vite.config.js
proxy: {
  '/api': 'http://localhost:8000',
  '/ws': 'ws://localhost:8000',
  '/sessions': 'http://localhost:8000',
  // ...
}
```

## 状态管理

使用 Pinia 管理全局状态：

- `useChatStore` - 聊天相关状态
- `useMemoryStore` - 记忆相关状态

## 下一步开发

- [ ] 完善所有视图组件功能
- [ ] 集成语音交互功能
- [ ] 添加更多动画效果
- [ ] 优化移动端体验
- [ ] 添加单元测试
- [ ] PWA 支持

## 注意事项

1. 确保后端服务器运行在 8000 端口
2. 开发时前端运行在 3000 端口
3. 生产构建会输出到 `../static/dist`
4. WebSocket 连接会自动处理重连
