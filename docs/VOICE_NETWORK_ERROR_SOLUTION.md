# 语音识别 Network 错误解决方案

## 🔍 问题分析

你遇到的 `network` 错误是因为：

1. **Chrome 的 Web Speech API 依赖 Google 服务器**
   - 语音数据需要发送到 Google 进行处理
   - 即使能 ping 通 google.com，浏览器的语音服务也可能被阻止
   - 国内网络环境下经常出现此问题

2. **错误触发流程**
   ```
   点击麦克风 → 启动识别 → 连接Google服务器 → 连接失败 → network错误 → 识别结束
   ```

## ✅ 解决方案

### 方案1: 使用 VPN/代理（临时方案）⭐ 推荐

**步骤：**
1. 启动 VPN 或系统代理
2. 确保代理支持 WebSocket 连接
3. 在浏览器中测试：访问 https://www.google.com/speech-api/
4. 刷新页面，重新测试语音功能

**验证命令：**
```bash
# 测试 Google 语音服务连接
curl -I https://www.google.com/speech-api/v2/recognize

# 如果返回 200 或 401，说明可以连接
```

### 方案2: 使用国内语音服务（推荐实现）🔥

我们可以集成**百度语音识别 API**作为备选方案。

#### 优势：
- ✅ 不受网络限制
- ✅ 中文识别准确度更高
- ✅ 稳定可靠

#### 实现步骤：

1. **注册百度智能云账号**
   - 访问：https://cloud.baidu.com/
   - 开通"语音技术"服务
   - 获取 API Key 和 Secret Key

2. **添加后端接口（Python）**
   ```python
   # 在 main.py 中添加
   from aip import AipSpeech
   
   # 百度语音配置
   APP_ID = 'your_app_id'
   API_KEY = 'your_api_key'
   SECRET_KEY = 'your_secret_key'
   
   client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)
   
   @app.post("/api/voice/recognize")
   async def voice_recognize(file: UploadFile):
       """语音识别接口"""
       # 读取音频文件
       audio_data = await file.read()
       
       # 调用百度语音识别
       result = client.asr(audio_data, 'pcm', 16000, {
           'dev_pid': 1537,  # 中文识别
       })
       
       if result['err_no'] == 0:
           return {"text": result['result'][0]}
       else:
           return {"error": result['err_msg']}, 400
   ```

3. **修改前端代码**
   ```javascript
   // 使用 MediaRecorder 录音
   let mediaRecorder = null;
   let audioChunks = [];
   
   async function startBaiduVoiceRecognition() {
       const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
       mediaRecorder = new MediaRecorder(stream);
       
       mediaRecorder.ondataavailable = (event) => {
           audioChunks.push(event.data);
       };
       
       mediaRecorder.onstop = async () => {
           const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
           const formData = new FormData();
           formData.append('file', audioBlob, 'audio.wav');
           
           // 发送到后端
           const response = await fetch('/api/voice/recognize', {
               method: 'POST',
               body: formData
           });
           
           const result = await response.json();
           if (result.text) {
               document.getElementById('messageInput').textContent = result.text;
           }
       };
       
       mediaRecorder.start();
       audioChunks = [];
   }
   ```

### 方案3: 使用 Safari 浏览器（Mac 用户）

Safari 的语音识别可能使用不同的服务器：

1. 打开 Safari 浏览器
2. 访问 http://localhost:8000
3. 测试语音功能

### 方案4: 降级为纯文本输入

如果以上方案都不可行，保持当前的文字输入方式。

## 🧪 诊断工具

### 在浏览器控制台运行：

```javascript
// 测试语音识别可用性
async function testSpeechRecognition() {
    console.log('=== 语音识别诊断 ===');
    
    // 1. 检查API支持
    const hasAPI = 'webkitSpeechRecognition' in window || 'SpeechRecognition' in window;
    console.log('1. API支持:', hasAPI ? '✅' : '❌');
    
    // 2. 检查网络
    console.log('2. 网络状态:', navigator.onLine ? '✅ 在线' : '❌ 离线');
    
    // 3. 检查麦克风权限
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        console.log('3. 麦克风权限:', '✅ 已授权');
        stream.getTracks().forEach(track => track.stop());
    } catch (e) {
        console.log('3. 麦克风权限:', '❌', e.message);
    }
    
    // 4. 测试识别
    if (hasAPI) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        const recognition = new SpeechRecognition();
        recognition.lang = 'zh-CN';
        
        recognition.onerror = (event) => {
            console.log('4. 识别测试:', '❌', event.error);
            console.log('   错误详情:', event);
        };
        
        recognition.onstart = () => {
            console.log('4. 识别测试:', '✅ 成功启动');
            recognition.stop();
        };
        
        recognition.onend = () => {
            console.log('   测试结束');
        };
        
        try {
            recognition.start();
        } catch (e) {
            console.log('4. 识别测试:', '❌', e.message);
        }
    }
    
    console.log('==================');
}

testSpeechRecognition();
```

## 📊 错误类型说明

| 错误代码              | 说明                   | 解决方案                 |
| --------------------- | ---------------------- | ------------------------ |
| `network`             | 无法连接到Google服务器 | 使用VPN或切换到百度API   |
| `not-allowed`         | 麦克风权限被拒绝       | 在浏览器设置中允许麦克风 |
| `no-speech`           | 没有检测到语音         | 检查麦克风是否正常工作   |
| `audio-capture`       | 无法访问麦克风         | 检查麦克风设备           |
| `service-not-allowed` | 语音服务不可用         | 更换浏览器或使用其他方案 |

## 🚀 下一步计划

### 近期（1-2天）
- [ ] 实现百度语音识别后端接口
- [ ] 修改前端使用 MediaRecorder
- [ ] 添加语音服务选择开关（Google/百度）

### 中期（1周）
- [ ] 集成阿里云语音服务作为第三备选
- [ ] 添加语音识别质量评分
- [ ] 优化识别速度和准确度

### 长期
- [ ] 离线语音识别（本地模型）
- [ ] 多语言支持
- [ ] 语音指令自定义

## 💡 临时解决方案（马上可用）

如果你现在想测试语音功能，有两个快速方法：

### 方法1: 使用命令行测试（验证麦克风）
```bash
# Mac 用户
say "你好，这是测试"

# 测试麦克风录音
rec test.wav
```

### 方法2: 使用在线语音测试
访问这些网站测试你的网络是否支持语音识别：
- https://www.google.com/intl/zh-CN/chrome/demos/speech.html
- https://mdn.github.io/web-speech-api/speech-color-changer/

如果这些网站也无法工作，说明确实是网络问题。

## 📞 需要帮助？

如果以上方案都不能解决，请提供以下信息：

1. 浏览器版本（在控制台运行：`navigator.userAgent`）
2. 操作系统
3. 是否使用了VPN
4. 诊断工具的完整输出
5. 浏览器控制台的完整错误信息

---

**推荐方案顺序：**
1. 🥇 尝试开启VPN（最快）
2. 🥈 等待我实现百度语音API（最稳定）
3. 🥉 使用Safari浏览器测试
4. 继续使用文字输入

当前最快的解决方案是**开启VPN后重试**。如果你想要长期稳定的方案，我可以立即开始实现百度语音识别！
