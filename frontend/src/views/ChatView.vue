<template>
  <div class="chat-view" :class="{ empty: isEmptyChat }">
    <!-- 空状态问候语 -->
    <div v-if="isEmptyChat" class="welcome-message">
      <div class="welcome-icon">👋</div>
      <h2 class="welcome-title">{{ currentGreeting }}</h2>
    </div>

    <div
      class="chat-container"
      ref="chatContainer"
      :style="{ visibility: isLoadingSession ? 'hidden' : 'visible' }"
    >
      <div class="chat-inner">
        <div
          v-for="(message, idx) in messages"
          :key="message.id"
          class="message"
          :class="[
            message.role,
            {
              'new-group':
                idx === 0 || messages[idx - 1]?.role !== message.role,
            },
          ]"
        >
          <img
            v-if="message.image_path"
            :src="formatImagePath(message.image_path)"
            alt="图片"
            class="message-image"
            @click="openImage(formatImagePath(message.image_path))"
          />
          <template v-if="message.role === 'assistant'">
            <template v-if="message.status === 'thinking'">
              <div class="thinking-wrapper">
                <div class="thinking-dot"></div>
              </div>
            </template>
            <template v-else>
              <div
                class="md-content"
                :class="{ typing: message.status === 'typing' }"
                v-html="renderMarkdown(message.content)"
              ></div>
            </template>
          </template>
          <template v-else>
            <div class="user-bubble">
              <div
                class="md-content"
                v-html="renderMarkdown(message.content)"
              ></div>
            </div>
          </template>

          <div
            class="message-toolbar"
            v-if="message.role === 'user' || message.status === 'done'"
          >
            <button
              v-if="message.role === 'user'"
              class="toolbar-icon"
              @click.stop="editMessage(message)"
              title="编辑"
            >
              <svg
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <path
                  d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"
                ></path>
                <path
                  d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"
                ></path>
              </svg>
            </button>
            <button
              class="toolbar-icon"
              @click.stop="copyMessage(message)"
              title="复制"
            >
              <svg
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                <path
                  d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"
                ></path>
              </svg>
            </button>
            <button
              v-if="message.role === 'assistant'"
              class="toolbar-icon"
              :class="{ active: feedbackState.get(message.id) === 'up' }"
              @click.stop="feedbackMessage(message, 'up')"
              title="有帮助"
            >
              <svg
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <path d="M7 10v12"></path>
                <path
                  d="M15 5.88 14 10h5.83a2 2 0 0 1 1.92 2.56l-2.33 8A2 2 0 0 1 17.5 22H4a2 2 0 0 1-2-2v-8a2 2 0 0 1 2-2h2.76a2 2 0 0 0 1.79-1.11L12 2h0a3.13 3.13 0 0 1 3 3.88Z"
                ></path>
              </svg>
            </button>
            <button
              v-if="message.role === 'assistant'"
              class="toolbar-icon"
              :class="{ active: feedbackState.get(message.id) === 'down' }"
              @click.stop="feedbackMessage(message, 'down')"
              title="不太好"
            >
              <svg
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <path d="M17 14V2"></path>
                <path
                  d="M9 18.12 10 14H4.17a2 2 0 0 1-1.92-2.56l2.33-8A2 2 0 0 1 6.5 2H20a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2h-2.76a2 2 0 0 0-1.79 1.11L12 22h0a3.13 3.13 0 0 1-3-3.88Z"
                ></path>
              </svg>
            </button>
            <button
              v-if="message.role === 'assistant'"
              class="toolbar-icon"
              :class="{ active: isSpeaking(message.id) }"
              @click.stop="toggleSpeak(message)"
              title="朗读"
            >
              <svg
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon>
                <path d="M15.54 8.46a5 5 0 0 1 0 7.07"></path>
                <path d="M19.07 4.93a10 10 0 0 1 0 14.14"></path>
              </svg>
            </button>
            <button
              v-if="message.role === 'assistant'"
              class="toolbar-icon"
              @click.stop="regenerateMessage(message)"
              title="重新生成"
            >
              <svg
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <polyline points="23 4 23 10 17 10"></polyline>
                <polyline points="1 20 1 14 7 14"></polyline>
                <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10"></path>
                <path d="M20.49 15a9 9 0 0 1-14.85 3.36L1 14"></path>
              </svg>
            </button>
            <button
              class="toolbar-icon"
              @click.stop="moreActions(message)"
              title="更多"
            >
              <svg
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <circle cx="5" cy="12" r="1"></circle>
                <circle cx="12" cy="12" r="1"></circle>
                <circle cx="19" cy="12" r="1"></circle>
              </svg>
            </button>
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
        width="24"
        height="24"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2.5"
        stroke-linecap="round"
        stroke-linejoin="round"
      >
        <line x1="12" y1="5" x2="12" y2="19"></line>
        <polyline points="6 13 12 19 18 13"></polyline>
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
            :class="{
              active: isVoiceMode && buttonMode === 'voice-mode',
              'send-mode': buttonMode === 'send',
              'stop-mode': buttonMode === 'stop',
            }"
            @click="handleMainButton"
            :title="
              buttonMode === 'send'
                ? '发送消息'
                : buttonMode === 'stop'
                ? '停止生成'
                : '语音模式'
            "
          >
            <!-- 发送图标 (向上箭头) -->
            <svg
              v-if="buttonMode === 'send'"
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="#000"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <line x1="12" y1="5" x2="12" y2="19" />
              <polyline points="6,11 12,5 18,11" />
            </svg>

            <!-- 停止图标 -->
            <svg
              v-else-if="buttonMode === 'stop'"
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="currentColor"
            >
              <rect x="6" y="6" width="12" height="12" rx="2"></rect>
            </svg>

            <!-- 语音模式图标 -->
            <svg
              v-else
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
import { markedHighlight } from "marked-highlight";
import hljs from "highlight.js";

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
const speakingMessageId = ref(null);
const inputContent = ref("");
const shouldScrollToBottom = ref(false); // 标志位：是否需要滚动到底部
const isLoadingSession = ref(true); // 初始就设置为 true，默认隐藏
let currentSpeech = null;

