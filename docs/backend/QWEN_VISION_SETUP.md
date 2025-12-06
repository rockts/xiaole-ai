# 通义千问 Qwen-VL 图像识别配置指南

## 🎯 为什么选择 Qwen-VL？

- ✅ **国内可用**：阿里云服务，无需翻墙
- ✅ **免费额度**：每月 100万 tokens 免费
- ✅ **功能强大**：支持图像识别、OCR、场景理解
- ✅ **响应快速**：国内服务器，延迟低
- ✅ **支付方便**：支持支付宝、微信支付

## 📝 获取 API Key 步骤

### 1. 注册阿里云账号
访问：https://account.aliyun.com/register/

### 2. 开通百炼平台
访问：https://bailian.console.aliyun.com/
- 点击「立即开通」
- 同意服务协议

### 3. 创建 API Key
1. 进入控制台：https://dashscope.console.aliyun.com/
2. 点击左侧「API-KEY 管理」
3. 点击「创建新的API-KEY」
4. 复制生成的 Key（格式类似：`sk-xxxxxxxxxxxxxx`）

### 4. 配置到项目
编辑 `.env` 文件，找到这一行：
```bash
QWEN_API_KEY=your_qwen_api_key_here
```

替换为你的实际 Key：
```bash
QWEN_API_KEY=sk-xxxxxxxxxxxxxx
```

## 🚀 测试图像识别

### 方式1：通过命令行测试
```bash
cd /Users/rockts/Dev/xiaole-ai
.venv/bin/python -c "
from vision_tool import VisionTool
import json

tool = VisionTool()
print('Qwen Key:', '✅ 已配置' if tool.qwen_key else '❌ 未配置')
result = tool.analyze_with_qwen('uploads/20251111_225624_IMG_9959.jpeg', '请描述这张图片')
print(json.dumps(result, ensure_ascii=False, indent=2))
"
```

### 方式2：通过 API 测试
先启动服务器（如果还没启动）：
```bash
kill $(lsof -t -i:8000) 2>/dev/null  # 停止旧进程
nohup .venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000 > /tmp/xiaole_server.log 2>&1 &
```

然后测试：
```bash
curl -X POST "http://127.0.0.1:8000/api/vision/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "image_path": "uploads/20251111_225624_IMG_9959.jpeg",
    "prompt": "请详细描述这张图片",
    "model": "qwen"
  }' | python3 -m json.tool
```

### 方式3：通过浏览器测试
1. 打开：http://localhost:8000
2. 点击「上传图片」按钮
3. 选择一张图片
4. 在输入框输入问题，比如「这张图片里有什么？」
5. 点击「发送」

## 📊 价格说明

### 免费额度
- 每月 100万 tokens
- 足够处理约 **1000-2000 张图片**

### 付费价格（超出免费额度后）
- qwen-vl-plus：0.008元/1000tokens
- 大约：**1元 ≈ 125 张图片**

比 Claude 和 GPT-4V 便宜 **10倍以上**！

## 🔧 常见问题

### Q1: 提示 "Your credit balance is too low"
**A**: 这是 Claude 的错误，不是 Qwen 的。说明系统正在尝试 Claude 而不是 Qwen。

**解决方法**：
1. 确保 `.env` 中配置了正确的 `QWEN_API_KEY`
2. 重启服务器：
   ```bash
   kill $(lsof -t -i:8000)
   nohup .venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000 > /tmp/xiaole_server.log 2>&1 &
   ```

### Q2: 图片识别返回 400 错误
**A**: 可能是图片格式或大小问题。

**检查**：
- 图片大小 < 20MB
- 支持格式：jpg, jpeg, png, gif, webp, bmp
- 图片文件存在且可读

### Q3: 想要更详细的图片分析
**A**: 在 prompt 中明确要求：
```json
{
  "prompt": "请详细描述这张图片，包括：1. 主要场景和环境 2. 人物和物体 3. 颜色和光线 4. 图片中的文字（如有）5. 整体氛围"
}
```

### Q4: 如何切换回 Claude/GPT-4V？
**A**: 在请求中指定 model 参数：
```json
{
  "model": "claude"  // 或 "gpt4v"
}
```

或者在 `.env` 中注释掉 `QWEN_API_KEY`。

## 🎨 支持的功能

Qwen-VL 可以识别：
- ✅ 场景和环境（室内/室外、时间、天气）
- ✅ 人物（数量、动作、表情、服装）
- ✅ 物体（种类、位置、状态）
- ✅ 文字（OCR，中英文）
- ✅ 颜色和光线
- ✅ 空间关系
- ✅ 情感和氛围

## 📚 更多资源

- 官方文档：https://help.aliyun.com/zh/dashscope/developer-reference/vl-plus-quick-start
- API 参考：https://help.aliyun.com/zh/dashscope/developer-reference/api-details-9
- 价格说明：https://help.aliyun.com/zh/dashscope/developer-reference/tongyi-qianwen-vl-plus-api-pricing

## 🆘 获取帮助

如果遇到问题：
1. 查看服务器日志：`tail -f /tmp/xiaole_server.log`
2. 查看浏览器控制台（F12）
3. 检查 `.env` 配置是否正确
4. 确认 Qwen API Key 有效且有余额

---

**配置完成后，记得重启服务器！** 🚀
