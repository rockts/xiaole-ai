# 提醒系统故障排查指南

## 问题：提醒创建后没有弹窗和声音

### 快速检查清单

#### 1. 检查服务状态
```bash
# 检查Python服务是否运行
ps aux | grep "python.*main.py"

# 检查端口8000
lsof -ti:8000

# 查看服务日志
tail -50 /tmp/xiaole_server.log
```

#### 2. 检查Scheduler状态
访问：http://localhost:8000/api/scheduler/status

应该看到：
```json
{
  "running": true,
  "total_jobs": 5,
  "jobs": [...]
}
```

如果`running: false`，手动启动：
```bash
curl -X POST http://localhost:8000/api/scheduler/start
```

#### 3. 检查WebSocket连接
打开浏览器控制台（F12 → Console），应该看到：
```
✅ WebSocket已连接
```

如果看到错误或"WebSocket已断开"，检查：
- 服务是否正常运行
- 浏览器是否阻止WebSocket连接

#### 4. 检查浏览器权限

**音频权限**：
- 浏览器可能阻止自动播放音频
- 解决：在浏览器地址栏点击🔒图标 → 网站设置 → 声音改为"允许"

**通知权限**：
- 打开 http://localhost:8000/static/index.html
- 浏览器会弹出通知权限请求
- 点击"允许"

#### 5. 手动测试WebSocket推送

打开浏览器控制台，执行：
```javascript
// 测试音效
function testSound() {
    const audio = new Audio('/static/sounds/dingdong.mp3');
    audio.play();
}
testSound();

// 如果音频文件不存在，测试Web Audio API
function testWebAudio() {
    const audioContext = new AudioContext();
    const oscillator = audioContext.createOscillator();
    const gainNode = audioContext.createGain();
    oscillator.connect(gainNode);
    gainNode.connect(audioContext.destination);
    oscillator.frequency.setValueAtTime(800, audioContext.currentTime);
    gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
    oscillator.start();
    oscillator.stop(audioContext.currentTime + 0.5);
}
testWebAudio();
```

### 常见问题和解决方案

#### 问题1：Scheduler未启动
**症状**：`/api/scheduler/status` 返回 `running: false`

**解决**：
```bash
curl -X POST http://localhost:8000/api/scheduler/start
```

或者重启服务：
```bash
cd /Users/rockts/Dev/xiaole-ai
pkill -f "python.*main.py"
.venv/bin/python main.py > /tmp/xiaole_server.log 2>&1 &
```

#### 问题2：WebSocket连接失败
**症状**：控制台显示"WebSocket已断开"或连接错误

**原因**：
- 服务未正常启动
- 端口8000被占用
- 浏览器缓存问题

**解决**：
1. 重启服务
2. 清除浏览器缓存（Cmd+Shift+Delete）
3. 硬刷新页面（Cmd+Shift+R）

#### 问题3：音频无法播放
**症状**：控制台显示"音频播放失败"

**原因**：
- 浏览器阻止自动播放
- 音频文件不存在
- 浏览器不支持Web Audio API

**解决**：
1. 允许网站自动播放音频
2. 创建音频文件（见下方）
3. 测试Web Audio API（见上方测试代码）

#### 问题4：通知不显示
**症状**：提醒触发但没有浏览器通知

**原因**：
- 通知权限被拒绝
- 页面在前台（通知只在后台显示）

**解决**：
1. 检查浏览器通知权限：浏览器设置 → 隐私与安全 → 网站设置 → 通知
2. 将页面最小化测试

### 创建音频文件（可选）

如果想使用音频文件而不是Web Audio API：

```bash
# 创建静态资源目录
mkdir -p static/sounds

# 下载或创建一个简单的提示音
# 方法1：使用在线工具生成（如https://www.zapsplat.com/）
# 方法2：录制一个简单的"叮咚"声
# 方法3：从系统音效中复制
cp /System/Library/Sounds/Glass.aiff static/sounds/dingdong.mp3
```

### 调试步骤

1. **打开浏览器控制台**（F12）
2. **查看Console标签**，应该看到：
   ```
   ✅ WebSocket已连接
   ```
3. **查看Network标签** → WS（WebSocket），确认连接状态
4. **手动创建一个立即触发的提醒**：
   - 在对话框输入："提醒我1分钟后测试"
   - 等待1分钟
   - 观察控制台输出和弹窗

### 验证提醒系统

运行诊断脚本：
```bash
cd /Users/rockts/Dev/xiaole-ai
.venv/bin/python tests/temp/test_reminder_system.py
```

应该看到：
```
============================================================
提醒系统诊断
============================================================

1. Scheduler状态:
   运行中: True
   任务数: 5
   - 检查时间提醒: 2025-11-14T...
   ...

2. 提醒管理器:
   WebSocket回调: 已设置

3. 活跃提醒: X个
   ...

4. 测试触发检查:
   应触发提醒: X个
   ...
============================================================
```

### 终极解决方案

如果以上都不work，完全重启：

```bash
# 1. 停止所有服务
pkill -f "python.*main.py"
lsof -ti:8000 | xargs kill -9

# 2. 清理日志
rm /tmp/xiaole_server.log

# 3. 重新启动
cd /Users/rockts/Dev/xiaole-ai
.venv/bin/python main.py > /tmp/xiaole_server.log 2>&1 &

# 4. 等待5秒
sleep 5

# 5. 检查状态
curl http://localhost:8000/api/scheduler/status

# 6. 刷新浏览器（硬刷新：Cmd+Shift+R）
```

### 联系开发者

如果问题仍然存在，提供以下信息：

1. 服务日志：`cat /tmp/xiaole_server.log`
2. Scheduler状态：`curl http://localhost:8000/api/scheduler/status`
3. 浏览器控制台截图
4. 提醒列表：访问 http://localhost:8000/static/index.html → 点击"提醒"标签

---

**最后更新**：2025-11-14
**版本**：v0.8.0
