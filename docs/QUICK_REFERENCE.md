# 小乐AI快速参考

**版本**: v0.6.0  
**更新**: 2025-11-11

## 🚀 快速启动

```bash
# 1. 启动服务
bash scripts/start_fixed.sh

# 2. 访问界面
open http://localhost:8000

# 3. 查看日志
tail -f /tmp/xiaole.log
```

## 📁 项目结构速览

```
xiaole-ai/
├── 核心模块
│   ├── agent.py              # AI代理（1200行）
│   ├── memory.py             # 记忆管理（300行）
│   ├── conversation.py       # 对话管理（155行）
│   ├── tool_manager.py       # 工具管理（400行）
│   └── main.py              # API入口（665行）
│
├── 工具模块 tools/
│   ├── search_tool.py       # 🔍 搜索（DuckDuckGo）
│   ├── file_tool.py         # 📁 文件操作
│   ├── weather_tool.py      # 🌤️  天气查询
│   ├── system_tool.py       # 💻 系统信息
│   └── reminder_tool.py     # ⏰ 提醒管理
│
├── 前端界面 static/
│   └── index.html           # Web界面（3910行）
│
├── 测试文件 tests/
│   ├── test_session_load.py # 会话加载测试 ✅
│   ├── test_export_fix.py   # 导出功能测试 ✅
│   └── test_improved_search.py # 搜索功能测试 ✅
│
└── 文档 docs/
    ├── PROJECT_STATUS.md    # 📊 项目状态总览 🆕
    ├── v0.6.0_PLAN.md      # 📝 v0.6.0计划
    └── TEST_GUIDE.md       # 🧪 测试指南
```

## 🔧 常用命令

### 服务管理
```bash
# 启动服务
bash scripts/start_fixed.sh

# 停止服务
lsof -ti:8000 | xargs kill -9

# 重启服务
lsof -ti:8000 | xargs kill -9 && bash scripts/start_fixed.sh

# 检查状态
ps aux | grep "python.*main.py"
```

### 测试命令
```bash
# 会话加载测试
python tests/test_session_load.py

# 搜索功能测试
python tests/test_improved_search.py

# 导出功能测试
python tests/test_export_fix.py

# 完整Phase 3测试
python tests/test_phase3_no_db.py
```

### 数据库操作
```bash
# 测试连接
python tests/test_nas_connection.py

# 查看最近会话
python tests/check_recent_sessions.py

# 运行迁移（待执行）
python scripts/run_migration.py
```

## 🎯 核心功能使用

### 1. 对话功能
```
用户: 你好
小乐: 你好！我是小乐...

用户: 记住我叫张三
小乐: 好的，我已经记住了...
```

### 2. 搜索功能 🆕
```
用户: 搜索下iPhone 17 Pro Max最新价格
小乐: [自动调用搜索工具]
     根据搜索结果，iPhone 17 Pro Max...
```

**触发关键词**:
- "搜索"、"查一下"、"找一下"
- "最新"、"现在"、"2025年"
- "iphone 17"、"价格"等

### 3. 文件操作
```
用户: 创建一个文件todo.txt，内容是...
小乐: [调用文件工具] 已创建文件...

用户: 读取todo.txt
小乐: [读取文件] 文件内容是...
```

### 4. 天气查询
```
用户: 明天天水的天气怎么样？
小乐: [调用天气工具] 明天天水...
```

### 5. 提醒管理
```
用户: 明天下午3点提醒我开会
小乐: [创建提醒] 已设置提醒...
```

### 6. 会话导出 🆕
1. 点击右侧会话列表
2. 点击会话卡片上的导出按钮
3. 选择格式（Markdown/JSON）
4. 自动下载文件

## 🐛 常见问题

### Q1: 服务启动失败？
```bash
# 检查端口占用
lsof -i:8000

# 清理后重启
lsof -ti:8000 | xargs kill -9
bash scripts/start_fixed.sh

# 查看错误日志
tail -50 /tmp/xiaole.log
```

### Q2: 搜索功能不工作？
```bash
# 检查ddgs包
python -c "from ddgs import DDGS; print('✅ OK')"

# 如果失败，重新安装
pip install --upgrade ddgs

# 测试搜索
python tests/test_improved_search.py
```

### Q3: 会话点击没反应？
- 检查浏览器控制台（F12）
- 确认服务器正在运行
- 刷新页面（Ctrl+R）

### Q4: 导出缺少时间戳？
- 已在v0.6.0修复 ✅
- 更新代码后重启服务

## 📊 API接口速查

### 对话接口
```bash
# 发送消息
curl "http://localhost:8000/chat?prompt=你好"

# 流式输出
curl "http://localhost:8000/chat?prompt=你好&stream=true"
```

### 会话管理
```bash
# 获取会话列表
curl "http://localhost:8000/sessions"

# 获取会话详情
curl "http://localhost:8000/session/{session_id}"

# 删除会话
curl -X DELETE "http://localhost:8000/session/{session_id}"
```

### 工具接口
```bash
# 工具列表
curl "http://localhost:8000/tools/list"

# 执行工具
curl -X POST "http://localhost:8000/tools/execute" \
  -H "Content-Type: application/json" \
  -d '{"tool_name":"search","parameters":{"query":"iPhone 17"}}'

# 工具历史
curl "http://localhost:8000/tools/history"
```

## 🔑 环境变量

```bash
# DeepSeek API
DEEPSEEK_API_KEY=sk-xxxxx
DEEPSEEK_API_BASE=https://api.deepseek.com

# Claude API（可选）
ANTHROPIC_API_KEY=sk-ant-xxxxx

# 数据库
DB_URL=postgresql://user:pass@host:port/db
```

## 📈 性能参考

| 操作 | 响应时间 | 说明 |
|------|---------|------|
| 简单对话 | 1-2秒 | 无工具调用 |
| 搜索查询 | 3-8秒 | 包含网络请求 |
| 文件操作 | <1秒 | 本地操作 |
| 会话加载 | <100ms | 数据库查询 |
| 消息发送 | <50ms | WebSocket |

## 🎨 快捷键

| 快捷键 | 功能 |
|--------|------|
| `Ctrl + Enter` | 发送消息 |
| `Ctrl + K` | 清空输入 |
| `Ctrl + L` | 清空对话 |
| `Ctrl + S` | 保存会话 |
| `F5` | 刷新页面 |

## 📞 获取帮助

- 📖 详细文档: `docs/PROJECT_STATUS.md`
- 📝 开发日志: `CHANGELOG.md`
- 🐛 问题追踪: `docs/CURRENT_STATUS.md`
- 🧪 测试指南: `docs/TEST_GUIDE.md`

---

*快速参考 v1.0 - 2025-11-11*
