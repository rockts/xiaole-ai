# 图片记忆功能修复

## 问题描述
用户上传课程表图片后，虽然小乐能识别出内容，但在后续对话中无法"记住"图片内容，提示"没看到"。

## 根本原因
之前的实现中，前端直接调用 `/api/vision/analyze` 获取图片识别结果并显示，但**没有将识别结果发送到 `/chat` API**，因此：
1. 图片内容没有进入对话历史
2. 图片内容没有被记忆系统保存
3. 小乐的上下文中没有图片信息

## 修复方案

### 1. 后端修改 (`main.py`)
**修改 `/chat` API，添加图片处理逻辑：**

```python
@app.post("/chat")
def chat(
    prompt: str,
    session_id: str = None,
    user_id: str = "default_user",
    response_style: str = "balanced",
    image_path: str = None,  # ✅ 新增：图片路径
    memorize: bool = False   # ✅ 新增：是否强制记忆
):
```

**关键逻辑：**
- 收到 `image_path` 时，先调用 `VisionTool.analyze_image()` 识别图片
- 将识别结果与用户问题合并为一条消息：`[图片内容]: xxx\n\n[用户问题]: xxx`
- 如果 `memorize=True` 或消息包含"记住/保存"等关键词，直接调用 `xiaole.memory.remember()` 保存
- 将合并后的消息传给 `xiaole.chat()`，进入正常对话流程

**优势：**
- 图片内容自动进入对话历史（通过 `xiaole.chat()` 的会话管理）
- 图片内容自动触发智能记忆提取（通过 `_extract_and_remember()`）
- 用户明确要求"记住"时，双保险直接入库

### 2. 前端修改 (`static/index.html`)
**简化 `sendMessageFromDiv()` 函数：**

**之前的流程（错误）：**
```
上传图片 → 调用 /api/vision/analyze 
→ 显示识别结果 
→ 结束（没有进入对话历史）
```

**修复后的流程（正确）：**
```
上传图片 → 直接调用 /chat API（带 image_path 参数）
→ 后端自动识别图片 + 合并到对话
→ 小乐回复 + 保存历史 + 记忆提取
```

**关键代码：**
```javascript
// 检测"记住"关键词
const memorizeKeywords = ['记住', '保存', '记下', '存一下', '记录'];
const shouldMemorize = message && memorizeKeywords.some(kw => message.includes(kw));

// 构建请求 URL（添加图片路径和记忆标志）
let url = `${API_BASE}/chat?prompt=${encodeURIComponent(message || '')}&response_style=${responseStyle}`;

if (currentImagePath) {
    url += `&image_path=${encodeURIComponent(currentImagePath)}`;
}

if (shouldMemorize) {
    url += `&memorize=true`;
}
```

## 工作流程

### 用户上传图片 + 要求记住
1. 用户上传课程表图片
2. 输入："记住这些内容"
3. 点击发送

**后端处理：**
```
1. 收到 image_path="uploads/xxx.jpeg", memorize=true
2. 调用 VisionTool 识别图片 → 获得课程表文字内容
3. 构建消息: "[图片内容]: 这是一张课程表...\n\n[用户问题]: 记住这些内容"
4. 因为 memorize=true，直接调用 memory.remember() 保存（tag="image:xxx.jpeg"）
5. 将完整消息传给 xiaole.chat() → 进入对话历史 + 触发智能提取
6. 小乐回复："好的，我已经记住了这张课程表的内容"
```

### 用户后续提问
1. 用户问："刚才那个课程表周四有什么课？"

**后端处理：**
```
1. xiaole.chat() 从对话历史中看到之前的 "[图片内容]: ..." 消息
2. 或者通过语义搜索从记忆库中召回课程表内容
3. 回答："根据之前的课程表，周四有..."
```

## 测试步骤

### 1. 基础图片识别测试
```bash
# 刷新浏览器
# 上传一张图片
# 点击发送（不输入文字）
# 期望：小乐回复图片内容描述
```

### 2. 记忆功能测试
```bash
# 上传课程表图片
# 输入："记住这些内容"
# 点击发送
# 期望：小乐回复"我已经记住了..."

# 等待几秒，再输入："刚才那个课程表周四有什么课？"
# 期望：小乐能回答出具体课程
```

### 3. 图片 + 问题测试
```bash
# 上传图片
# 输入："这张图片是什么类型的文档？"
# 点击发送
# 期望：小乐根据图片内容回答
```

### 4. 对话历史测试
```bash
# 上传图片后发送
# 再问："刚才的图片内容是什么？"
# 期望：小乐能回忆起图片内容
```

## 技术细节

### 记忆存储策略
- **自动记忆**：所有图片内容都会进入对话历史，触发智能提取
- **强制记忆**：用户说"记住"时，直接入库（importance=0.8）
- **标签管理**：使用 `tag="image:文件名"` 便于检索

### 关键词检测
前端检测：`['记住', '保存', '记下', '存一下', '记录']`
后端检测：同样的关键词列表

### 错误处理
- 图片识别失败：返回错误信息，不中断流程
- 记忆保存失败：打印警告，不影响对话
- API 超时：60秒超时保护

## 改进点

### 相比旧实现
1. ✅ 图片内容进入对话历史（可被后续引用）
2. ✅ 自动触发记忆提取（无需用户明确要求）
3. ✅ 双保险记忆机制（智能提取 + 强制入库）
4. ✅ 统一 API 入口（简化前端逻辑）
5. ✅ 更好的错误处理

### 性能优化
- 图片识别结果直接用于对话，不重复调用
- 记忆检索利用语义搜索（相似度匹配）
- 对话历史限制（避免上下文过长）

## 注意事项

1. **服务器自动重载**：修改 `.py` 文件后，uvicorn 会自动重启
2. **浏览器缓存**：修改 HTML 后需要**硬刷新**（Cmd+Shift+R）
3. **API Key**：确保 Qwen API Key 配置正确
4. **uploads 目录**：确保 `/uploads` 已挂载为静态文件目录

## 相关文件

- `/Users/rockts/Dev/xiaole-ai/main.py` - `/chat` API 实现
- `/Users/rockts/Dev/xiaole-ai/static/index.html` - `sendMessageFromDiv()` 函数
- `/Users/rockts/Dev/xiaole-ai/vision_tool.py` - 图片识别逻辑
- `/Users/rockts/Dev/xiaole-ai/memory.py` - 记忆管理
- `/Users/rockts/Dev/xiaole-ai/agent.py` - `_extract_and_remember()` 方法

---

**修复日期**: 2025年11月12日
**修复版本**: v0.6.1 (图片记忆功能)
