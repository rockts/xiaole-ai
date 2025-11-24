<template>
  <teleport to="body">
    <div class="share-overlay" @click="emit('close')">
      <div class="share-dialog" @click.stop>
        <div class="share-header">
          <h3 class="share-title">{{ title }}</h3>
          <button
            class="share-close-btn"
            aria-label="关闭"
            @click="emit('close')"
          >
            <svg
              width="36"
              height="36"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="3"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>
        <div class="divider"></div>

        <div class="preview-wrap">
          <!-- 若已生成缩略图则直接展示 -->
          <img
            v-if="previewUrl"
            class="preview-image"
            :src="previewUrl"
            alt="分享预览图"
          />

          <!-- 备用 HTML 预览：用于截图源或回退显示 -->
          <div v-show="!previewUrl" class="preview-card" ref="previewCardRef">
            <div class="preview-watermark">XiaoLe AI</div>

            <!-- 摘要式布局 -->
            <div class="summary-content">
              <div
                v-for="(msg, index) in previewMessages"
                :key="index"
                class="message-row"
                :class="msg.role"
              >
                <!-- 用户消息 -->
                <div v-if="msg.role === 'user'" class="user-message">
                  <div class="message-bubble">
                    <div
                      v-if="msg.content"
                      class="message-text"
                      v-html="renderMarkdown(msg.content)"
                    ></div>
                    <div v-if="msg.image" class="message-image-wrapper">
                      <img
                        :src="msg.image"
                        class="message-image"
                        crossorigin="anonymous"
                      />
                    </div>
                  </div>
                </div>

                <!-- AI 消息 -->
                <div v-else class="ai-message">
                  <div class="ai-avatar">
                    <svg
                      width="20"
                      height="20"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="2"
                    >
                      <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                      <polyline points="22 4 12 14.01 9 11.01"></polyline>
                    </svg>
                  </div>
                  <div class="message-content">
                    <div class="ai-name">XiaoLe AI</div>
                    <div
                      v-if="msg.content"
                      class="message-text"
                      v-html="renderMarkdown(msg.content)"
                    ></div>
                    <div v-if="msg.image" class="message-image-wrapper">
                      <img
                        :src="msg.image"
                        class="message-image"
                        crossorigin="anonymous"
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 底部渐变遮罩 -->
            <div class="fade-overlay"></div>
          </div>
        </div>

        <div class="share-actions">
          <button class="action-btn" @click="copyLink">
            <div class="icon-circle">
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
                  d="M10 13a5 5 0 0 0 7.07 0l1.41-1.41a5 5 0 1 0-7.07-7.07L10 5"
                />
                <path
                  d="M14 11a5 5 0 0 0-7.07 0L5.5 12.41a5 5 0 1 0 7.07 7.07L14 19"
                />
              </svg>
            </div>
            <span class="action-label">复制链接</span>
          </button>

          <button class="action-btn" title="Post on X" @click="shareToX">
            <div class="icon-circle">
              <svg
                width="18"
                height="18"
                viewBox="0 0 24 24"
                fill="currentColor"
              >
                <path
                  d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"
                />
              </svg>
            </div>
            <span class="action-label">X</span>
          </button>

          <button class="action-btn" title="LinkedIn" @click="shareToLinkedIn">
            <div class="icon-circle">
              <svg
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="currentColor"
              >
                <path
                  d="M4.98 3.5C4.98 4.88 3.86 6 2.5 6S0 4.88 0 3.5 1.12 1 2.5 1s2.48 1.12 2.48 2.5zM0 8h5v16H0V8zm7.5 0H12v2.2h.06c.62-1.17 2.14-2.4 4.4-2.4 4.7 0 5.56 3.09 5.56 7.11V24h-5V16.5c0-1.79-.03-4.09-2.49-4.09-2.49 0-2.87 1.94-2.87 3.96V24h-5V8z"
                />
              </svg>
            </div>
            <span class="action-label">LinkedIn</span>
          </button>

          <button class="action-btn" title="Reddit" @click="shareToReddit">
            <div class="icon-circle">
              <svg
                width="22"
                height="22"
                viewBox="0 0 24 24"
                fill="currentColor"
              >
                <path
                  d="M22 12c0 4.42-4.48 8-10 8S2 16.42 2 12s4.48-8 10-8 10 3.58 10 8zm-15 1.5a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3zm10 0a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3zM7.5 14.5c.9 1.17 2.7 2 4.5 2s3.6-.83 4.5-2"
                />
              </svg>
            </div>
            <span class="action-label">Reddit</span>
          </button>
        </div>
      </div>
    </div>
  </teleport>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { marked } from "marked";

