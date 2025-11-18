<template>
  <teleport to="body">
    <div class="share-overlay" @click="emit('close')">
      <div class="share-dialog" @click.stop>
        <div class="share-header">
          <h3 class="share-title">{{ title }}</h3>
          <button class="close-btn" aria-label="关闭" @click="emit('close')">
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
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>
        <div class="divider"></div>

        <div class="preview-wrap">
          <!-- 若已生成缩略图则直接展示 -->
          <img v-if="previewUrl" class="preview-image" :src="previewUrl" alt="分享预览图" />

          <!-- 备用 HTML 预览：用于截图源或回退显示 -->
          <div v-show="!previewUrl" class="preview-card" ref="previewCardRef">
            <div class="preview-watermark">XiaoLe</div>
            <div class="preview-title">{{ title }}</div>
            <div class="preview-list">
              <div v-for="(m, i) in previewMessages" :key="i" class="pmsg" :class="m.role">
                <div class="avatar">{{ m.role === 'user' ? '你' : '小乐' }}</div>
                <div class="text">{{ m.content }}</div>
              </div>
            </div>
          </div>
        </div>

        <div class="share-actions">
          <button class="action-btn" @click="copyLink">
            <span class="icon">
              <svg
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
              >
                <path
                  d="M10 13a5 5 0 0 0 7.07 0l1.41-1.41a5 5 0 1 0-7.07-7.07L10 5"
                />
                <path
                  d="M14 11a5 5 0 0 0-7.07 0L5.5 12.41a5 5 0 1 0 7.07 7.07L14 19"
                />
              </svg>
            </span>
            复制链接
          </button>

          <button class="action-btn" title="Post on X" @click="shareToX">
            <span class="icon">✕</span>
            X
          </button>
          <button class="action-btn" title="LinkedIn" @click="shareToLinkedIn">
            <span class="icon">
              <svg
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="currentColor"
              >
                <path
                  d="M4.98 3.5C4.98 4.88 3.86 6 2.5 6S0 4.88 0 3.5 1.12 1 2.5 1s2.48 1.12 2.48 2.5zM0 8h5v16H0V8zm7.5 0H12v2.2h.06c.62-1.17 2.14-2.4 4.4-2.4 4.7 0 5.56 3.09 5.56 7.11V24h-5V16.5c0-1.79-.03-4.09-2.49-4.09-2.49 0-2.87 1.94-2.87 3.96V24h-5V8z"
                />
              </svg>
            </span>
            LinkedIn
          </button>
          <button class="action-btn" title="Reddit" @click="shareToReddit">
            <span class="icon">
              <svg
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="currentColor"
              >
                <path
                  d="M22 12c0 4.42-4.48 8-10 8S2 16.42 2 12s4.48-8 10-8 10 3.58 10 8zm-15 1.5a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3zm10 0a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3zM7.5 14.5c.9 1.17 2.7 2 4.5 2s3.6-.83 4.5-2"
                />
              </svg>
            </span>
            Reddit
          </button>
        </div>
      </div>
    </div>
  </teleport>
</template>

<script setup>
import { ref, onMounted } from 'vue'
const emit = defineEmits(['close'])
const props = defineProps({
  title: { type: String, default: "分享" },
  shareUrl: { type: String, required: true },
})

const previewUrl = ref('')
const previewCardRef = ref(null)
const previewMessages = ref([])

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
  const url = `/api/share/preview/${id}.png`
  try {
    await new Promise((resolve, reject) => {
      const img = new Image()
      img.onload = () => resolve(true)
      img.onerror = reject
      img.src = url
    })
    previewUrl.value = url
  } catch (_) {
    // ignore
  }
}

// 无服务端时，使用前端截图
const htmlToImagePreview = async () => {
  try {
    const mod = await import('html-to-image')
    const toPng = mod.toPng || mod.default?.toPng
    if (!toPng) return
    const node = previewCardRef.value
    if (!node) return
    const dataUrl = await toPng(node, { cacheBust: true, pixelRatio: 2 })
    previewUrl.value = dataUrl
  } catch (e) {
    console.warn('生成缩略图失败，保留HTML预览', e)
  }
}

onMounted(async () => {
  try {
    const id = props.shareUrl.split('/').filter(Boolean).pop()
    // 拉取会话最近消息以构建预览
    const resp = await fetch(`/session/${id}`)
    if (resp.ok) {
      const data = await resp.json()
      const list = (data.messages || data.history || []).slice(-5)
      previewMessages.value = list.map((m) => ({
        role: m.role || (m.author || 'assistant'),
        content: (m.content || '').toString().slice(0, 80)
      }))
      await tryServerPreview(id)
      if (!previewUrl.value) await htmlToImagePreview()
    } else {
      await htmlToImagePreview()
    }
  } catch (_) {
    await htmlToImagePreview()
  }
})
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
  background: var(--bg-primary);
  border-radius: 16px;
  box-shadow: 0 16px 60px rgba(0, 0, 0, 0.35);
  width: min(860px, 92vw);
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  padding: 16px 16px 20px;
}
.share-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 4px 4px 8px;
}
.share-title {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}
.close-btn {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: transparent;
  border-radius: 8px;
  color: var(--text-secondary);
  cursor: pointer;
}
.close-btn:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}
.divider {
  height: 1px;
  background: var(--border-light);
  opacity: 0.7;
  margin: 4px 0 12px;
}

.preview-wrap {
  padding: 8px 0;
  display: flex;
  justify-content: center;
}
.preview-image{width:100%;max-width:720px;border-radius:14px;border:1px solid var(--border-light);box-shadow:0 10px 30px rgba(0,0,0,.18)}
.preview-card {
  position: relative;
  width: 100%;
  max-width: 720px;
  aspect-ratio: 16/9;
  border-radius: 14px;
  border: 1px solid var(--border-light);
  background: linear-gradient(180deg, rgba(255,255,255,.06), rgba(0,0,0,.1));
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 16px 18px;
  overflow: hidden;
}
[data-theme="light"] .preview-card {
  background: linear-gradient(180deg, rgba(0, 0, 0, 0.03), rgba(0, 0, 0, 0.06));
}
.preview-watermark {
  position: absolute;
  bottom: 14px;
  right: 16px;
  color: var(--text-primary);
  opacity: 0.6;
  font-weight: 700;
}
.preview-title{font-size:16px;font-weight:700;color:var(--text-primary)}
.preview-list{display:flex;flex-direction:column;gap:8px;overflow:hidden}
.pmsg{display:flex;gap:10px}
.pmsg .avatar{font-size:12px;color:var(--text-secondary);width:34px;flex-shrink:0}
.pmsg .text{flex:1;color:var(--text-primary);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}

.share-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  justify-content: center;
  margin-top: 18px;
}
.action-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  border: none;
  border-radius: 999px;
  background: var(--bg-secondary);
  color: var(--text-primary);
  cursor: pointer;
  font-size: 14px;
}
.action-btn:hover {
  background: var(--bg-hover);
}
.icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 18px;
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
