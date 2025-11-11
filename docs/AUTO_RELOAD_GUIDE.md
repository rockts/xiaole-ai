# 🔄 自动重载开发模式使用指南

## ✅ 已配置完成

小乐AI 现在支持**代码热重载**功能！修改代码后服务器会自动重启，无需手动操作。

## 🚀 启动方式

### 方式1：前台运行（推荐开发时使用）
```bash
./scripts/start_server.sh
```
- ✅ 实时看到输出
- ✅ 自动重载
- ❌ 关闭终端会停止服务

### 方式2：后台运行（推荐日常使用）
```bash
./scripts/start_server_background.sh
```
- ✅ 后台运行
- ✅ 自动重载
- ✅ 关闭终端继续运行
- ✅ 日志保存到文件

## 📝 工作原理

### 监控范围
服务器会监控以下文件的变化：
- ✅ 所有 `.py` 文件
- ✅ `.env` 配置文件
- ✅ HTML、JS 等静态文件

### 自动排除
以下文件/目录的变化**不会**触发重启：
- ❌ `*.pyc` 编译文件
- ❌ `__pycache__` 缓存目录
- ❌ `*.log` 日志文件
- ❌ `logs/` 日志目录
- ❌ `uploads/` 上传文件
- ❌ `chroma_db/` 向量数据库

## 💡 使用场景

### 场景1：修改代码
```bash
# 1. 启动服务器（后台）
./scripts/start_server_background.sh

# 2. 修改任意 Python 文件
vim main.py  # 或用你喜欢的编辑器

# 3. 保存文件后，服务器自动重启（2-3秒）

# 4. 刷新浏览器测试新功能
```

### 场景2：修改配置
```bash
# 1. 修改 .env 文件
vim .env

# 2. 保存后自动重启，新配置生效
```

### 场景3：查看重启日志
```bash
# 实时查看日志
tail -f /tmp/xiaole_server.log

# 查看最近的重启记录
tail -50 /tmp/xiaole_server.log | grep -i "restart\|started"
```

## 🛠️ 常用命令

### 查看服务器状态
```bash
# 检查服务器是否运行
lsof -i :8000

# 查看进程
ps aux | grep uvicorn
```

### 停止服务器
```bash
# 方法1：使用 pkill
pkill -f 'uvicorn main:app'

# 方法2：使用 PID
kill $(lsof -t -i:8000)
```

### 重启服务器
```bash
# 停止并启动
pkill -f 'uvicorn main:app' && ./scripts/start_server_background.sh
```

### 查看日志
```bash
# 实时查看
tail -f /tmp/xiaole_server.log

# 查看最近100行
tail -100 /tmp/xiaole_server.log

# 搜索错误
grep -i error /tmp/xiaole_server.log

# 搜索重启记录
grep -i "restart\|reload" /tmp/xiaole_server.log
```

## 🔍 监控文件变化（可选）

如果你想实时看到哪些文件触发了重启：

```bash
# 终端1：运行监控脚本
./scripts/watch_changes.sh

# 终端2：修改代码
# 终端1 会显示文件变化提示
```

## ⚡ 重启速度

- **检测变化**：< 1 秒
- **重启服务器**：2-3 秒
- **总计**：修改代码后 3-4 秒内生效

## 🐛 故障排查

### 问题1：修改代码后没有自动重启

**检查1**：服务器是否在运行
```bash
lsof -i :8000
```

**检查2**：是否使用了 `--reload` 参数
```bash
ps aux | grep uvicorn | grep reload
```

**检查3**：查看日志是否有错误
```bash
tail -50 /tmp/xiaole_server.log
```

**解决方法**：重新启动
```bash
./scripts/start_server_background.sh
```

### 问题2：重启太频繁

**原因**：可能修改了排除列表之外的文件

**解决方法**：在 `start_server_background.sh` 中添加更多排除规则
```bash
--reload-exclude "your_folder/*"
```

### 问题3：重启后出错

**检查**：代码是否有语法错误
```bash
# 手动检查 Python 语法
python3 -m py_compile main.py
```

**查看详细错误**：
```bash
tail -100 /tmp/xiaole_server.log
```

## 🎯 开发最佳实践

### ✅ 推荐做法

1. **使用后台模式开发**
   ```bash
   ./scripts/start_server_background.sh
   tail -f /tmp/xiaole_server.log  # 另一个终端
   ```

2. **小步提交**
   - 修改一个功能
   - 等待自动重启（3秒）
   - 测试功能
   - 继续下一个功能

3. **保持浏览器开发者工具打开**
   - F12 打开控制台
   - 看到重启后手动刷新（或使用 Live Reload 插件）

### ❌ 避免做法

1. **不要频繁修改保存**
   - 写完一个完整功能再保存
   - 避免每输入一行就保存

2. **不要在重启过程中发送请求**
   - 等待 2-3 秒让服务器完全启动
   - 看到日志 "Application startup complete"

3. **不要直接修改数据库/上传文件**
   - 这些不需要重启
   - 修改后会白白触发重启

## 📊 性能影响

- **开发环境**：✅ 推荐使用自动重载
- **生产环境**：❌ 不要使用 `--reload`（去掉该参数）

## 🆘 获取帮助

如果遇到问题：

1. **查看实时日志**
   ```bash
   tail -f /tmp/xiaole_server.log
   ```

2. **检查进程状态**
   ```bash
   lsof -i :8000
   ps aux | grep uvicorn
   ```

3. **完全重启**
   ```bash
   pkill -f 'uvicorn main:app'
   sleep 2
   ./scripts/start_server_background.sh
   ```

---

## 🎉 现在开始开发吧！

修改代码 → 自动重启 → 刷新浏览器 → 看到效果 🚀
