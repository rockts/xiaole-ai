<template>
  <div class="chat-view" :class="{ empty: isEmptyChat }">
    <!-- 空状态问候语 -->
    <div v-if="isEmptyChat" class="welcome-message">
      <div class="welcome-icon">👋</div>
      <h2 class="welcome-title">{{ currentGreeting }}</h2>
    </div>

    <div class="chat-container" ref="chatContainer">
      <div class="chat-inner">
        <div
          v-for="message in messages"
          :key="message.id"
          class="message"
          :class="message.role"
        >
          <div class="message-content">
            <img
              v-if="message.image_path"
              :src="formatImagePath(message.image_path)"
              alt="图片"
              class="message-image"
              @click="openImage(formatImagePath(message.image_path))"
            />
            <div
              class="md-content"
              v-html="renderMarkdown(message.content)"
            ></div>
          </div>
        </div>

        <div v-if="isTyping" class="message assistant">
          <div class="message-avatar">🤖</div>
          <div class="message-content">
            <div class="typing-indicator">
              <span class="typing-dot"></span>
              <span class="typing-dot"></span>
              <span class="typing-dot"></span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 图片预览遮罩 -->
    <div
      v-if="imagePreviewUrl"
      class="image-preview-overlay"
      @click="closeImagePreview"
    >
      <img :src="imagePreviewUrl" alt="预览图" class="image-preview" />
    </div>

    <div class="input-container">
      <div class="input-wrapper">
        <div class="input-controls">
          <button class="icon-btn" @click="handleUpload" title="附件">
            <svg
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <line x1="12" y1="5" x2="12" y2="19"></line>
              <line x1="5" y1="12" x2="19" y2="12"></line>
            </svg>
          </button>

          <div
            ref="messageInput"
            class="message-editor"
            contenteditable="true"
            @keydown.enter="handleEnter"
            @input="handleInput"
            data-placeholder="给 小乐 AI 发送消息..."
          ></div>

          <button
            class="icon-btn"
            :class="{ recording: isRecording }"
            @click="handleVoiceInput"
            title="语音输入"
          >
            <svg
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <path
                d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"
              ></path>
              <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
              <line x1="12" y1="19" x2="12" y2="23"></line>
              <line x1="8" y1="23" x2="16" y2="23"></line>
            </svg>
          </button>

          <button
            class="icon-btn voice-mode-btn"
            :class="{ active: isVoiceMode }"
            @click="toggleVoiceMode"
            title="语音模式"
          >
            <svg
              width="32"
              height="32"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="1.5"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <circle
                cx="12"
                cy="12"
                r="11.5"
                fill="currentColor"
                opacity="0.15"
              ></circle>
              <line x1="8" y1="13.5" x2="8" y2="10.5"></line>
              <line x1="10.5" y1="15" x2="10.5" y2="9"></line>
              <line x1="13.5" y1="15" x2="13.5" y2="9"></line>
              <line x1="16" y1="13.5" x2="16" y2="10.5"></line>
            </svg>
          </button>
        </div>
      </div>
    </div>

    <input
      ref="fileInput"
      type="file"
      accept="image/*"
      style="display: none"
      @change="handleFileChange"
    />
  </div>
</template>

<script setup>
import {
  ref,
  computed,
  watch,
  nextTick,
  onMounted,
  onBeforeUnmount,
} from "vue";
import { useRoute, useRouter } from "vue-router";
import { useChatStore } from "@/stores/chat";
import { storeToRefs } from "pinia";
import { marked } from "marked";

const route = useRoute();
const router = useRouter();
const chatStore = useChatStore();
const { messages, sessionInfo, isTyping } = storeToRefs(chatStore);
const isEmptyChat = computed(
  () => (messages.value?.length || 0) === 0 && !isTyping.value
);

const messageInput = ref(null);
const chatContainer = ref(null);
const fileInput = ref(null);
const isRecording = ref(false);
const isVoiceMode = ref(false);
const imagePreviewUrl = ref(null);

const greetings = [
  "你好！很高兴见到你",
  "嗨！有什么可以帮你的吗？",
  "欢迎回来！",
  "你好呀～准备好开始了吗？",
  "Hi！让我们开始吧",
];

const currentGreeting = ref("");

// 随机选择问候语
const selectRandomGreeting = () => {
  const hour = new Date().getHours();
  let timeGreeting = "";

  if (hour >= 5 && hour < 12) {
    timeGreeting = "早上好！";
  } else if (hour >= 12 && hour < 18) {
    timeGreeting = "下午好！";
  } else if (hour >= 18 && hour < 22) {
    timeGreeting = "晚上好！";
  } else {
    timeGreeting = "夜深了，";
  }

  const randomGreeting =
    greetings[Math.floor(Math.random() * greetings.length)];
  currentGreeting.value = timeGreeting + " " + randomGreeting;
};