// 判断是否有输入内容
const hasInputContent = computed(() => {
  return inputContent.value.trim().length > 0;
});

// 按钮状态：voice-mode(语音模式) / send(发送) / stop(停止)
const buttonMode = computed(() => {
  if (isTyping.value) return "stop";
  if (hasInputContent.value) return "send";
  return "voice-mode";
});

// 随机选择问候语
const selectRandomGreeting = () => {
  const hour = new Date().getHours();
  let list = [];

  if (hour >= 5 && hour < 11) {
    list = [
      "早上好！新的一天开始了，准备好出发了吗？",
      "早安！今天有什么计划？",
      "一日之计在于晨，加油！",
      "早上好，愿你今天充满活力！",
    ];
  } else if (hour >= 11 && hour < 14) {
    list = [
      "中午好！记得按时吃饭哦。",
      "午休时间，要不要聊聊？",
      "中午好，补充点能量继续前行吧。",
    ];
  } else if (hour >= 14 && hour < 18) {
    list = [
      "下午好！喝杯茶休息一下吧。",
      "下午好，工作学习辛苦了。",
      "午后时光，有什么我可以帮你的？",
    ];
  } else if (hour >= 18 && hour < 23) {
    list = [
      "晚上好！今天过得怎么样？",
      "晚上好，卸下一天的疲惫，聊聊吧。",
      "晚上好，我在听。",
    ];
  } else {
    list = [
      "夜深了，还在忙吗？注意休息哦。",
      "这么晚了，有什么心事吗？",
      "夜深人静，正好思考。我在。",
      "还不睡吗？小乐陪你聊聊。",
    ];
  }

  return list[Math.floor(Math.random() * list.length)];
};

