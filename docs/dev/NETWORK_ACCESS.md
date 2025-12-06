# 小乐AI - 局域网访问配置指南

## 当前配置状态

✅ **后端已配置为局域网访问模式**
- 监听地址: `0.0.0.0:8000`
- 本机IP: `192.168.88.104`

## 其他电脑访问小乐

### 1. 后端API访问
其他电脑可以通过以下地址访问后端API：
```
http://192.168.88.104:8000
```

### 2. 前端界面访问

#### 方式一：修改前端配置（推荐）
编辑 `frontend/src/services/api.js`，将API地址改为：
```javascript
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://192.168.88.104:8000';
```

然后重新构建前端：
```bash
cd frontend
npm run build
```

#### 方式二：前端也监听局域网
编辑 `frontend/vite.config.js`：
```javascript
export default {
  server: {
    host: '0.0.0.0',  // 添加这行
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://192.168.88.104:8000',
        changeOrigin: true
      }
    }
  }
}
```

启动前端：
```bash
cd frontend
npm run dev
```

其他电脑访问：`http://192.168.88.104:5173`

### 3. 防火墙配置

#### macOS 防火墙
如果其他电脑无法访问，需要检查防火墙设置：

1. 打开"系统偏好设置" → "安全性与隐私" → "防火墙"
2. 点击锁形图标解锁
3. 点击"防火墙选项"
4. 添加 Python 到允许列表，或临时关闭防火墙测试

#### 临时关闭防火墙测试（不推荐长期使用）
```bash
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setglobalstate off
```

#### 允许特定端口
```bash
# 允许8000端口
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add /usr/local/bin/python3
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --unblockapp /usr/local/bin/python3
```

### 4. 测试连接

在其他电脑上测试API是否可访问：
```bash
curl http://192.168.88.104:8000/health
```

或在浏览器中打开：
```
http://192.168.88.104:8000/docs
```

## 问题排查

### 问题1：其他电脑无法访问
1. 确认两台电脑在同一局域网
2. ping 测试连通性：`ping 192.168.88.104`
3. 检查防火墙设置
4. 确认后端服务正在运行：`lsof -i:8000`

### 问题2：前端连接后端失败
1. 检查浏览器控制台是否有CORS错误
2. 确认前端配置的API地址正确
3. 检查后端CORS设置（已在main.py中配置）

### 问题3：IP地址变化
如果Mac的IP地址变化了，需要：
1. 查看当前IP：`ifconfig | grep "inet " | grep -v 127.0.0.1`
2. 更新前端配置中的IP地址
3. 重新构建前端

## 安全建议

1. **生产环境**: 不建议直接暴露到公网，使用反向代理（如Nginx）
2. **局域网使用**: 确保局域网是受信任的网络
3. **添加认证**: 考虑添加API密钥或用户认证机制
4. **HTTPS**: 生产环境应该配置HTTPS证书

## 快速启动脚本

创建启动脚本 `start_network.sh`：
```bash
#!/bin/bash
# 显示当前IP
echo "本机IP地址："
ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}'

# 启动后端
echo "启动后端服务..."
cd /Users/rockts/Dev/xiaole-ai/backend
python3 main.py &

# 启动前端
echo "启动前端服务..."
cd /Users/rockts/Dev/xiaole-ai/frontend
npm run dev
```

## 相关文件
- 后端配置: `backend/main.py` (line 2010)
- 前端配置: `frontend/vite.config.js`
- API服务: `frontend/src/services/api.js`
