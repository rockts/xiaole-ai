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
          v-for="(message, idx) in messages"
          :key="message.id"
          class="message"
          :class="[
            message.role,
            {
              'new-group': idx === 0 || messages[idx - 1]?.role !== message.role,
            },
          ]"
        >
          <div class="message-content">
            <div class="message-toolbar">
              <button class="toolbar-icon" @click.stop="copyMessage(message)" title="复制">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                  <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                  <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                </svg>
              </button>
              <button v-if="message.role === 'assistant'" class="toolbar-icon" :class="{ active: feedbackState.get(message.id) === 'up' }" @click.stop="feedbackMessage(message, 'up')" title="有帮助">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M14 9V5a3 3 0 0 0-6 0v4"></path>
                  <path d="M5 15h12a2 2 0 0 0 2-2v-1a5 5 0 0 0-5-5H9l-4 8Z"></path>
                </svg>
              </button>
              <button v-if="message.role === 'assistant'" class="toolbar-icon" :class="{ active: feedbackState.get(message.id) === 'down' }" @click.stop="feedbackMessage(message, 'down')" title="不太好">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M10 15v4a3 3 0 0 0 6 0v-4"></path>
                  <path d="M19 9H7a2 2 0 0 0-2 2v1a5 5 0 0 0 5 5h4l4-8Z"></path>
                </svg>
              </button>
              <button v-if="message.role === 'assistant'" class="toolbar-icon" @click.stop="regenerateMessage(message)" title="重新生成">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                  <polyline points="23 4 23 10 17 10"></polyline>
                  <polyline points="1 20 1 14 7 14"></polyline>
                  <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10"></path>
                  <path d="M20.49 15a9 9 0 0 1-14.85 3.36L1 14"></path>
                </svg>
              </button>
              <button class="toolbar-icon" @click.stop="moreActions(message)" title="更多">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <circle cx="5" cy="12" r="1"></circle>
                  <circle cx="12" cy="12" r="1"></circle>
                  <circle cx="19" cy="12" r="1"></circle>
                </svg>
              </button>
            </div>
            <img v-if="message.image_path" :src="formatImagePath(message.image_path)" alt="图片" class="message-image" @click="openImage(formatImagePath(message.image_path))" />
            <template v-if="message.role === 'assistant'">
              <div class="assistant-bubble">
                <div class="md-content" v-html="renderMarkdown(message.content)"></div>
              </div>
            </template>
            <template v-else>
              <div class="user-bubble">
                <div class="md-content" v-html="renderMarkdown(message.content)"></div>
              </div>
            </template>
          </div>
        </div>

        <div v-if="isTyping" class="message assistant">
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

    <!-- 回到底部按钮 -->
    <button
      v-show="showScrollToBottom"
      class="scroll-to-bottom"
      @click="scrollToBottomSmooth"
      aria-label="回到底部"
    >
      <svg
        width="18"
        height="18"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      >
        <polyline points="6 9 12 15 18 9"></polyline>
      </svg>
    </button>

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
const showScrollToBottom = ref(false);
const feedbackState = ref(new Map());

const greetings = [
  "你好！很高兴见到你",
  "嗨！有什么可以帮你的吗？",
  "欢迎回来！",
  "你好呀～准备好开始了吗？",
  "Hi！让我们开始吧",
];

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
  return timeGreeting + " " + randomGreeting;
};

const currentGreeting = ref(selectRandomGreeting());

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

const copyMessage = async (message) => {
  try {
    const text = message?.content || "";
    if (!text) return;
    await navigator.clipboard.writeText(text);
  } catch (_) {}
};

const regenerateMessage = async (message) => {
  // 预留：调用后端重生该条回答或以该条为上下文重试
  // 这里先简单触发一次基于同一 prompt 的发送
  try {
    if (message?.role !== "assistant") return;
    const lastUser = [...messages.value]
      .reverse()
      .find((m) => m.role === "user");
    if (!lastUser?.content) return;
    await chatStore.sendMessage(lastUser.content, null, router);
  } catch (_) {}
};

const moreActions = (message) => {
  // 预留更多操作，如反馈、删除、引用、分享
  console.debug("更多操作", message?.id);
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
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight;
  }
};

const onScroll = () => {
  const el = chatContainer.value;
  if (!el) return;
  const nearBottom = el.scrollHeight - el.scrollTop - el.clientHeight < 140;
  showScrollToBottom.value = !nearBottom;
};

