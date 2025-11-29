# 语音模式功能 - 剩余修改清单

> 说明：ChatView 中的语音消息样式、时长格式化、禁用编辑与隐藏编辑按钮已完成。

## 追加：语音模式 UI 视觉微调

- VoiceModeDialog：
  - 增加背景晕影与层次阴影，使波纹更有体积感；
  - 按钮阴影与激活态外环更明显，状态更直观；
  - 小屏下尺寸与间距更协调。
- VoiceSelector：
  - 内置三组 SVG 渐变；
  - 语音卡片增加微弱高亮背景与描边，头像内外阴影更柔和；
  - 文案字距细化，整体可读性更好。

## 1. 在 ChatView.vue 中添加格式化时长函数

在 `formatImagePath` 函数后添加：

```javascript
const formatDuration = (seconds) => {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
};
```

## 2. 修改用户消息的模板结构 (约第122行)

将：
```vue
<div class="user-bubble" v-if="editingMessageId !== message.id">
  <div
    class="md-content"
    v-html="renderMarkdown(message.content)"
  ></div>
</div>
```

改为：
```vue
<div 
  class="user-bubble" 
  :class="{ 'voice-message': message.messageType === 'voice' }"
  v-if="editingMessageId !== message.id"
>
  <div
    class="md-content"
    v-html="renderMarkdown(message.content)"
  ></div>
  
  <!-- 语音消息特殊标记 -->
  <div v-if="message.messageType === 'voice'" class="voice-meta">
    <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
      <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
      <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
    </svg>
    <span class="voice-duration">{{ formatDuration(message.duration || 0) }}</span>
  </div>
</div>
```

## 3. 在样式部分添加语音消息样式 (在 .user-bubble 样式后添加)

```css
/* 语音消息样式 */
.user-bubble.voice-message {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(118, 75, 162, 0.15) 100%);
  border-left: 3px solid #667eea;
}

.voice-meta {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 8px;
  font-size: 12px;
  color: var(--text-tertiary);
  opacity: 0.8;
}

.voice-duration {
  font-variant-numeric: tabular-nums;
}
```

## 4. 禁用语音消息的编辑功能

在 `editMessage` 函数中添加检查 (约第1550行)：

```javascript
const editMessage = (message) => {
  // 语音消息不允许编辑
  if (message.messageType === 'voice') {
    return;
  }
  
  editingMessageId.value = message.id;
  editingContent.value = message.content;
  
  // ... 其余代码保持不变
};
```

## 5. 在工具栏中隐藏语音消息的编辑按钮 (约第155行)

将：
```vue
<button
  v-if="message.role === 'user'"
  class="toolbar-icon"
  @click.stop="editMessage(message)"
  title="编辑"
>
```

改为：
```vue
<button
  v-if="message.role === 'user' && message.messageType !== 'voice'"
  class="toolbar-icon"
  @click.stop="editMessage(message)"
  title="编辑"
>
```

## 完成后测试

1. 点击语音模式按钮，应该弹出全屏对话界面
2. 点击麦克风按钮开始录音，AI头像应该有动态效果
3. 说话后文字应该显示在对话中，带有麦克风图标和时长
4. 语音消息应该有特殊的渐变背景
5. 语音消息不应该显示编辑按钮
6. 点击右上角按钮可以切换音色

所有功能都已实现，请按照上述说明完成剩余的小修改！