const sessionId = computed(() => route.params.sessionId);

watch(
  sessionId,
  (newId) => {
    if (newId) {
      chatStore.loadSession(newId);
    } else {
      chatStore.clearCurrentSession();
    }
  },
  { immediate: true }
);

watch(
  messages,
  () => {
    nextTick(() => {
      scrollToBottom();
      enhanceRenderedContent();
    });
  },
  { deep: true }
);

const renderMarkdown = (content) => {
  return marked.parse(content || "");
};

const formatImagePath = (path) => {
  if (!path) return "";
  // 如果路径不是以 / 或 http 开头，添加 / 前缀
  if (!path.startsWith("/") && !path.startsWith("http")) {
    return "/" + path;
  }
  return path;
};

const scrollToBottom = () => {
  if (chatContainer.value) {
    const inner = chatContainer.value.querySelector(".chat-inner");
    if (inner) {
      inner.scrollTop = inner.scrollHeight;
    }
  }
};

const openImage = (src) => {
  if (!src) return;
  imagePreviewUrl.value = src;
  try {
    document.body.style.overflow = "hidden";
  } catch (_) {}
};

const closeImagePreview = () => {
  imagePreviewUrl.value = null;
  try {
    document.body.style.overflow = "";
  } catch (_) {}
};

// 委托点击 Markdown 图片放大预览
const onChatClick = (e) => {
  const target = e.target;
  if (!target) return;
  if (
    target.tagName === "IMG" &&
    target.closest &&
    target.closest(".md-content")
  ) {
    const src = target.currentSrc || target.src;
    openImage(src);
  }
};

// 为代码块添加复制按钮等增强，避免重复添加
const enhanceRenderedContent = () => {
  if (!chatContainer.value) return;
  const blocks = chatContainer.value.querySelectorAll(
    ".md-content pre:not([data-has-copy])"
  );
  blocks.forEach((pre) => {
    pre.setAttribute("data-has-copy", "1");
    const btn = document.createElement("button");
    btn.className = "copy-btn";
    btn.type = "button";
    btn.textContent = "复制";
    btn.addEventListener("click", async (e) => {
      e.stopPropagation();
      try {
        const code = pre.querySelector("code");
        const text = code ? code.innerText : pre.innerText;
        await navigator.clipboard.writeText(text);
        const original = btn.textContent;
        btn.textContent = "已复制";
        btn.classList.add("copied");
        setTimeout(() => {
          btn.textContent = original;
          btn.classList.remove("copied");
        }, 1200);
      } catch (_) {}
    });
    pre.appendChild(btn);
  });
};

const handleInput = () => {
  // 处理输入
};

const handleEnter = (e) => {
  if (!e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
};

const sendMessage = async () => {
  const content = messageInput.value?.innerText?.trim();
  if (!content) return;

  await chatStore.sendMessage(content, null, router);
  messageInput.value.innerText = "";
};

const handleUpload = () => {
  fileInput.value?.click();
};

const handleFileChange = async (e) => {
  const file = e.target.files?.[0];
  if (file) {
    const imagePath = await chatStore.uploadImage(file);
    if (imagePath) {
      await chatStore.sendMessage("", imagePath, router);
    }
    e.target.value = "";
  }
};

const handleVoice = () => {
  // 语音输入功能
  console.log("语音输入");
};

const handleVoiceInput = () => {
  isRecording.value = !isRecording.value;
  if (isRecording.value) {
    console.log("开始语音输入");
    // TODO: 调用语音识别 API
  } else {
    console.log("停止语音输入");
  }
};

const toggleVoiceMode = () => {
  isVoiceMode.value = !isVoiceMode.value;
  console.log("语音模式:", isVoiceMode.value ? "开启" : "关闭");
  // TODO: 实现语音模式逻辑
};

const canSend = computed(() => {
  return messageInput.value?.innerText?.trim().length > 0;
});

onMounted(() => {
  scrollToBottom();
  selectRandomGreeting();
  nextTick(enhanceRenderedContent);
  if (chatContainer.value) {
    chatContainer.value.addEventListener("click", onChatClick);
  }
});

onBeforeUnmount(() => {
  if (chatContainer.value) {
    chatContainer.value.removeEventListener("click", onChatClick);
  }
});
</script>

<style scoped>
.chat-view {
  display: flex;
  flex-direction: column;
  height: 100%;
  position: relative;
  background: var(--bg-primary);
}

/* 欢迎消息 */
.welcome-message {
  position: absolute;
  top: 35%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  z-index: 1;
  animation: fadeInUp 0.5s ease-out;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translate(-50%, -45%);
  }
  to {
    opacity: 1;
    transform: translate(-50%, -50%);
  }
}

