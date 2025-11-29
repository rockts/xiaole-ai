# v0.8.1 发布说明

**发布日期**: 2025-11-29  
**版本类型**: Bug修复版本  
**分支**: develop → v0.8.1  

## 🎯 核心修复

### 提醒系统完全修复 ✅

**问题**：提醒系统不工作（无弹窗、无语音播报）

**根本原因**：
1. AsyncIOScheduler 在 FastAPI 环境中无法执行任务
2. ReminderManager 缺少事件循环，后台线程无法推送 WebSocket 消息

**解决方案**：
```python
# 1. 更换调度器
from apscheduler.schedulers.background import BackgroundScheduler
self.scheduler = BackgroundScheduler()

# 2. 设置事件循环
@app.on_event("startup")
async def startup_event():
    loop = asyncio.get_event_loop()
    reminder_manager.set_loop(loop)
```

**测试结果**：
- ✅ 调度器每分钟可靠运行
- ✅ WebSocket 推送成功
- ✅ 前端弹窗正常显示
- ✅ 语音播报正常工作

详见：[v0.8.1 修复报告](v0.8.1_REMINDER_FIX.md)

## 📦 其他改进

### 代码质量
- 🧹 清理重复的提醒弹窗代码
- 🧹 统一使用 ReminderNotification 全局组件
- 🧹 优化时间格式解析，支持多种格式

### 文档整理
- 📝 创建详细的修复报告
- 📝 更新 CHANGELOG.md
- 📝 更新 README.md 版本信息
- 📦 归档临时笔记和报告

### 项目清理
- 🗑️ 删除临时测试文件
- 🗑️ 删除调试脚本
- 🗑️ 清理 __pycache__ 目录

## 📥 升级方式

### 从 v0.8.0 升级

```bash
# 1. 拉取最新代码
git pull origin develop

# 2. 重启服务
./restart.sh

# 3. 验证提醒系统
curl http://localhost:8000/api/reminders/scheduler/status
```

### 全新部署

```bash
# 克隆仓库
git clone https://github.com/rockts/xiaole-ai.git
cd xiaole-ai

# 切换到 v0.8.1
git checkout v0.8.1

# 按照 README.md 完成部署
```

## ⚠️ 重要提示

1. **调度器状态**：首次启动后，调度器需要 1 分钟初始化
2. **提醒延迟**：提醒触发延迟 0-60 秒（取决于检查间隔）
3. **浏览器权限**：语音播报需要用户交互后才能自动播放

## 🔍 验证清单

升级后请验证以下功能：

- [ ] 创建一个 1 分钟后的测试提醒
- [ ] 等待提醒触发（弹窗显示）
- [ ] 确认语音播报正常
- [ ] 点击"我知道了"确认提醒
- [ ] 检查调度器状态 API

## 📊 性能数据

- **调度器资源占用**: ~5MB 内存
- **提醒触发延迟**: 0-60 秒
- **WebSocket 延迟**: <100ms
- **前端渲染延迟**: <200ms

## 🐛 已知问题

无重大已知问题。如遇到问题请查看：
- [故障排查指南](TROUBLESHOOTING.md)
- [提醒问题排查](REMINDER_TROUBLESHOOTING.md)

## 🚀 下一步

v0.9.0 规划：
- [ ] 前端架构持续优化
- [ ] 提醒统计和分析面板
- [ ] 更细粒度的调度间隔
- [ ] 提醒优先级队列

## 📞 支持

遇到问题？
1. 查看日志：`logs/xiaole_ai.log`
2. 检查调度器：`/api/reminders/scheduler/status`
3. 提交 Issue：https://github.com/rockts/xiaole-ai/issues

---

**感谢使用小乐 AI 管家！** 🎉
