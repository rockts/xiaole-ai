# Claude API 配置指南

## 📝 获取 Claude API Key

### 方法1: Anthropic 官方 API

1. 访问 [Anthropic Console](https://console.anthropic.com/)
2. 注册/登录账号
3. 进入 API Keys 页面
4. 点击 "Create Key" 创建新的 API Key
5. 复制 API Key（格式：`sk-ant-...`）

### 方法2: 通过第三方代理（国内用户）

如果无法访问 Anthropic 官方，可以使用：
- **OpenRouter**: https://openrouter.ai/
- **API2D**: https://api2d.com/
- 其他代理服务

## ⚙️ 配置步骤

### 1. 编辑 .env 文件

打开项目根目录的 `.env` 文件，修改以下内容：

```bash
# 替换为你的实际 API Key
CLAUDE_API_KEY=sk-ant-your-actual-api-key-here

# 使用的模型（可选修改）
CLAUDE_MODEL=claude-3-5-sonnet-20241022
```

### 2. 可用的 Claude 模型

```bash
# Claude 3.5 Sonnet (推荐 - 最新最强)
CLAUDE_MODEL=claude-3-5-sonnet-20241022

# Claude 3 Opus (最强但较贵)
CLAUDE_MODEL=claude-3-opus-20240229

# Claude 3 Sonnet (平衡)
CLAUDE_MODEL=claude-3-sonnet-20240229

# Claude 3 Haiku (快速便宜)
CLAUDE_MODEL=claude-3-haiku-20240307
```

## 🧪 测试 API 连接

### 方法1: 使用测试脚本

```bash
python test_api.py
```

### 方法2: 直接测试

```python
# 创建测试文件 test_claude.py
from dotenv import load_dotenv
from anthropic import Anthropic
import os

load_dotenv()

client = Anthropic(api_key=os.getenv("CLAUDE_API_KEY"))

response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "你好，请用一句话介绍自己"}
    ]
)

print(response.content[0].text)
```

运行：
```bash
python test_claude.py
```

### 方法3: 通过 API 测试

```bash
# 启动服务
uvicorn main:app --reload

# 在另一个终端测试
curl -X POST "http://localhost:8000/think?prompt=你好，小乐"
```

## 💰 价格参考

Claude 3.5 Sonnet (20241022):
- Input: $3 / million tokens
- Output: $15 / million tokens

Claude 3 Haiku:
- Input: $0.25 / million tokens
- Output: $1.25 / million tokens

## 🔒 安全提示

1. ⚠️ **永远不要提交 .env 文件到 Git**
   - 已在 .gitignore 中配置
   - 定期检查是否误提交

2. 🔐 **保护你的 API Key**
   - 不要在代码中硬编码
   - 不要分享给他人
   - 定期轮换 Key

3. 💵 **监控 API 使用**
   - 在 Anthropic Console 查看使用量
   - 设置使用限制
   - 避免无限循环调用

## 🚀 开始使用

配置完成后，重启服务：

```bash
uvicorn main:app --reload
```

现在你的小乐AI就真正具备智能对话能力了！🎉

## 🐛 常见问题

### Q: 提示 "API key not valid"？
A: 检查 API Key 是否正确复制，是否包含完整的 `sk-ant-` 前缀

### Q: 提示 "Rate limit exceeded"？
A: API 调用频率过高，等待一段时间或升级账号等级

### Q: 响应很慢？
A: Claude API 响应时间通常 2-5 秒，这是正常的

### Q: 想使用更便宜的模型？
A: 修改 .env 中的 `CLAUDE_MODEL` 为 `claude-3-haiku-20240307`

## 📚 更多资源

- [Anthropic 文档](https://docs.anthropic.com/)
- [Claude API 参考](https://docs.anthropic.com/claude/reference/)
- [Python SDK](https://github.com/anthropics/anthropic-sdk-python)