const currentGreeting = ref(selectRandomGreeting());

// 配置 marked 使用代码高亮
marked.use(
  markedHighlight({
    langPrefix: "hljs language-",
    highlight(code, lang) {
      const language = hljs.getLanguage(lang) ? lang : "plaintext";
      return hljs.highlight(code, { language }).value;
    },
  })
);

marked.setOptions({
  breaks: true,
  gfm: true,
  sanitize: false, // 关键：不对 HTML 进行转义
  headerIds: false,
});

const sessionId = computed(() => route.params.sessionId);

watch(
  sessionId,
  async (newId) => {
    if (newId) {
      isLoadingSession.value = true;
      await chatStore.loadSession(newId);
      // 立即设置滚动位置（在渲染前）
      await nextTick();
      await nextTick();
      // 使用 requestAnimationFrame 确保在浏览器绘制前完成
      requestAnimationFrame(() => {
        if (chatContainer.value) {
          chatContainer.value.scrollTop = chatContainer.value.scrollHeight;
        }
        // 立即显示，因为滚动已经在绘制前完成
        requestAnimationFrame(() => {
          isLoadingSession.value = false;
        });
      });
    } else {
      chatStore.clearCurrentSession();
      isLoadingSession.value = false;
    }
  },
  { immediate: true }
);

