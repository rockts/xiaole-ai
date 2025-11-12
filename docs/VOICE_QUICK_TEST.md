# 语音功能快速测试指南 🎤

## 📋 前置条件检查

### 1. 确认后端服务运行
```bash
# 检查进程
ps aux | grep "python.*main.py"

# 如果没运行，启动服务
cd /Users/rockts/Dev/xiaole-ai
python3 main.py
```

### 2. 验证百度API配置
```bash
# 方式1：检查状态接口
curl 'http://localhost:8000/api/voice/status?detailed=true'

# 期望输出：
# {
#   "enabled": true,
#   "service": "百度语音识别",
#   "provider": "Baidu AI",
#   "configured": true,
#   "has_app_id": true,
#   "has_api_key": true,
#   "has_secret_key": true,
#   "app_id_masked": "******7549",
#   "api_key_masked": "************************1vPW",
#   "secret_key_masked": "*****************************I49"
# }
```

如果 `enabled: false`，说明百度API密钥未配置或有误，请检查 `.env` 文件。

## 🎯 测试方法

### 方法A：前端页面测试（推荐）

1. **打开页面**
   ```
   http://localhost:8000/static/index.html
   ```

2. **找到麦克风按钮**
   - 位置：页面底部聊天输入框的**右侧**
   - 图标：🎤

3. **切换到百度语音**
   - 点击右上角"⚙️ 设置"
   - 找到"🎤 语音交互设置"
   - "语音识别服务"选择"**百度语音 (推荐)**"
   - 保存设置

4. **测试录音识别**
   - 点击🎤按钮（变红色表示开始录音）
   - 说一句话："今天天气怎么样"
   - 再次点击🎤停止录音
   - 等待识别结果自动填入输入框

5. **查看结果**
   - 成功：输入框显示识别的文字
   - 失败：右上角显示错误提示

### 方法B：API直接测试

#### 测试1：语音识别（需要音频文件）
```bash
# 如果你有 wav 文件
curl -X POST 'http://localhost:8000/api/voice/recognize' \
  -F 'file=@test.wav'

# 期望返回：
# {"success": true, "text": "你好世界"}
```

#### 测试2：语音合成
```bash
curl -X POST 'http://localhost:8000/api/voice/synthesize' \
  -H 'Content-Type: application/json' \
  -d '{
    "text": "你好，我是小乐AI管家，语音测试成功",
    "person": 0,
    "speed": 5,
    "pitch": 5,
    "volume": 5,
    "audio_format": "mp3"
  }'

# 期望返回：
# {
#   "success": true,
#   "audio_base64": "SUQzBAAAAAAAI1RTU0UAAAAPAAADTGF2ZjYw...",
#   "mime": "audio/mpeg",
#   "format": "mp3"
# }
```

**播放合成的音频**（浏览器控制台）：
```javascript
// 1. 复制上面返回的 audio_base64 值
const b64 = "SUQzBAAAAAAAI1RTU0UAAAAPAAADTGF2ZjYw...";

// 2. 播放
const audio = new Audio(`data:audio/mpeg;base64,${b64}`);
audio.play();
```

## 🐛 常见问题排查

### 问题1：看不到麦克风按钮

**原因**：
- 页面没加载完整
- CSS 样式问题
- 浏览器缓存

**解决**：
1. 强制刷新页面（Ctrl+Shift+R 或 Cmd+Shift+R）
2. 清除浏览器缓存
3. 在浏览器控制台检查：
   ```javascript
   document.getElementById('voiceBtn')
   ```
   如果返回 `null`，说明元素未加载

### 问题2：点击麦克风报"network"错误

**原因**：
- 使用 file:// 协议打开页面（不安全来源）
- API地址错误

**解决**：
- ✅ 正确：http://localhost:8000/static/index.html
- ❌ 错误：file:///Users/.../index.html

### 问题3：提示"百度语音服务未配置"

**原因**：`.env` 文件缺失或密钥错误

**解决**：
```bash
# 1. 检查 .env 文件
cat .env | grep BAIDU

# 2. 应该看到三个配置
BAIDU_APP_ID=7217549
BAIDU_API_KEY=yq6CZ2dqQnGdevtiQgDa1vPW
BAIDU_SECRET_KEY=VcDVu97wz506w9TApXWURVkutCtJI49

# 3. 重启后端服务
pkill -f "python.*main.py"
python3 main.py
```

### 问题4：识别返回 err_no 错误码

| err_no | 含义         | 解决方案                      |
| ------ | ------------ | ----------------------------- |
| 3301   | 认证失败     | 检查 API Key 是否正确         |
| 3302   | 鉴权失败     | 检查 Secret Key 是否正确      |
| 3307   | 语音过长     | 录音时间不要超过60秒          |
| 3308   | 语音过短     | 至少说1秒以上                 |
| 3309   | 音频质量问题 | 检查麦克风，避免噪音          |
| 3310   | 采样率不匹配 | 不用担心，前端已自动处理为16k |
| 3314   | 音频质量差   | 说话清晰一点，靠近麦克风      |
| 3315   | 音频格式错误 | 前端已修复为标准WAV，不应出现 |

### 问题5：录音没有声音

**解决**：
1. 检查系统麦克风权限（macOS: 系统偏好设置 → 安全性与隐私 → 麦克风）
2. 检查浏览器麦克风权限（地址栏左侧锁图标 → 网站设置）
3. 测试麦克风是否正常工作（打开 QuickTime → 新建音频录制）

### 问题6：合成的音频播放失败

**原因**：
- Base64 数据不完整
- 浏览器自动播放策略阻止

**解决**：
```javascript
// 添加用户交互后播放
audio.play().catch(err => {
    console.log('需要用户交互才能播放:', err);
    // 显示播放按钮让用户手动点击
});
```

## ✅ 验证检查清单

- [ ] 后端服务运行中（`ps aux | grep main.py`）
- [ ] 百度API配置正确（`/api/voice/status?detailed=true` 返回 enabled=true）
- [ ] 页面能正常访问（http://localhost:8000/static/index.html）
- [ ] 能看到🎤麦克风按钮
- [ ] 点击麦克风能弹出权限请求
- [ ] 录音时按钮变红色
- [ ] 停止录音后能看到识别结果
- [ ] 识别的文字准确

## 📞 还有问题？

### 查看后端日志
```bash
# 如果后台运行
tail -f logs/server.log

# 如果前台运行
# 直接查看终端输出
```

### 查看浏览器控制台
1. 按 F12 打开开发者工具
2. 切换到 Console 标签
3. 查看红色错误信息

### 诊断脚本
```bash
# 快速诊断
curl http://localhost:8000/api/voice/status?detailed=true
curl http://localhost:8000/
curl http://localhost:8000/static/index.html | grep "voiceBtn"
```

---

**测试成功标志**：能录音 → 识别文字 → 发送消息 → （可选）听到AI语音回复

**预计测试时间**：3-5分钟