const scrollToBottomSmooth = () => {
  const el = chatContainer.value;
  if (!el) return;
  el.scrollTo({ top: el.scrollHeight, behavior: "smooth" });
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
    // 代码语言标签
    try {
      const codeEl = pre.querySelector("code");
      const cls = codeEl?.className || "";
      const m = cls.match(/language-([a-z0-9+#-]+)/i);
      if (m && !pre.querySelector(".code-lang")) {
        const label = document.createElement("span");
        label.className = "code-lang";
        label.textContent = m[1].toLowerCase();
        pre.appendChild(label);
      }
    } catch (_) {}

    // 复制按钮
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
  currentGreeting.value = selectRandomGreeting();
  nextTick(enhanceRenderedContent);
  if (chatContainer.value) {
    chatContainer.value.addEventListener("click", onChatClick);
    chatContainer.value.addEventListener("scroll", onScroll, { passive: true });
  }
});

onBeforeUnmount(() => {
  if (chatContainer.value) {
    chatContainer.value.removeEventListener("click", onChatClick);
    chatContainer.value.removeEventListener("scroll", onScroll);
  }
});

const feedbackMessage = async (message, type) => {
  try {
    const id = message?.id;
    if (!id) return;
    const current = feedbackState.value.get(id);
    if (current === type) {
      feedbackState.value.delete(id); // 取消当前选择
    } else {
      feedbackState.value.set(id, type);
    }
    // TODO: 可在此调用后端反馈接口
    console.debug("反馈", type, id);
  } catch (_) {}
};
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
.welcome-message { position: absolute; top: 35%; left: 50%; transform: translate(-50%, -50%); text-align: center; z-index: 10; animation: fadeInUp 0.5s ease-out; }
@keyframes fadeInUp { from { opacity: 0; transform: translate(-50%, -45%);} to { opacity: 1; transform: translate(-50%, -50%);} }
.welcome-icon { font-size: 48px; margin-bottom: 16px; }
.welcome-title { font-size: 24px; font-weight: 500; color: var(--text-primary); letter-spacing: -0.5px; }
.welcome-subtitle { font-size: 16px; color: var(--text-secondary); }
.chat-view.empty { justify-content: center; align-items: center; }
.chat-view.empty .chat-container { display: none; }
.chat-view.empty .input-container { position: static; background: transparent; border-top: none; padding: 0; display: flex; justify-content: center; align-items: center; width: 100%; }
.chat-view.empty .input-wrapper { max-width: 720px; width: 90%; box-shadow: none; background: var(--bg-secondary); border: 1px solid var(--border-medium); }
.chat-container { flex: 1; overflow-y: auto; padding: 0; display: flex; justify-content: center; background: var(--bg-primary); margin-bottom: 100px; }
.chat-inner { width: 100%; max-width: 740px; padding: 22px 20px; }
.message { margin-bottom: 8px; display: flex; }
.message.user { justify-content: flex-end; }
.message.assistant { justify-content: flex-start; }
.message-content { background: #f7f7f7; border-radius: 8px; margin: 8px 0; padding: 16px 20px 8px 20px; box-shadow: 0 1px 4px rgba(0,0,0,0.04); position: relative; }
.message-content :deep(p) { margin: 0 0 0.75em 0; line-height: 1.6; }
.message-content :deep(p:last-child) { margin-bottom: 0; }
.message-content :deep(ul), .message-content :deep(ol) { margin: 0.5em 0; padding-left: 1.5em; }
.message-content :deep(li) { margin: 0.25em 0; }
.message-content :deep(code) { background: rgba(0,0,0,0.05); padding: 0.2em 0.4em; border-radius: 3px; font-size: 0.9em; }
.message-content :deep(pre) { background: var(--code-bg, rgba(0,0,0,0.06)); padding: 34px 16px 14px; border-radius: 10px; overflow-x: auto; margin: 0.9em 0; position: relative; }
.message-content :deep(pre code) { background: none; padding: 0; }
.message-image { max-width: 320px; max-height: 180px; margin: 12px 0 0 0; border-radius: 6px; box-shadow: 0 1px 4px rgba(0,0,0,0.08); cursor: pointer; }
.md-content :deep(h1), .md-content :deep(h2), .md-content :deep(h3) { margin: 0.7em 0 0.4em; line-height: 1.2; }
.md-content :deep(h4), .md-content :deep(h5), .md-content :deep(h6) { margin: 0.6em 0 0.3em; }
.md-content :deep(a) { color: var(--brand-primary); text-decoration: none; }
.md-content :deep(a:hover) { text-decoration: underline; }
.md-content :deep(blockquote) { margin: 0.9em 0; padding: 8px 12px; border-left: 3px solid var(--border-medium); background: var(--bg-secondary); border-radius: 6px; }
.md-content :deep(table) { width: 100%; border-collapse: collapse; margin: 12px 0; }
.md-content :deep(th), .md-content :deep(td) { border: 1px solid var(--border-light); padding: 8px 10px; }
.md-content :deep(img) { max-width: 100%; border-radius: 10px; border: 1px solid var(--border-light); }
.copy-btn { position: absolute; top: 6px; right: 8px; border: 1px solid var(--border-light); background: var(--bg-primary); color: var(--text-secondary); font-size: 12px; padding: 4px 8px; border-radius: 6px; cursor: pointer; }
.copy-btn:hover { background: var(--bg-hover); color: var(--text-primary); }
.copy-btn.copied { color: var(--brand-primary); border-color: var(--brand-primary); }
.code-lang { position: absolute; top: 8px; left: 10px; font-size: 12px; color: var(--text-tertiary); background: var(--bg-primary); border: 1px solid var(--border-light); border-radius: 6px; padding: 2px 6px; }
.message-toolbar { position: absolute; top: 8px; right: 12px; display: flex; gap: 8px; opacity: 0.7; transition: opacity 0.2s; }
.message-content:hover .message-toolbar { opacity: 1; }
.toolbar-icon { background: none; border: none; padding: 2px; cursor: pointer; color: #888; border-radius: 4px; transition: background 0.2s, color 0.2s; }
.toolbar-icon:hover, .toolbar-icon.active { background: #eaeaea; color: #222; }
.input-container { padding: 12px 16px 16px; border-top: none; background: transparent; flex-shrink: 0; }
.input-wrapper { max-width: 760px; margin: 0 auto; display: flex; gap: 8px; align-items: center; background: var(--bg-primary); border: 1px solid var(--border-light); border-radius: 16px; padding: 6px 12px; transition: all 0.2s ease; box-shadow: 0 1px 3px rgba(0,0,0,0.04); }
.input-wrapper:focus-within { border-color: var(--border-light); box-shadow: 0 1px 4px rgba(0,0,0,0.06); }
.input-controls { display: flex; align-items: center; gap: 10px; width: 100%; }
.message-editor { flex: 1; max-height: 200px; overflow-y: auto; outline: none; padding: 10px 14px; color: var(--text-primary); font-size: 15px; line-height: 1.6; min-height: 24px; border: 1px solid var(--border-light); border-radius: 14px; background: var(--bg-secondary); transition: all 0.2s ease; }
.message-editor:focus { border-color: var(--brand-primary); background: var(--bg-primary); }
.message-editor:empty:before { content: attr(data-placeholder); color: var(--text-tertiary); }
.icon-btn { width: 28px; height: 28px; border: none; background: transparent; cursor: pointer; display: flex; align-items: center; justify-content: center; border-radius: 6px; transition: all var(--duration-fast) var(--ease-out); color: var(--text-secondary); flex-shrink: 0; }
.icon-btn svg { stroke: currentColor; width: 18px; height: 18px; }
[data-theme="dark"] .icon-btn svg { stroke: var(--text-secondary); }
[data-theme="dark"] .icon-btn:hover svg { stroke: var(--text-primary); }
.icon-btn:hover:not(:disabled) { background: var(--bg-hover); color: var(--text-primary); }
.icon-btn:disabled { opacity: 0.4; cursor: not-allowed; }
.icon-btn.active { background: var(--brand-primary); color: var(--text-inverse); }
.icon-btn.active svg { stroke: var(--text-inverse); }
.icon-btn.recording { background: var(--error); color: var(--text-inverse); animation: pulse 1.5s ease-in-out infinite; }
.icon-btn.recording svg { stroke: var(--text-inverse); }
@keyframes pulse { 0%,100% { opacity: 1; transform: scale(1);} 50% { opacity: 0.8; transform: scale(1.05);} }
.icon-btn.primary { background: transparent; color: var(--text-secondary); }
.icon-btn.primary:hover:not(:disabled) { background: var(--bg-hover); color: var(--text-primary); }
.icon-btn.primary:not(:disabled):active { background: var(--bg-active); }
.icon-btn.primary:disabled { background: transparent; opacity: 0.3; }
.voice-mode-btn { width: 34px; height: 34px; }
.voice-mode-btn svg { width: 28px; height: 28px; }
.voice-mode-btn svg line { stroke: var(--text-primary); }
[data-theme="dark"] .voice-mode-btn svg line { stroke: #ffffff; }
.scroll-to-bottom { position: fixed; right: 28px; bottom: 90px; width: 36px; height: 36px; border-radius: 10px; border: 1px solid var(--border-light); background: var(--bg-primary); color: var(--text-secondary); box-shadow: 0 6px 24px rgba(0,0,0,0.12); display: flex; align-items: center; justify-content: center; cursor: pointer; z-index: 1000; }
.scroll-to-bottom:hover { background: var(--bg-hover); color: var(--text-primary); }
.image-preview-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.65); display: flex; align-items: center; justify-content: center; z-index: 2000; cursor: zoom-out; }
.image-preview { max-width: 92vw; max-height: 92vh; border-radius: 12px; box-shadow: 0 15px 60px rgba(0,0,0,0.35); }
@media (max-width: 900px) { .input-wrapper { max-width: 98vw; } }
</style>
