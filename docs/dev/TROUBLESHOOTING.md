# 故障排查指南

## 前端页面加载缓慢/无响应问题

### 问题现象
- 访问 `http://localhost:3000` 时页面长时间加载（超过3秒）
- curl 测试前端端口时连接超时
- 浏览器显示"等待响应"或一直转圈
- 后端服务正常但前端无法访问

### 问题时间
2025年11月22日

### 根本原因

#### 1. Vite 代理配置被注释
**文件**: `frontend/vite.config.js`

代理配置被错误地注释掉，导致前端无法正确转发 API 请求到后端。

**错误配置示例**:
```javascript
server: {
    host: '0.0.0.0',
    port: 3000,
    /* proxy: {
        '/api': {
            target: 'http://127.0.0.1:8000',
            ...
        }
    } */
}
```

**正确配置**:
```javascript
server: {
    host: '0.0.0.0',
    port: 3000,
    proxy: {
        '/api': {
            target: 'http://127.0.0.1:8000',
            changeOrigin: true
        },
        '/ws': {
            target: 'ws://127.0.0.1:8000',
            ws: true
        },
        // ... 其他代理配置
    }
}
```

#### 2. 健康检查路径错误
**文件**: `frontend/src/utils/healthCheck.js`

健康检查代码使用了错误的路径，导致请求前端根路径而非后端 API，造成循环阻塞。

**错误代码**:
```javascript
const response = await fetch('/', {
    method: 'GET',
    signal: controller.signal
})
```

**正确代码**:
```javascript
// 使用后端API路径而不是前端根路径
const apiBase = import.meta.env.VITE_API_BASE || ''
const response = await fetch(`${apiBase}/`, {
    method: 'GET',
    signal: controller.signal
})
```

#### 3. 环境变量未配置
**文件**: `frontend/.env`

需要明确指定后端 API 地址。

**正确配置**:
```dotenv
# API Base URL
VITE_API_BASE=http://127.0.0.1:8000
```

### 诊断步骤

1. **检查端口占用**
```bash
lsof -i :8000  # 后端端口
lsof -i :3000  # 前端端口
```

2. **测试后端服务**
```bash
curl http://127.0.0.1:8000/
# 应返回: {"message":"你好，我是小乐AI管家，我已启动。"}
```

3. **测试前端响应时间**
```bash
curl -I -m 3 http://127.0.0.1:3000/
# 应在3秒内返回 HTTP/1.1 200 OK
```

4. **检查日志**
```bash
tail -n 50 logs/backend.log
tail -n 50 logs/frontend.log
```

### 解决方案

#### 快速修复（推荐）

1. **恢复 Vite 代理配置**
```bash
# 编辑 frontend/vite.config.js
# 取消注释 proxy 配置块
```

2. **修复健康检查**
```bash
# 编辑 frontend/src/utils/healthCheck.js
# 修改 fetch 路径使用 VITE_API_BASE
```

3. **配置环境变量**
```bash
# 编辑 frontend/.env
echo "VITE_API_BASE=http://127.0.0.1:8000" > frontend/.env
```

4. **重启服务**
```bash
./restart.sh
```

#### 完整重置（如果快速修复无效）

```bash
# 1. 停止所有服务
./stop.sh
pkill -f "python.*main.py"
pkill -f "vite"

# 2. 清理缓存
cd frontend
rm -rf node_modules/.vite .vite

# 3. 重新启动
cd ..
./start.sh

# 4. 验证
sleep 3
curl -I http://127.0.0.1:3000/
```

## 外部访问问题（局域网其他电脑无法访问）

### 问题现象
- 本机访问 `http://localhost:3000` 正常
- 局域网其他电脑访问 `http://192.168.x.x:3000` 时，页面能加载但无法获取数据
- 控制台报错 `Connection refused` 或请求 `http://127.0.0.1:8000` 失败

### 根本原因
前端配置了硬编码的 `VITE_API_BASE=http://127.0.0.1:8000`。
当其他电脑访问时，浏览器会尝试连接访问者电脑的 `127.0.0.1:8000`，而不是服务器的后端。

### 解决方案
1. **移除或注释 `VITE_API_BASE`**
   编辑 `frontend/.env`，注释掉该行：
   ```dotenv
   # VITE_API_BASE=http://127.0.0.1:8000
   ```
   这样前端会使用相对路径（如 `/api/...`），请求会被发送到 Vite 服务器（3000端口），然后由 Vite 代理转发到后端（8000端口）。

2. **修改健康检查路径**
   编辑 `frontend/src/utils/healthCheck.js`，确保使用被代理的路径：
   ```javascript
   // 使用被代理的API路径，确保相对路径能正确转发到后端
   const response = await fetch(`${apiBase}/api/scheduler/status`, { ... })
   ```

3. **重启服务**
   ```bash
   ./restart.sh
   ```

### 预防措施

1. **不要注释代理配置**
   - Vite 的代理配置是前后端通信的关键
   - 如需调试，使用环境变量控制而非注释代码

2. **健康检查使用正确路径**
   - 始终通过 `VITE_API_BASE` 访问后端 API
   - 避免直接使用相对路径 `/`

3. **环境变量文档化**
   - 在 `frontend/.env.example` 中提供示例配置
   - 确保团队成员了解必需的环境变量

4. **定期测试**
   ```bash
   # 添加到 CI/CD 或日常检查
   curl -I -m 3 http://127.0.0.1:3000/ || echo "前端响应异常"
   ```

### 相关文件清单

- `frontend/vite.config.js` - Vite 配置和代理设置
- `frontend/src/utils/healthCheck.js` - 后端健康检查逻辑
- `frontend/.env` - 环境变量配置
- `start.sh` / `restart.sh` - 服务启动脚本

### 参考链接

- [Vite 代理配置文档](https://vitejs.dev/config/server-options.html#server-proxy)
- [健康检查最佳实践](./FRONTEND_OPTIMIZATION.md)

---

**最后更新**: 2025年11月22日  
**影响版本**: v0.8.0+  
**优先级**: 高（影响系统可用性）