.welcome-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.welcome-title {
  font-size: 24px;
  font-weight: 500;
  color: var(--text-primary);
  letter-spacing: -0.5px;
}

.welcome-subtitle {
  font-size: 16px;
  color: var(--text-secondary);
}

/* 空聊天时，整体上下左右居中输入框 */
.chat-view.empty {
  justify-content: center;
  align-items: center;
}

.chat-view.empty .chat-container {
  display: none;
}

.chat-view.empty .input-container {
  position: static;
  background: transparent;
  border-top: none;
  padding: 0;
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
}

.chat-view.empty .input-wrapper {
  max-width: 720px;
  width: 90%;
  box-shadow: none;
  background: var(--bg-secondary);
  border: 1px solid var(--border-medium);
}

.chat-container {
  flex: 1;
  overflow-y: auto;
  padding: 22px 20px;
  display: flex;
  justify-content: center;
  background: var(--bg-primary);
}

.chat-inner {
  width: 100%;
  max-width: 740px;
}

.message {
  margin-bottom: 8px;
  display: flex;
}

.message.user {
  justify-content: flex-end;
}

/* 左右对齐布局，无头像时内容居左/居右 */
.message.assistant {
  justify-content: flex-start;
}

/* 内容区宽度与阅读体验 */
.message-content {
  padding: 0;
  max-width: 740px;
}

.message-content :deep(p) {
  margin: 0 0 0.75em 0;
  line-height: 1.6;
}

.message-content :deep(p:last-child) {
  margin-bottom: 0;
}

.message-content :deep(ul),
.message-content :deep(ol) {
  margin: 0.5em 0;
  padding-left: 1.5em;
}

.message-content :deep(li) {
  margin: 0.25em 0;
}

.message-content :deep(code) {
  background: rgba(0, 0, 0, 0.05);
  padding: 0.2em 0.4em;
  border-radius: 3px;
  font-size: 0.9em;
}

.message-content :deep(pre) {
  background: var(--code-bg, rgba(0, 0, 0, 0.06));
  padding: 14px 16px;
  border-radius: 10px;
  overflow-x: auto;
  margin: 0.9em 0;
  position: relative;
}

.message-content :deep(pre code) {
  background: none;
  padding: 0;
}

.message-image {
  max-width: 300px;
  margin-top: 8px;
  border-radius: 8px;
}

/* 统一 Markdown 内容区域样式 */
.md-content :deep(h1),
.md-content :deep(h2),
.md-content :deep(h3) {
  margin: 0.7em 0 0.4em;
  line-height: 1.2;
}
.md-content :deep(h4),
.md-content :deep(h5),
.md-content :deep(h6) {
  margin: 0.6em 0 0.3em;
}
.md-content :deep(a) {
  color: var(--brand-primary);
  text-decoration: none;
}
.md-content :deep(a:hover) {
  text-decoration: underline;
}
.md-content :deep(blockquote) {
  margin: 0.9em 0;
  padding: 8px 12px;
  border-left: 3px solid var(--border-medium);
  background: var(--bg-secondary);
  border-radius: 6px;
}
.md-content :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 12px 0;
}
.md-content :deep(th),
.md-content :deep(td) {
  border: 1px solid var(--border-light);
  padding: 8px 10px;
}
.md-content :deep(img) {
  max-width: 100%;
  border-radius: 10px;
  border: 1px solid var(--border-light);
}

/* 代码复制按钮 */
.copy-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  border: 1px solid var(--border-light);
  background: var(--bg-primary);
  color: var(--text-secondary);
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 6px;
  cursor: pointer;
}
.copy-btn:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}
.copy-btn.copied {
  color: var(--brand-primary);
  border-color: var(--brand-primary);
}

.input-container {
  padding: 12px 16px 16px;
  border-top: none;
  background: transparent;
  flex-shrink: 0;
}

.input-wrapper {
  max-width: 740px;
  margin: 0 auto;
  display: flex;
  gap: 6px;
  align-items: center;
  background: var(--bg-secondary);
  border: 1px solid var(--border-light);
  border-radius: 14px;
  padding: 8px 10px;
  transition: all var(--duration-fast) var(--ease-out);
  box-shadow: 0 0 0 0 transparent;
}

