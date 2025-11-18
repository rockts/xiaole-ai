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
          <div class="message-avatar">
            {{ message.role === "user" ? "👤" : "🤖" }}
          </div>
          <div class="message-content">
            <img
              v-if="message.image_path"
              :src="formatImagePath(message.image_path)"
              alt="图片"
              class="message-image"
            />
            <div v-html="renderMarkdown(message.content)"></div>
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
import { ref, computed, watch, nextTick, onMounted } from "vue";
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
    nextTick(() => scrollToBottom());
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
  padding: 24px 20px;
  display: flex;
  justify-content: center;
}

.chat-inner {
  width: 100%;
  max-width: 768px;
}

.message {
  margin-bottom: 24px;
  display: flex;
}

.message.user {
  justify-content: flex-end;
}

.message.user .message-content {
  background: var(--message-user-bg);
  border-radius: 18px 18px 4px 18px;
}

.message.assistant .message-content {
  background: var(--message-ai-bg);
  border-radius: 18px 18px 18px 4px;
}

.message-content {
  padding: 10px 14px;
  max-width: 70%;
  line-height: 1.6;
  font-size: 15px;
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
  background: rgba(0, 0, 0, 0.05);
  padding: 12px;
  border-radius: 6px;
  overflow-x: auto;
  margin: 0.75em 0;
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

.input-container {
  padding: 16px 20px 24px;
  border-top: none;
  background: transparent;
  flex-shrink: 0;
}

.input-wrapper {
  max-width: 768px;
  margin: 0 auto;
  display: flex;
  gap: 8px;
  align-items: center;
  background: var(--bg-secondary);
  border: 1px solid var(--border-medium);
  border-radius: 26px;
  padding: 12px 16px;
  transition: all var(--duration-fast) var(--ease-out);
  box-shadow: 0 0 0 0 transparent;
}

.input-wrapper:focus-within {
  background: var(--bg-primary);
  border-color: var(--text-tertiary);
  box-shadow: none;
}

.input-controls {
  display: flex;
  align-items: center;
  gap: 4px;
  width: 100%;
}

.message-editor {
  flex: 1;
  max-height: 200px;
  overflow-y: auto;
  outline: none;
  padding: 4px 8px;
  color: var(--text-primary);
  font-size: 15px;
  line-height: 1.5;
}

.message-editor:empty:before {
  content: attr(data-placeholder);
  color: var(--text-tertiary);
}

.icon-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  transition: all var(--duration-fast) var(--ease-out);
  color: var(--text-secondary);
  flex-shrink: 0;
}

.icon-btn svg {
  stroke: currentColor;
  width: 20px;
  height: 20px;
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
  width: 40px;
  height: 40px;
}

.voice-mode-btn svg {
  width: 32px;
  height: 32px;
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
  gap: 16px !important;
  align-items: flex-start !important;
  padding: 24px 0 !important;
  border-bottom: 1px solid var(--border-light) !important;
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

.message-content {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.message-image {
  max-width: 100%;
  max-height: 400px;
  border-radius: 8px;
  border: 1px solid var(--border-light);
}
</style>