const emit = defineEmits(["close"]);
const props = defineProps({
  title: { type: String, default: "分享" },
  shareUrl: { type: String, required: true },
});

const previewUrl = ref("");
const previewCardRef = ref(null);
const previewMessages = ref([]);
const summaryText = ref("");
const answerText = ref("");

const renderMarkdown = (text) => {
  if (!text) return "";
  return marked.parse(text);
};

const copyLink = async () => {
  try {
    if (navigator.clipboard?.writeText) {
      await navigator.clipboard.writeText(props.shareUrl);
      alert("已复制分享链接");
    } else {
      const ta = document.createElement("textarea");
      ta.value = props.shareUrl;
      ta.style.position = "fixed";
      ta.style.opacity = "0";
      document.body.appendChild(ta);
      ta.select();
      document.execCommand("copy");
      document.body.removeChild(ta);
      alert("已复制分享链接");
    }
  } catch (e) {
    console.error("复制失败", e);
    alert("复制失败，请重试");
  }
};

const open = (url) => window.open(url, "_blank", "noopener,noreferrer");
const shareToX = () => {
  const u = encodeURIComponent(props.shareUrl);
  const t = encodeURIComponent(props.title);
  open(`https://twitter.com/intent/tweet?url=${u}&text=${t}`);
};
const shareToLinkedIn = () => {
  const u = encodeURIComponent(props.shareUrl);
  open(`https://www.linkedin.com/sharing/share-offsite/?url=${u}`);
};
const shareToReddit = () => {
  const u = encodeURIComponent(props.shareUrl);
  const t = encodeURIComponent(props.title);
  open(`https://www.reddit.com/submit?url=${u}&title=${t}`);
};

// 优先尝试服务端生成的预览图（如果后端有该能力）
const tryServerPreview = async (id) => {
  const url = `/api/share/preview/${id}.png`;
  try {
    await new Promise((resolve, reject) => {
      const img = new Image();
      img.onload = () => resolve(true);
      img.onerror = reject;
      img.src = url;
    });
    previewUrl.value = url;
  } catch (_) {
    // ignore
  }
};

// 无服务端时，使用前端截图
const htmlToImagePreview = async () => {
  try {
    const node = previewCardRef.value;
    if (!node) {
      console.warn("previewCardRef 未找到");
      return;
    }

    // 等待 DOM 和样式完全加载
    await new Promise((resolve) => setTimeout(resolve, 300));

    const mod = await import("html-to-image");
    const toPng = mod.toPng || mod.default?.toPng;
    if (!toPng) {
      console.warn("html-to-image toPng 方法未找到");
      return;
    }

    console.log("开始生成预览图...");
    const dataUrl = await toPng(node, {
      cacheBust: true,
      pixelRatio: 2,
      backgroundColor: "#1a1a1a",
    });
    previewUrl.value = dataUrl;
    console.log("预览图生成成功");
  } catch (e) {
    console.error("生成缩略图失败", e);
  }
};

onMounted(async () => {
  console.log("ShareDialog mounted, shareUrl:", props.shareUrl);
  try {
    const id = props.shareUrl.split("/").filter(Boolean).pop();
    console.log("提取的会话ID:", id);

    // 拉取会话最近消息以构建预览
    const resp = await fetch(`/session/${id}`);
    console.log("会话数据响应状态:", resp.status);

    if (resp.ok) {
      const data = await resp.json();
      const list = (data.messages || data.history || []).slice(-5);
      console.log("获取到的消息数量:", list.length);

      // 提取摘要内容 (取第一条用户消息和第一条AI回复)
      const userMsg = list.find(
        (m) => m.role === "user" || m.author === "user"
      );
      const aiMsg = list.find(
        (m) =>
          m.role === "assistant" || m.author === "assistant" || m.role === "ai"
      );

      summaryText.value = userMsg
        ? (userMsg.content || "").toString().slice(0, 150)
        : "对话内容...";
      answerText.value = aiMsg
        ? (aiMsg.content || "").toString().slice(0, 300)
        : "暂无回答...";

      console.log("原始消息数据:", list);
      previewMessages.value = list.map((m) => {
        let imagePath = null;
        if (m.image_path) {
          // 处理可能的路径重复问题
          imagePath = m.image_path.startsWith("uploads/")
            ? `/${m.image_path}`
            : `/uploads/${m.image_path}`;
        }
        const msg = {
          role: m.role || m.author || "assistant",
          content: (m.content || "").toString().slice(0, 120),
          image: imagePath,
        };
        console.log("处理后的消息:", msg);
        return msg;
      });

      console.log("尝试服务端预览图...");
      await tryServerPreview(id);

      if (!previewUrl.value) {
        console.log("服务端预览图不可用，使用前端截图");
        await htmlToImagePreview();
      } else {
        console.log("使用服务端预览图");
      }
    } else {
      console.log("会话数据获取失败，直接使用前端截图");
      await htmlToImagePreview();
    }
  } catch (err) {
    console.error("onMounted 错误:", err);
    await htmlToImagePreview();
  }
});
</script>