.input-wrapper:focus-within {
  background: var(--bg-primary);
  border-color: var(--text-tertiary);
  box-shadow: 0 0 0 3px
    color-mix(in srgb, var(--brand-primary) 15%, transparent);
}

.input-controls {
  display: flex;
  align-items: center;
  gap: 4px;
  width: 100%;
}

.message-editor {
  flex: 1;
  max-height: 160px;
  overflow-y: auto;
  outline: none;
  padding: 2px 6px;
  color: var(--text-primary);
  font-size: 14.5px;
  line-height: 1.45;
  min-height: 24px;
}

.message-editor:empty:before {
  content: attr(data-placeholder);
  color: var(--text-tertiary);
}

.icon-btn {
  width: 28px;
  height: 28px;
  border: none;
  background: transparent;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  transition: all var(--duration-fast) var(--ease-out);
  color: var(--text-secondary);
  flex-shrink: 0;
}

.icon-btn svg {
  stroke: currentColor;
  width: 18px;
  height: 18px;
}

[data-theme="dark"] .icon-btn svg {
  stroke: var(--text-secondary);
}

[data-theme="dark"] .icon-btn:hover svg {
  stroke: var(--text-primary);
}

.icon-btn:hover:not(:disabled) {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.icon-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.icon-btn.active {
  background: var(--brand-primary);
  color: var(--text-inverse);
}

.icon-btn.active svg {
  stroke: var(--text-inverse);
}

.icon-btn.recording {
  background: var(--error);
  color: var(--text-inverse);
  animation: pulse 1.5s ease-in-out infinite;
}

.icon-btn.recording svg {
  stroke: var(--text-inverse);
}

@keyframes pulse {
  0%,
  100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.8;
    transform: scale(1.05);
  }
}

.icon-btn.primary {
  background: transparent;
  color: var(--text-secondary);
}

.icon-btn.primary:hover:not(:disabled) {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.icon-btn.primary:not(:disabled):active {
  background: var(--bg-active);
}

.icon-btn.primary:disabled {
  background: transparent;
  opacity: 0.3;
}

.voice-mode-btn {
  width: 34px;
  height: 34px;
}

.voice-mode-btn svg {
  width: 28px;
  height: 28px;
}

.voice-mode-btn svg line {
  stroke: var(--text-primary);
}

[data-theme="dark"] .voice-mode-btn svg line {
  stroke: #ffffff;
}

/* ChatGPT 标准布局 */
.message {
  display: flex !important;
  flex-direction: row !important;
  gap: 10px !important;
  align-items: flex-start !important;
  padding: 14px 0 !important;
  border-bottom: none !important;
  position: relative;
  z-index: 0;
}

.message:last-child {
  border-bottom: none !important;
}

.message-avatar {
  flex-shrink: 0;
  width: 32px;
  height: 32px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  background: var(--bg-tertiary);
}

.message.assistant .message-avatar {
  background: #10a37f1a;
  color: #10a37f;
}
.message.user .message-avatar {
  background: #1f29371a;
}

.message-content {
  flex: 0 1 auto;
  min-width: 0;
  display: block;
  line-height: 1.7;
  font-size: 14.5px;
}
.message.assistant .message-content {
  margin-right: auto;
  max-width: 100%;
}
.message.user .message-content {
  margin-left: auto;
  max-width: 58%;
}

.message-image {
  max-width: 100%;
  max-height: 400px;
  border-radius: 8px;
  border: 1px solid var(--border-light);
  cursor: zoom-in;
}

/* 助手透明背景，用户右侧有气泡背景 */
.message.assistant {
  background: transparent;
  padding: 0 !important;
  margin: 0;
}
.chat-inner {
  padding: 0 16px;
}

/* 用户气泡更轻、更接近 ChatGPT 用户侧 */
.message.user .message-content {
  display: inline-block;
  background: var(--bg-secondary);
  border: none;
  border-radius: 9999px;
  padding: 8px 12px;
  white-space: pre-wrap;
  word-break: break-word;
}

/* Markdown 图片也可点击预览 */
.md-content :deep(img) {
  cursor: zoom-in;
}

/* 图片预览遮罩样式 */
.image-preview-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.65);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  cursor: zoom-out;
}
.image-preview {
  max-width: 92vw;
  max-height: 92vh;
  border-radius: 12px;
  box-shadow: 0 15px 60px rgba(0, 0, 0, 0.35);
}
</style>
