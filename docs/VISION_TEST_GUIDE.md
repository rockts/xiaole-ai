# 图片识别功能测试指南

**版本**: v0.6.0 Phase 4 Day 1  
**日期**: 2025-11-11

## 📋 功能概述

小乐AI现已支持图片识别功能，可以：
- 📤 上传图片文件
- 🔍 使用Claude Vision或GPT-4V识别图片内容
- 💬 在对话中显示分析结果

## 🚀 快速开始

### 1. 配置API密钥

编辑 `.env` 文件，添加以下任一密钥：

```bash
# 选项1：使用Claude Vision（推荐）
CLAUDE_API_KEY=your_claude_key_here

# 选项2：使用GPT-4V
OPENAI_API_KEY=your_openai_key_here
```

### 2. 启动服务器

```bash
cd /Users/rockts/Dev/xiaole-ai
source venv/bin/activate
python main.py
```

访问: http://localhost:8000

### 3. 测试图片上传

1. 点击聊天输入框左侧的 **📷 按钮**
2. 选择一张图片（支持 jpg/png/gif/webp/bmp）
3. 图片预览会出现在输入框上方
4. 点击 **🔍 识别图片** 按钮
5. 等待几秒，识别结果会显示在聊天中

## 🧪 测试场景

### 场景1：基础图片识别

**测试图片**: 风景照、建筑物、动物等
**预期结果**: 详细描述图片中的物体、场景、颜色等

**操作步骤**:
1. 上传一张风景照
2. 点击识别
3. 查看描述是否准确

### 场景2：文字识别（OCR）

**测试图片**: 包含文字的图片（文档、截图、海报等）
**预期结果**: 识别并提取图片中的文字内容

**操作步骤**:
1. 上传包含文字的图片
2. 点击识别
3. 检查是否准确识别文字

### 场景3：复杂场景分析

**测试图片**: 多人物、多物体的复杂场景
**预期结果**: 识别主要元素和它们的关系

**操作步骤**:
1. 上传复杂场景图片
2. 点击识别
3. 验证是否理解场景构成

### 场景4：文件格式测试

**测试不同格式**:
- ✅ JPG/JPEG
- ✅ PNG
- ✅ GIF
- ✅ WEBP
- ✅ BMP

**预期结果**: 所有格式都能正常上传和识别

### 场景5：边界测试

**测试项目**:
1. 大文件（接近20MB）
2. 小文件（几KB）
3. 超大文件（>20MB，应该拒绝）
4. 非图片文件（应该拒绝）

**预期结果**: 
- 20MB内文件正常处理
- 超大文件显示错误提示
- 非图片文件显示格式错误

## 📊 API端点测试

### 1. 上传API测试

```bash
# 使用curl测试上传
curl -X POST http://localhost:8000/api/vision/upload \
  -F "file=@/path/to/test/image.jpg"
```

**预期响应**:
```json
{
  "success": true,
  "file_path": "uploads/20251111_123456_image.jpg",
  "filename": "image.jpg",
  "size": 123456
}
```

### 2. 分析API测试

```bash
# 使用curl测试分析
curl -X POST http://localhost:8000/api/vision/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "image_path": "uploads/20251111_123456_image.jpg",
    "prompt": "请详细描述这张图片的内容"
  }'
```

**预期响应**:
```json
{
  "success": true,
  "description": "这是一张...",
  "model": "claude-3.5-sonnet",
  "timestamp": "2025-11-11T12:34:56.789"
}
```

## ⚠️ 常见问题

### 问题1: 上传失败

**可能原因**:
- 文件格式不支持
- 文件太大（>20MB）
- python-multipart未安装

**解决方案**:
```bash
pip install python-multipart
```

### 问题2: 识别失败

**可能原因**:
- API密钥未配置
- API密钥无效
- 网络连接问题
- API配额用尽

**解决方案**:
1. 检查 `.env` 文件配置
2. 验证API密钥有效性
3. 检查网络连接
4. 查看日志: `tail -f /tmp/xiaole_server.log`

### 问题3: 图片不显示预览

**可能原因**:
- 浏览器不支持FileReader API
- 图片文件损坏

**解决方案**:
1. 使用现代浏览器（Chrome/Firefox/Safari）
2. 尝试其他图片

## 📈 性能指标

| 指标 | 预期值 |
|------|--------|
| 上传速度 | <2秒（5MB图片） |
| 识别速度 | 3-10秒（取决于API） |
| 支持格式 | 5种（jpg/png/gif/webp/bmp） |
| 最大文件 | 20MB |

## 🔍 调试技巧

### 1. 查看浏览器控制台

打开开发者工具（F12），查看Console标签：
- 上传请求状态
- API响应内容
- JavaScript错误

### 2. 查看服务器日志

```bash
tail -f /tmp/xiaole_server.log
```

关注：
- API调用记录
- 错误堆栈
- 响应时间

### 3. 测试API端点

使用Postman或curl直接测试API：
- `/api/vision/upload` - 上传端点
- `/api/vision/analyze` - 分析端点

## ✅ 测试检查清单

- [ ] 上传JPG图片成功
- [ ] 上传PNG图片成功
- [ ] 识别风景照准确
- [ ] 识别文字图片准确
- [ ] 大文件（10MB+）正常处理
- [ ] 超大文件（>20MB）正确拒绝
- [ ] 非图片文件正确拒绝
- [ ] 预览图片正常显示
- [ ] 移除预览功能正常
- [ ] 识别结果正确显示在聊天中
- [ ] 错误提示清晰明确
- [ ] API响应时间合理

## 📝 报告问题

如果发现问题，请记录：
1. 操作步骤
2. 预期结果 vs 实际结果
3. 浏览器和版本
4. 错误信息（控制台/日志）
5. 测试图片信息（格式、大小）

提交到项目Issue或直接联系开发者。

---

**相关文件**:
- `vision_tool.py` - 后端实现
- `main.py` - API接口
- `static/index.html` - 前端界面
- `tests/test_vision_tool.py` - 单元测试

**文档更新**: 2025-11-11
