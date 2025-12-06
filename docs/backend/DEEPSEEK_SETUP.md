# 🚀 DeepSeek API 配置指南（支持支付宝！）

## 为什么选择 DeepSeek？

✅ **支持支付宝/微信支付** - 无需国际信用卡  
✅ **超级便宜** - 比 Claude 便宜 90%+  
✅ **性能强大** - 接近 GPT-4 水平  
✅ **中文友好** - 中国公司，中文理解优秀  
✅ **API兼容** - OpenAI 格式，易于集成  

## 💰 价格对比

| 模型       | 输入价格         | 输出价格          | 相对Claude  |
| ---------- | ---------------- | ----------------- | ----------- |
| DeepSeek   | ¥1 / 百万tokens  | ¥2 / 百万tokens   | **便宜95%** |
| Claude 3.5 | ¥20 / 百万tokens | ¥100 / 百万tokens | -           |

**实际使用：**
- 一次对话(~500 tokens): **不到1分钱**
- 1000次对话: **约2元人民币**
- 10000次对话: **约20元人民币**

## 📝 注册步骤

### 第 1 步：访问官网

```bash
网址: https://platform.deepseek.com/
```

### 第 2 步：注册账号

1. 点击右上角 **"注册"**
2. 选择注册方式：
   - 📱 手机号注册（推荐）
   - 📧 邮箱注册
   - 🔐 GitHub/微信登录

3. 填写信息并验证

### 第 3 步：实名认证（可选但推荐）

- 提供身份证信息
- 通过后可获得更高的配额

### 第 4 步：充值

1. 进入 **"账户管理" > "充值"**
2. 选择充值金额（最低 **10元**）
3. 支付方式：
   - ✅ 支付宝
   - ✅ 微信支付
   - ✅ 银行卡

**建议：先充值 10-20 元测试，够用很久了！**

### 第 5 步：创建 API Key

1. 进入 **"API Keys"** 页面
2. 点击 **"创建新密钥"**
3. 给密钥起个名字，如：`xiaole-ai`
4. 复制生成的 API Key（格式：`sk-xxxxx`）

⚠️ **重要：密钥只显示一次，请立即保存！**

## ⚙️ 配置到项目

### 方法 1：使用配置脚本（推荐）

```bash
# 运行配置脚本
./setup_api_key.sh

# 按提示输入你的 DeepSeek API Key
```

### 方法 2：手动编辑

编辑 `.env` 文件：

```bash
# 确认使用 DeepSeek
AI_API_TYPE=deepseek

# 粘贴你的 API Key
DEEPSEEK_API_KEY=sk-your-actual-key-here

# 模型名称（默认即可）
DEEPSEEK_MODEL=deepseek-chat
```

## 🧪 测试配置

### 快速测试

```bash
# 测试 API 连接
python test_claude.py
```

如果看到 DeepSeek 的回复，说明配置成功！

### 完整测试

```bash
# 启动服务
uvicorn main:app --reload

# 在另一个终端运行
python test_api.py
```

### 单独测试 DeepSeek

```bash
python -c "
from agent import XiaoLeAgent
agent = XiaoLeAgent()
print(agent.think('你好，请介绍一下你自己'))
"
```

## 📊 可用模型

### deepseek-chat（推荐）
- 最新最强的模型
- 适合对话、分析、编程
- **价格：¥1/百万tokens (输入)**

### deepseek-coder
- 专门针对代码优化
- 适合编程任务
- 价格相同

## 🎯 切换回 Claude

如果以后想切换回 Claude（充值后），只需修改 `.env`：

```bash
# 切换到 Claude
AI_API_TYPE=claude

# 确保 Claude API Key 已配置
CLAUDE_API_KEY=sk-ant-your-key-here
```

重启服务即可！

## 💡 使用建议

### 1. 控制成本
```bash
# 在 agent.py 中调整 max_tokens
"max_tokens": 512  # 减少输出长度
```

### 2. 提升质量
```bash
# 调整 temperature
"temperature": 0.3  # 更确定性的回复
"temperature": 0.9  # 更有创造性
```

### 3. 监控使用
- 在 DeepSeek 控制台查看用量
- 设置余额告警

## 🐛 常见问题

### Q: 提示 "API key not valid"？
A: 检查 API Key 是否正确复制，确保以 `sk-` 开头

### Q: 提示 "Insufficient balance"？
A: 账户余额不足，请充值

### Q: 响应很慢？
A: 
- DeepSeek 通常响应时间 1-3 秒
- 检查网络连接
- 减小 max_tokens 参数

### Q: 中文乱码？
A: DeepSeek 原生支持中文，不应该有乱码。检查终端编码设置。

### Q: 想使用免费额度？
A: 新用户通常有一定免费额度，但需要实名认证。查看官网最新政策。

## 🎉 开始使用

配置完成后：

```bash
# 1. 启动服务
uvicorn main:app --reload

# 2. 访问 API 文档
open http://localhost:8000/docs

# 3. 测试对话
curl -X POST "http://localhost:8000/think?prompt=你好小乐"
```

## 📚 更多资源

- **官方文档**: https://platform.deepseek.com/docs
- **API 参考**: https://platform.deepseek.com/api-docs
- **定价详情**: https://platform.deepseek.com/pricing
- **社区论坛**: https://github.com/deepseek-ai

## 🎊 总结

使用 DeepSeek 的优势：
- ✅ 10元就能用很久
- ✅ 支持国内支付方式
- ✅ 性能接近国际顶级模型
- ✅ 中文理解优秀
- ✅ 响应速度快

**现在就去注册吧！** 🚀

注册地址: https://platform.deepseek.com/
