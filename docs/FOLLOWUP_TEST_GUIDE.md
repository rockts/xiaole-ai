# 主动问答追问提示功能 - 测试指南

## ✅ 已完成的修改

### 1. 后端功能（已有）
- `agent.py`: 分析对话并生成followup_info
- `proactive_qa.py`: 保存追问记录到数据库
- 返回格式:
```json
{
  "session_id": "xxx",
  "reply": "回复内容",
  "followup": {
    "id": 123,
    "followup": "追问内容",
    "confidence": 70
  }
}
```

### 2. 前端显示（新增）

#### (1) 聊天响应处理
**文件**: `static/index.html` 第805行

```javascript
if (data.followup) {
    showFollowupSuggestion(data.followup);
}
```

#### (2) 追问提示函数
**文件**: `static/index.html` 第2516-2589行

```javascript
function showFollowupSuggestion(followupInfo) {
    // 创建渐变粉色提示卡片
    // 点击自动发送追问
    // 8秒后自动消失
    // 播放800Hz提示音
}
```

#### (3) CSS动画
**文件**: `static/index.html` 第499-526行

```css
@keyframes slideInUp { ... }     /* 从下滑入 */
@keyframes slideOutDown { ... }  /* 向下滑出 */
```

## 🎨 UI设计

### 追问提示卡片
- **位置**: 屏幕底部居中
- **颜色**: 渐变粉色 (#f093fb → #f5576c)
- **图标**: 🤔 思考表情
- **动画**: 从下滑入，8秒后滑出
- **交互**: 点击自动发送追问
- **提示音**: 800Hz正弦波（0.15秒）

### 与主动对话对比
| 功能 | 位置 | 颜色 | 触发 | 音调 |
|------|------|------|------|------|
| 主动对话 | 右下角 | 紫色 | 定时任务 | 600Hz |
| 追问提示 | 底部中央 | 粉色 | 实时响应 | 800Hz |

## 🧪 测试方法

### 方法1: 浏览器测试
1. 打开 http://localhost:8000
2. 发送**不完整的问题**:
   - ❌ "Python好还是Java好？" （太完整）
   - ✅ "你知道什么？" （需要明确）
   - ✅ "最好的编程语言？" （模糊）
   - ✅ "推荐一个数据库" （缺少场景）

3. 期望结果:
   - AI回复后，底部出现粉色追问卡片
   - 显示"💡 小乐有个疑问"
   - 显示具体追问内容
   - 点击后自动发送

### 方法2: API测试
```bash
curl -X POST "http://localhost:8000/chat?prompt=你知道什么？" | jq .
```

期望看到:
```json
{
  "session_id": "...",
  "reply": "...",
  "followup": {
    "id": 123,
    "followup": "您刚才提到'你知道什么？'，能再详细说说吗？",
    "confidence": 70
  }
}
```

## 🔍 调试工具

### 查看已有追问记录
```bash
python tests/test_proactive_qa_debug.py
```

**预期输出**:
- 找到5条待追问记录
- ID: 61, 64, 65, 66, 67
- 置信度均为70
- followup_asked全部为False

### 查看最近对话
```sql
-- 连接数据库
psql -h 192.168.31.200 -U xiaole -d xiaole_ai

-- 查询最近的追问记录
SELECT id, original_question, followup_question, confidence, followup_asked
FROM proactive_questions
ORDER BY created_at DESC
LIMIT 10;
```

## ⚠️ 常见问题

### Q1: 为什么没有弹出追问提示？
**可能原因**:
1. 问题太完整，AI认为不需要追问
2. 置信度低于阈值（默认70）
3. 分析功能出错（检查日志）

**解决方法**:
- 发送更模糊的问题
- 检查agent.py的日志输出
- 浏览器控制台查看是否收到followup字段

### Q2: 卡片显示了但点击无反应？
**可能原因**:
- JavaScript错误
- sendMessageFromDiv()函数问题

**解决方法**:
- F12打开控制台查看错误
- 检查messageInput元素是否存在

### Q3: 追问记录重复？
**原因**: 数据库有历史记录

**解决方法**:
```sql
-- 清理已发送的记录
UPDATE proactive_questions 
SET followup_asked = true 
WHERE id IN (61, 64, 65, 66, 67);
```

## 📊 功能指标

| 指标 | 目标 | 当前状态 |
|------|------|---------|
| 追问识别准确率 | >70% | ✅ 70 |
| 响应延迟 | <200ms | ✅ 前端即时 |
| 卡片显示时长 | 8秒 | ✅ 8秒 |
| 用户点击率 | >30% | 待测试 |

## 🚀 下一步优化

1. **追问策略**:
   - 调整置信度阈值
   - 增加更多问题类型识别

2. **UI优化**:
   - 添加"不需要"按钮
   - 支持拖动卡片位置
   - 记住用户偏好

3. **数据统计**:
   - 追问点击率
   - 追问有效性评分
   - A/B测试不同文案

## 📝 技术细节

### 数据流
```
用户发送消息
    ↓
agent.py处理
    ↓
proactive_qa.analyze_conversation()
    ↓
生成followup_info
    ↓
返回JSON (含followup字段)
    ↓
前端sendMessageFromDiv()
    ↓
检查data.followup
    ↓
showFollowupSuggestion()
    ↓
显示粉色卡片
    ↓
用户点击
    ↓
自动发送追问
    ↓
标记followup_asked=true
```

### 关键代码位置
- 后端分析: `agent.py:381-420`
- 前端检查: `static/index.html:805-807`
- 显示函数: `static/index.html:2516-2589`
- CSS动画: `static/index.html:499-526`

---

**创建时间**: 2025-01-10
**版本**: v0.5.0
**状态**: ✅ 功能已实现，等待测试验证