watch(
  messages,
  () => {
    // 如果正在加载会话，不触发自动滚动（由 loadSession 负责初始定位）
    if (isLoadingSession.value) return;

    nextTick(() => {
      // 只在用户发送消息后或 AI 正在打字时才滚动
      if (shouldScrollToBottom.value || isTyping.value) {
        setTimeout(() => {
          scrollToBottom();
          // AI 打字过程中持续滚动到底部
          if (isTyping.value) {
            shouldScrollToBottom.value = true;
          } else {
            shouldScrollToBottom.value = false;
          }
        }, 50); // 减少延迟，更快响应
      }
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

const editMessage = (message) => {
  // 编辑用户消息：将消息内容填充到输入框
  if (message?.role !== "user") return;
  // 设置 contenteditable div 的内容
  nextTick(() => {
    const editor = messageInput.value;
    if (editor) {
      editor.textContent = message.content || "";
      editor.focus();
      // 将光标移到末尾
      const range = document.createRange();
      const sel = window.getSelection();
      range.selectNodeContents(editor);
      range.collapse(false);
      sel.removeAllRanges();
      sel.addRange(range);
    }
  });
};

const isSpeaking = (messageId) => {
  return speakingMessageId.value === messageId;
};

const toggleSpeak = (message) => {
  if (!message?.content) return;

  // 如果正在朗读当前消息，则停止
  if (isSpeaking(message.id)) {
    stopSpeech();
    return;
  }

  // 停止之前的朗读
  stopSpeech();

  // 开始新的朗读
  try {
    const utterance = new SpeechSynthesisUtterance(message.content);
    utterance.lang = "zh-CN";
    utterance.rate = 1.0;
    utterance.pitch = 1.0;
    utterance.volume = 1.0;

    utterance.onstart = () => {
      speakingMessageId.value = message.id;
    };

    utterance.onend = () => {
      speakingMessageId.value = null;
      currentSpeech = null;
    };

    utterance.onerror = () => {
      speakingMessageId.value = null;
      currentSpeech = null;
    };

    currentSpeech = utterance;
    window.speechSynthesis.speak(utterance);
  } catch (error) {
    console.error("朗读失败:", error);
    speakingMessageId.value = null;
  }
};

const stopSpeech = () => {
  if (currentSpeech) {
    window.speechSynthesis.cancel();
    speakingMessageId.value = null;
    currentSpeech = null;
  }
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

const scrollToTop = () => {
  if (!chatContainer.value) return;
  chatContainer.value.scrollTo({
    top: 0,
    behavior: "smooth",
  });
};

const scrollToBottom = () => {
  if (!chatContainer.value) return;
  const container = chatContainer.value;
  container.scrollTo({
    top: container.scrollHeight,
    behavior: "smooth",
  });
};

const onScroll = () => {
  const el = chatContainer.value;
  if (!el) return;
  // 检查是否接近底部
  const nearBottom = el.scrollHeight - el.scrollTop - el.clientHeight < 140;
  showScrollToBottom.value = !nearBottom;
};

const scrollToBottomSmooth = () => {
  scrollToBottom();
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

    // 提取语言标签
    const codeEl = pre.querySelector("code");
    const cls = codeEl?.className || "";
    const m = cls.match(/language-([a-z0-9+#-]+)/i);
    const lang = m ? m[1].toLowerCase() : "plaintext";

    // 创建头部容器
    const header = document.createElement("div");
    header.className = "code-header";

    // 语言标签
    const label = document.createElement("span");
    label.className = "code-lang";
    label.textContent = lang;
    header.appendChild(label);

    // 复制按钮
    const btn = document.createElement("button");
    btn.className = "copy-btn";
    btn.type = "button";
    btn.innerHTML = `
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
        <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
      </svg>
      <span class="copy-text">复制代码</span>
    `;
    btn.addEventListener("click", async (e) => {
      e.stopPropagation();
      try {
        const code = pre.querySelector("code");
        const text = code ? code.innerText : pre.innerText;
        await navigator.clipboard.writeText(text);
        const textSpan = btn.querySelector(".copy-text");
        if (textSpan) {
          textSpan.textContent = "已复制";
          btn.classList.add("copied");
          setTimeout(() => {
            textSpan.textContent = "复制代码";
            btn.classList.remove("copied");
          }, 1500);
        }
      } catch (_) {}
    });
    header.appendChild(btn);

    // 将header插入pre顶部
    pre.insertBefore(header, pre.firstChild);
  });
};

const handleInput = () => {
  // 更新输入内容状态
  inputContent.value = messageInput.value?.innerText || "";

  // 处理输入，清理空内容以显示占位符
  if (messageInput.value && messageInput.value.innerText.trim() === "") {
    messageInput.value.innerHTML = "";
  }
};

const handleEnter = (e) => {
  if (!e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
};

const sendMessage = async () => {
  const content = messageInput.value?.innerText?.trim();
  if (!content || isTyping.value) return;

  // 立即清空输入框
  messageInput.value.innerText = "";
  messageInput.value.innerHTML = "";
  inputContent.value = "";

  // 立即添加用户消息到界面末尾（保持对话顺序）
  messages.value.push({
    id: `temp-${Date.now()}`,
    role: "user",
    content: content,
    timestamp: new Date().toISOString(),
  });

  // 设置标志位：需要滚动到底部
  shouldScrollToBottom.value = true;

  // 发送到后端
  await chatStore.sendMessage(content, null, router);
};

const stopGeneration = () => {
  console.log("停止 AI 生成");
  chatStore.stopGeneration();
};

const handleMainButton = () => {
  if (buttonMode.value === "send") {
    sendMessage();
  } else if (buttonMode.value === "stop") {
    stopGeneration();
  } else {
    toggleVoiceMode();
  }
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
  // 移除自动滚动，让浏览器保持用户的滚动位置
  currentGreeting.value = selectRandomGreeting();
  nextTick(enhanceRenderedContent);
  if (chatContainer.value) {
    chatContainer.value.addEventListener("click", onChatClick);
    chatContainer.value.addEventListener("scroll", onScroll, { passive: true });
  }
});

onBeforeUnmount(() => {
  // 停止朗读
  stopSpeech();

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
.welcome-message {
  position: absolute;
  top: 35%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  z-index: 10;
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
  max-width: 680px;
  width: 90%;
  box-shadow: none;
  background: var(--bg-secondary);
  border: 1px solid var(--border-medium);
}
.chat-container {
  flex: 1;
  overflow-y: auto;
  padding: 0;
  display: flex;
  justify-content: center;
  background: var(--bg-primary);
  margin-bottom: 100px;
  scroll-behavior: auto; /* 确保初始滚动是瞬间的 */
}
.chat-inner {
  width: 100%;
  max-width: 680px;
  padding: 16px 20px;
  position: relative;
}
.message {
  margin-bottom: 16px;
  display: flex;
  flex-direction: column;
  opacity: 0;
  animation: messageSlideIn 0.3s ease-out forwards;
}
@keyframes messageSlideIn {
  from {
    opacity: 0;
    transform: translateY(6px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
.message.new-group {
  margin-top: 24px;
}
.message.user {
  align-items: flex-end;
}
.message.assistant {
  align-items: flex-start;
}
.user-bubble {
  background: #2f2f2f;
  color: #ececec;
  border-radius: 16px;
  padding: 11px 15px;
  display: inline-block;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.08);
  font-size: 16px;
  max-width: 68%;
  word-wrap: break-word;
  word-break: break-word;
  overflow-wrap: break-word;
  hyphens: auto;
}
.user-bubble :deep(p) {
  margin: 0 0 0.5em 0;
  line-height: 1.6;
  color: #ececec;
}
.user-bubble :deep(p:last-child) {
  margin-bottom: 0;
}
.message.assistant .md-content {
  font-size: 16px;
  max-width: 100%;
  word-wrap: break-word;
  word-break: break-word;
  overflow-wrap: break-word;
}
.message.assistant .md-content :deep(p) {
  margin: 0 0 0.6em 0;
  line-height: 1.6;
  color: var(--text-primary);
}
.message.assistant .md-content :deep(p:last-child) {
  margin-bottom: 0;
}
.message-content :deep(p:last-child) {
  margin-bottom: 0;
}
.message-content :deep(ul),
.message-content :deep(ol),
.md-content :deep(ul),
.md-content :deep(ol) {
  margin: 0.8em 0;
  padding-left: 2em;
  list-style-position: outside;
}
.message-content :deep(li),
.md-content :deep(li) {
  margin: 0.3em 0;
  line-height: 1.6;
  padding-left: 0.3em;
}
.md-content :deep(ul) {
  list-style-type: disc;
}
.md-content :deep(ol) {
  list-style-type: decimal;
}
.md-content :deep(ul ul) {
  list-style-type: circle;
}
.md-content :deep(ul ul ul) {
  list-style-type: square;
}
.message-content :deep(code),
.md-content :deep(code) {
  background: rgba(175, 184, 193, 0.2);
  padding: 0.2em 0.5em;
  border-radius: 4px;
  font-size: 0.9em;
  font-family: ui-monospace, "SF Mono", Monaco, "Cascadia Code", monospace;
  color: var(--text-primary);
  border: 1px solid rgba(175, 184, 193, 0.25);
  font-weight: 500;
}
.message-content :deep(pre code),
.md-content :deep(pre code) {
  border: none;
  font-weight: 400;
}
.message-content :deep(pre),
.md-content :deep(pre) {
  background: #0d1117;
  padding: 0;
  border-radius: 10px;
  overflow: hidden;
  margin: 1em 0;
  position: relative;
  border: 1px solid rgba(255, 255, 255, 0.12);
  max-width: 100%;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
}
.message-content :deep(pre code),
.md-content :deep(pre code) {
  background: none;
  padding: 16px 20px;
  color: #e6edf3;
  font-family: ui-monospace, "SF Mono", Monaco, "Cascadia Code", "Roboto Mono",
    Menlo, Consolas, monospace;
  font-size: 14px;
  line-height: 1.75;
  display: block;
  white-space: pre;
  overflow-x: auto;
  font-weight: 400;
  letter-spacing: 0.02em;
  tab-size: 2;
}
[data-theme="light"] .message-content :deep(pre) {
  background: #f6f8fa;
  border: 1px solid #e1e4e8;
}
[data-theme="light"] .message-content :deep(pre code) {
  color: #24292e;
}
.message-image {
  max-width: 320px;
  max-height: 180px;
  margin: 12px 0 0 0;
  border-radius: 6px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
  cursor: pointer;
}
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

/* 代码块头部 */
.md-content :deep(.code-header),
.message-content :deep(.code-header) {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(
    180deg,
    rgba(0, 0, 0, 0.4) 0%,
    rgba(0, 0, 0, 0.3) 100%
  );
  border-bottom: 1px solid rgba(255, 255, 255, 0.12);
  padding: 10px 20px;
  backdrop-filter: blur(10px);
  position: relative;
  z-index: 1;
}

.md-content :deep(.code-lang),
.message-content :deep(.code-lang) {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.85);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  padding: 3px 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
}

.md-content :deep(.copy-btn),
.message-content :deep(.copy-btn) {
  border: 1px solid rgba(255, 255, 255, 0.15);
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.75);
  font-size: 12px;
  padding: 6px 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  font-weight: 500;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  display: flex;
  align-items: center;
  gap: 6px;
  user-select: none;
}

.md-content :deep(.copy-btn svg),
.message-content :deep(.copy-btn svg) {
  width: 14px;
  height: 14px;
  opacity: 0.85;
  transition: transform 0.2s ease;
}

.md-content :deep(.copy-btn:hover),
.message-content :deep(.copy-btn:hover) {
  background: rgba(255, 255, 255, 0.18);
  border-color: rgba(255, 255, 255, 0.25);
  color: rgba(255, 255, 255, 0.95);
  transform: translateY(-1px);
}

.md-content :deep(.copy-btn:hover svg),
.message-content :deep(.copy-btn:hover svg) {
  transform: scale(1.1);
}

.md-content :deep(.copy-btn.copied),
.message-content :deep(.copy-btn.copied) {
  background: rgba(46, 160, 67, 0.25);
  border-color: rgba(46, 160, 67, 0.4);
  color: #3fb950;
}

.md-content :deep(.copy-btn.copied svg),
.message-content :deep(.copy-btn.copied svg) {
  opacity: 1;
  transform: scale(1.15);
}

/* 代码滚动条优化 */
.md-content :deep(pre code)::-webkit-scrollbar {
  height: 8px;
}

.md-content :deep(pre code)::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 4px;
}

.md-content :deep(pre code)::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 4px;
}

.md-content :deep(pre code)::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.3);
}
.message-toolbar {
  display: flex;
  gap: 2px;
  margin-top: 4px;
  transition: opacity 0.2s;
}
.message.assistant .message-toolbar {
  opacity: 1;
}
.message.user .message-toolbar {
  opacity: 0;
  justify-content: flex-end;
}
.message.user:hover .message-toolbar {
  opacity: 1;
}
.toolbar-icon {
  background: none;
  border: none;
  padding: 5px;
  cursor: pointer;
  color: var(--text-tertiary);
  border-radius: 5px;
  transition: all 0.15s;
  width: 26px;
  height: 26px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.toolbar-icon svg {
  width: 15px;
  height: 15px;
}
.toolbar-icon:hover {
  background: var(--bg-hover);
  color: var(--text-secondary);
}
.toolbar-icon.active {
  background: var(--bg-active);
  color: var(--text-primary);
}
.message.user .toolbar-icon {
  color: rgba(255, 255, 255, 0.5);
}
.message.user .toolbar-icon:hover {
  background: rgba(255, 255, 255, 0.15);
  color: rgba(255, 255, 255, 0.9);
}
.message.user .toolbar-icon.active {
  background: rgba(255, 255, 255, 0.2);
  color: #fff;
}
.input-container {
  padding: 12px 16px 16px;
  border-top: none;
  background: transparent;
  flex-shrink: 0;
}
.input-wrapper {
  max-width: 680px;
  margin: 0 auto;
  display: flex;
  gap: 8px;
  align-items: center;
  background: var(--bg-secondary);
  border: 1px solid var(--border-light);
  border-radius: 22px;
  padding: 5px 10px;
  transition: all 0.2s ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
  min-height: 50px;
}
.input-wrapper:focus-within {
  border-color: var(--text-tertiary);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}
.input-controls {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
}
.message-editor {
  flex: 1;
  max-height: 200px;
  overflow-y: auto;
  outline: none;
  padding: 9px 10px;
  color: var(--text-primary);
  font-size: 15px;
  line-height: 1.5;
  min-height: 22px;
  border: none;
  background: transparent;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}
.message-editor:empty:before {
  content: attr(data-placeholder);
  color: var(--text-tertiary);
  font-size: 15px;
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
  transition: all 0.15s ease;
  color: var(--text-secondary);
  flex-shrink: 0;
}
.icon-btn svg {
  width: 18px;
  height: 18px;
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
.icon-btn.recording {
  background: var(--error);
  color: var(--text-inverse);
  animation: pulse 1.5s ease-in-out infinite;
}
.voice-mode-btn {
  width: 36px;
  height: 36px;
  border-radius: 50%;
}

.voice-mode-btn svg {
  width: 28px;
  height: 28px;
}

.voice-mode-btn.send-mode {
  background: #ffffff;
  color: var(--text-primary);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.25);
  border: 1px solid var(--border-medium);
}
.voice-mode-btn.send-mode:hover {
  background: #ffffff;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.28);
}

/* 停止模式样式 */
.voice-mode-btn.stop-mode {
  background: var(--error);
  color: #fff;
  box-shadow: 0 2px 8px rgba(255, 0, 0, 0.35);
}
.voice-mode-btn.stop-mode:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 14px rgba(255, 0, 0, 0.45);
}

/* 思考与打字效果 */
.thinking-wrapper {
  display: flex;
  align-items: center;
  min-height: 24px;
  padding: 2px 4px;
}
.thinking-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #fff;
  box-shadow: 0 0 8px rgba(255, 255, 255, 0.6);
  animation: thinkingPulse 1s ease-in-out infinite;
}
@keyframes thinkingPulse {
  0% {
    transform: scale(0.7);
    opacity: 0.5;
  }
  50% {
    transform: scale(1.6);
    opacity: 1;
  }
  100% {
    transform: scale(0.7);
    opacity: 0.5;
  }
}
.md-content.typing:after {
  content: "";
  display: inline-block;
  width: 6px;
  height: 16px;
  background: var(--text-primary);
  margin-left: 2px;
  animation: caretBlink 0.9s steps(2, start) infinite;
  vertical-align: bottom;
}
@keyframes caretBlink {
  0%,
  49% {
    opacity: 1;
  }
  50%,
  100% {
    opacity: 0;
  }
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
.scroll-to-bottom {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  bottom: 120px;
  width: 48px;
  height: 48px;
  border-radius: 50%;
  border: 1px solid var(--border-medium);
  background: var(--bg-secondary);
  color: var(--text-primary);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 100;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  animation: fadeIn 0.3s ease;
}
.scroll-to-bottom svg {
  opacity: 1;
}
.scroll-to-bottom:hover {
  background: var(--brand-primary);
  color: white;
  transform: translateX(-50%) translateY(-2px);
  box-shadow: 0 6px 24px rgba(0, 0, 0, 0.25);
  border-color: var(--brand-primary);
}
.scroll-to-bottom:active {
  transform: translateX(-50%) translateY(0);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateX(-50%) translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateX(-50%) translateY(0);
  }
}
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
@media (max-width: 900px) {
  .input-wrapper {
    max-width: 98vw;
  }
}
</style>