<style scoped>
.share-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
  animation: fadeIn 0.15s ease-out;
}
.share-dialog {
  position: relative;
  background: var(--bg-primary);
  border-radius: 16px;
  box-shadow: 0 16px 60px rgba(0, 0, 0, 0.35);
  width: min(860px, 92vw);
  max-height: 85vh;
  display: flex;
  flex-direction: column;
  padding: 0;
  overflow: hidden;
}
.share-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-light);
  background: var(--bg-primary);
  flex-shrink: 0;
  z-index: 10;
}
.share-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}
.share-close-btn {
  /* Reset positioning to flow naturally in flex header */
  position: static;
  width: 56px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;

  background: transparent;
  border: none;
  /* Use text-primary for high contrast against bg-primary */
  color: var(--text-primary);
  opacity: 1;
}

.share-close-btn:hover {
  transform: scale(1.1);
  background: rgba(128, 128, 128, 0.1);
  border-radius: 12px;
}

.share-close-btn svg {
  width: 36px;
  height: 36px;
  stroke: currentColor;
  stroke-width: 3;
}

.divider {
  display: none;
}

.preview-wrap {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  justify-content: center;
  background: var(--bg-secondary);
  min-height: 0;
}
/* 美化滚动条 */
.preview-wrap::-webkit-scrollbar {
  width: 6px;
}
.preview-wrap::-webkit-scrollbar-track {
  background: transparent;
}
.preview-wrap::-webkit-scrollbar-thumb {
  background: var(--border-heavy);
  border-radius: 3px;
}

.preview-image {
  width: 100%;
  max-width: 720px;
  border-radius: 14px;
  border: 1px solid var(--border-light);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.18);
  height: auto;
  object-fit: contain;
}
.preview-card {
  position: relative;
  width: 100%;
  max-width: 720px;
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.06);
  background: #1e1e1e;
  display: flex;
  flex-direction: column;
  padding: 40px 32px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.35);
  overflow: hidden;
}

.preview-watermark {
  position: absolute;
  bottom: 20px;
  right: 24px;
  color: rgba(255, 255, 255, 0.2);
  font-weight: 600;
  font-size: 13px;
  letter-spacing: 0.5px;
  pointer-events: none;
  z-index: 10;
}

.summary-content {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.message-row {
  display: flex;
  width: 100%;
}

.message-row.user {
  justify-content: flex-end;
}

.user-message .message-bubble {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px 12px 0 12px;
  padding: 12px 16px;
  max-width: 85%;
  color: #fff;
}

.ai-message {
  display: flex;
  gap: 12px;
  max-width: 90%;
}

.ai-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #10a37f;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
  margin-top: 2px;
}

.message-content {
  flex: 1;
}

.ai-name {
  font-size: 12px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.5);
  margin-bottom: 4px;
  text-transform: uppercase;
}

.message-text {
  font-size: 15px;
  line-height: 1.6;
  color: rgba(255, 255, 255, 0.9);
}

.message-text :deep(p) {
  margin: 0 0 0.5em 0;
}
.message-text :deep(p:last-child) {
  margin: 0;
}
.message-text :deep(strong) {
  font-weight: 700;
  color: #fff;
}

.message-image-wrapper {
  margin-top: 8px;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.message-image {
  display: block;
  max-width: 100%;
  height: auto;
}

.fade-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 120px;
  background: linear-gradient(
    to bottom,
    rgba(30, 30, 30, 0),
    rgba(30, 30, 30, 1)
  );
  pointer-events: none;
  z-index: 5;
}

.share-actions {
  display: flex;
  gap: 24px;
  flex-wrap: wrap;
  justify-content: center;
  padding: 20px;
  background: var(--bg-primary);
  border-top: 1px solid var(--border-light);
  margin-top: 0;
  flex-shrink: 0;
}
.action-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 0;
  border: none;
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 12px;
  transition: all 0.2s ease;
}
.action-btn:hover {
  color: var(--text-primary);
  transform: translateY(-2px);
}
.icon-circle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: var(--bg-secondary);
  border: 1px solid var(--border-light);
  color: var(--text-primary);
  transition: all 0.2s ease;
}
.action-btn:hover .icon-circle {
  background: var(--bg-hover);
  border-color: var(--text-secondary);
}
.action-label {
  font-weight: 500;
}
.icon {
  display: none; /* Deprecated */
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}
</style>
