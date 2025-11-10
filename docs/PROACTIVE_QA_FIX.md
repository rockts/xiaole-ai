# 主动问答修复说明

## 🐛 发现的问题

### 问题1: 问题识别不全
**症状**: 用户问"我们最近一次聊购物是什么时候？"，没有被识别为问题

**原因**: 问题模式中缺少关键疑问词：
- ❌ "什么时候"（时间）
- ❌ "哪里"（地点）  
- ❌ "哪个"、"哪种"（选择）
- ❌ "几个"（数量）
- ❌ "怎样"（方式）

**修复**: 
```python
# 修改前
QUESTION_PATTERNS = [
    r'(什么|啥|哪|谁|多少|怎么|为什么|如何)',
    ...
]

# 修改后
QUESTION_PATTERNS = [
    r'(什么|啥|什么时候|哪里|哪个|哪种|哪|谁|多少|几个|怎么|为什么|如何|怎样)',
    ...
]
```

### 问题2: 显示重复记录
**症状**: 主动问答历史中出现重复的问题记录

**原因**: 
- 保存时按 `user_id` 去重 ✅
- 查询时按 `session_id` 查询 ❌
- 结果：不同会话的相同问题都被显示出来

**修复**: 
修改 `get_pending_followups()` 和 `get_followup_history()`：
- 使用 `user_id` 查询（而不是 `session_id`）
- 使用子查询去重：每个 `original_question` 只保留最新的一条
- SQL 逻辑：
  ```sql
  SELECT * FROM proactive_questions
  WHERE id IN (
      SELECT MAX(id) 
      FROM proactive_questions 
      WHERE user_id = ? AND followup_asked = False
      GROUP BY original_question
  )
  ORDER BY confidence_score DESC
  ```

## ✅ 修复内容

### 文件: `proactive_qa.py`

**1. 问题识别增强（第38行）**
```python
QUESTION_PATTERNS = [
    r'(什么|啥|什么时候|哪里|哪个|哪种|哪|谁|多少|几个|怎么|为什么|如何|怎样)',
    r'(吗|呢|啊)\s*\??$',
    r'\?',
]
```

**2. 待追问列表去重（第298-345行）**
```python
def get_pending_followups(self, session_id: str, limit: int = 5) -> list:
    """获取待追问的问题列表（按user_id去重，避免跨会话重复）"""
    # 1. 从session_id获取user_id
    # 2. 使用子查询：每个original_question只保留最新的max(id)
    # 3. 按置信度排序
```

**3. 历史记录去重（第361-427行）**
```python
def get_followup_history(self, session_id=None, user_id=None, limit=20):
    """获取追问历史记录（去重显示，每个问题只显示最新一条）"""
    # 1. 优先使用user_id，没有则从session_id获取
    # 2. 使用子查询去重
    # 3. 按创建时间倒序
```

## 🧪 测试验证

### 方法1: 网页测试

1. 打开 http://localhost:8000/static/index.html
2. 输入问题：**"我们最近一次聊购物是什么时候？是关于电子产品还是日常用品？"**
3. 期望结果：
   - ✅ 问题被识别（包含"什么时候"）
   - ✅ 如果AI回答不完整（如"可能是上周"），应该生成追问
   - ✅ 页面底部弹出追问提示（如果触发）

### 方法2: 查看历史

1. 切换到右侧"主动问答"标签页
2. 期望结果：
   - ✅ 不再显示重复的问题记录
   - ✅ 每个问题只显示一条（最新的）
   - ✅ 显示置信度标签（绿色≥70%, 黄色50-69%, 红色<50%）
   - ✅ 显示"待追问"或"已追问"状态

### 方法3: API测试

```bash
# 查看历史记录（应该去重）
curl "http://localhost:8000/proactive/history?user_id=default_user&limit=10"

# 查看待追问列表（应该去重）
curl "http://localhost:8000/proactive/pending/你的session_id"
```

## 📊 预期效果

### 触发示例

**场景1: 时间问题**
```
用户: "我们最近一次聊购物是什么时候？"
AI: "我不太确定具体时间"
→ 触发追问！置信度: 65% (基础50% + 标记15%)
追问: "关于'我们最近一次聊购物是什么时候？'，您能说得更具体一些吗？"
```

**场景2: 地点问题**
```
用户: "这个东西在哪里买的？"
AI: "可能是网上"
→ 触发追问！置信度: 65%
追问: "您提到'这个东西在哪里买的？'，具体是指哪个呢？"
```

**场景3: 选择问题**
```
用户: "你喜欢哪个编程语言？"
AI: "不好说"
→ 触发追问！置信度: 80% (基础50% + 标记15% + 超短30% - 但长度5字)
```

### 不触发示例

```
用户: "我们最近一次聊购物是什么时候？"
AI: "上个月您询问过关于手机和平板的购买建议，那是在11月5日下午"
→ 不触发（回答完整且详细）
```

## 🔍 调试方法

### 查看日志
```bash
tail -f logs/xiaole_ai.log | grep "主动问答"
```

看到以下信息说明功能正常：
```
# 有分析但没触发（AI回答完整）
ℹ️ 无需存储: xxx

# 分析出错
主动问答分析失败: xxx

# 成功保存
（没有特定日志，但数据库有记录）
```

### 查看数据库
```sql
-- 查看最近的记录
SELECT 
    id,
    original_question,
    confidence_score,
    followup_asked,
    created_at
FROM proactive_questions
WHERE user_id = 'default_user'
ORDER BY created_at DESC
LIMIT 10;

-- 检查重复
SELECT 
    original_question,
    COUNT(*) as count
FROM proactive_questions
WHERE user_id = 'default_user'
AND followup_asked = False
GROUP BY original_question
HAVING COUNT(*) > 1;
```

## 💡 后续优化建议

1. **智能合并追问**: 多个相关问题合并成一个追问
2. **用户偏好学习**: 记录哪些追问被点击，优化置信度算法
3. **多轮追问**: 支持追问后继续追问
4. **追问时机控制**: 避免频繁打断用户

## ✅ 修复完成

- ✅ 问题识别：新增5个常用疑问词
- ✅ 去重逻辑：使用user_id + 子查询
- ✅ 服务已重启：http://localhost:8000

**现在可以测试了！** 试试问："我们最近一次聊购物是什么时候？是关于电子产品还是日常用品？"
