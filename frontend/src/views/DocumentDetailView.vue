<template>
  <div class="doc-detail-view">
    <!-- 顶部导航 -->
    <div class="nav-header">
      <button class="btn-back" @click="router.back()">← 返回列表</button>
      <div class="actions">
        <button class="btn-delete" @click="handleDelete" :disabled="deleting">
          {{ deleting ? "删除中..." : "🗑️ 删除文档" }}
        </button>
      </div>
    </div>

    <div class="card">
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>加载文档详情...</p>
      </div>

      <div v-else-if="document" class="doc-content">
        <div class="doc-header">
          <div class="doc-icon">{{ getFileIcon(document.file_type) }}</div>
          <div class="doc-title-area">
            <h4>{{ document.original_filename || document.filename }}</h4>
            <div class="doc-meta">
              <span>{{ formatTime(document.created_at) }}</span>
              <span class="separator">•</span>
              <span>{{ formatSize(document.file_size) }}</span>
              <span class="separator">•</span>
              <span class="status-badge" :class="document.status">
                {{ getStatusText(document.status) }}
              </span>
            </div>
          </div>
        </div>

        <div class="divider"></div>

        <!-- 摘要部分 -->
        <div v-if="document.summary" class="section summary-section">
          <div class="section-header">
            <span class="section-icon">📝</span>
            <h5>智能摘要</h5>
          </div>
          <div
            class="content summary-content markdown-body"
            v-html="renderMarkdown(document.summary)"
          ></div>
        </div>

        <!-- 关键点部分 -->
        <div
          v-if="document.key_points && document.key_points.length"
          class="section key-points-section"
        >
          <div class="section-header">
            <span class="section-icon">💡</span>
            <h5>关键要点</h5>
          </div>
          <ul class="key-points">
            <li v-for="(point, index) in document.key_points" :key="index">
              {{ point }}
            </li>
          </ul>
        </div>

        <!-- PDF 预览部分 -->
        <div v-if="isPdf" class="section preview-section">
          <div
            class="section-header"
            @click="showPreview = !showPreview"
            style="cursor: pointer"
          >
            <div class="header-left">
              <span class="section-icon">👁️</span>
              <h5>文件预览</h5>
            </div>
            <span class="toggle-icon">{{ showPreview ? "▼" : "▶" }}</span>
          </div>
          <div v-show="showPreview" class="content preview-content">
            <embed
              :src="fileUrl"
              type="application/pdf"
              width="100%"
              height="600px"
              class="pdf-viewer"
            />
          </div>
        </div>

        <!-- 原始内容部分 -->
        <div v-if="document.content" class="section original-section">
          <div
            class="section-header"
            @click="showOriginal = !showOriginal"
            style="cursor: pointer"
          >
            <div class="header-left">
              <span class="section-icon">📄</span>
              <h5>原始内容</h5>
            </div>
            <span class="toggle-icon">{{ showOriginal ? "▼" : "▶" }}</span>
          </div>
          <div
            v-show="showOriginal"
            class="content text-content markdown-body"
            v-html="renderMarkdown(document.content)"
          ></div>
        </div>
      </div>

      <div v-else class="error-state">
        <p>未找到文档信息</p>
        <button @click="router.back()">返回列表</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import { marked } from "marked";
import api from "@/services/api";

const route = useRoute();
const router = useRouter();
const document = ref(null);
const loading = ref(false);
const deleting = ref(false);
const showOriginal = ref(false);
const showPreview = ref(true);

const fileUrl = computed(() => {
  if (!document.value) return "";
  return `/uploads/${document.value.filename}`;
});

const isPdf = computed(() => {
  return document.value?.file_type === "pdf";
});

const renderMarkdown = (text) => {
  if (!text) return "";
  return marked.parse(text);
};

const loadDocument = async () => {
  try {
    loading.value = true;
    const data = await api.getDocument(route.params.id);
    if (data.success && data.document) {
      document.value = data.document;
    }
  } catch (error) {
    console.error("Failed to load document:", error);
  } finally {
    loading.value = false;
  }
};

const handleDelete = async () => {
  if (!confirm("确定要删除这个文档吗？此操作无法撤销。")) return;

  try {
    deleting.value = true;
    await api.deleteDocument(document.value.id);
    router.push("/documents");
  } catch (error) {
    console.error("Failed to delete document:", error);
    alert("删除失败，请重试");
  } finally {
    deleting.value = false;
  }
};

const formatTime = (time) => {
  return new Date(time).toLocaleString("zh-CN", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
};

const formatSize = (bytes) => {
  if (bytes === 0) return "0 B";
  const k = 1024;
  const sizes = ["B", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + " " + sizes[i];
};

const getFileIcon = (type) => {
  const icons = {
    pdf: "📕",
    docx: "📝",
    doc: "📝",
    txt: "📄",
    md: "📉",
  };
  return icons[type?.toLowerCase()] || "📄";
};

const getStatusText = (status) => {
  const map = {
    pending: "等待中",
    processing: "处理中",
    completed: "已完成",
    failed: "失败",
  };
  return map[status] || status;
};

onMounted(() => {
  loadDocument();
});
</script>

<style scoped>
.doc-detail-view {
  padding: var(--space-xl);
  max-width: 1000px;
  margin: 0 auto;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica,
    Arial, sans-serif;
}

.nav-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-xl);
}

.btn-back {
  background: var(--bg-primary);
  border: 1px solid var(--border-medium);
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border-radius: var(--radius-md);
  transition: all var(--duration-fast);
  box-shadow: var(--shadow-sm);
}

.btn-back:hover {
  color: var(--text-primary);
  background: var(--bg-secondary);
  transform: translateX(-2px);
}

.btn-delete {
  background: rgba(239, 68, 68, 0.1);
  color: var(--error);
  border: 1px solid transparent;
  padding: 8px 16px;
  border-radius: var(--radius-md);
  cursor: pointer;
  font-size: 14px;
  transition: all var(--duration-fast);
  display: flex;
  align-items: center;
  gap: 6px;
}

.btn-delete:hover:not(:disabled) {
  background: rgba(239, 68, 68, 0.2);
  transform: translateY(-1px);
}

.btn-delete:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.card {
  background: var(--card-bg);
  border-radius: var(--radius-xl);
  padding: var(--space-3xl);
  box-shadow: var(--shadow-lg);
  border: 1px solid var(--card-border);
}

.doc-header {
  display: flex;
  gap: var(--space-xl);
  align-items: flex-start;
  margin-bottom: var(--space-2xl);
}

.doc-icon {
  font-size: 48px;
  background: var(--bg-secondary);
  width: 88px;
  height: 88px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-light);
}

.doc-title-area {
  flex: 1;
}

.doc-title-area h4 {
  font-size: 28px;
  margin: 0 0 12px 0;
  color: var(--text-primary);
  line-height: 1.3;
  font-weight: 700;
}

.doc-meta {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  color: var(--text-secondary);
  font-size: 14px;
}

.separator {
  color: var(--border-medium);
}

.divider {
  height: 1px;
  background: var(--border-light);
  margin: var(--space-2xl) 0;
}

.section {
  margin-bottom: 40px;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-lg);
  padding-bottom: var(--space-md);
  border-bottom: 1px solid var(--border-light);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.section-icon {
  font-size: 22px;
}

.section h5 {
  margin: 0;
  color: var(--text-primary);
  font-size: 18px;
  font-weight: 600;
  letter-spacing: -0.01em;
}

.toggle-icon {
  color: var(--text-tertiary);
  font-size: 12px;
  transition: transform var(--duration-fast);
}

.summary-content {
  background: var(--bg-secondary);
  padding: var(--space-xl);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-light);
  color: var(--text-secondary);
  line-height: 1.8;
}

.key-points {
  padding-left: 0;
  list-style: none;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: var(--space-lg);
}

.key-points li {
  background: var(--card-bg);
  padding: 16px 20px;
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-light);
  line-height: 1.6;
  color: var(--text-secondary);
  display: flex;
  align-items: flex-start;
  gap: 12px;
  transition: all var(--duration-fast);
  box-shadow: var(--shadow-sm);
}

.key-points li:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
  border-color: var(--border-medium);
}

.key-points li::before {
  content: "💡";
  font-size: 16px;
  flex-shrink: 0;
  margin-top: 2px;
}

.text-content {
  background: var(--bg-secondary);
  padding: var(--space-xl);
  border-radius: var(--radius-lg);
  font-size: 14px;
  max-height: 600px;
  overflow-y: auto;
  border: 1px solid var(--border-light);
  color: var(--text-secondary);
}

/* Markdown Styles Refined */
.markdown-body :deep(p) {
  margin-bottom: 1.2em;
}

.markdown-body :deep(h1),
.markdown-body :deep(h2),
.markdown-body :deep(h3) {
  color: var(--text-primary);
  margin-top: 1.5em;
  margin-bottom: 0.8em;
}

.markdown-body :deep(strong) {
  color: var(--text-primary);
  font-weight: 600;
}

.markdown-body :deep(code) {
  background: var(--bg-tertiary);
  color: var(--brand-primary);
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.9em;
}

.status-badge {
  font-size: 12px;
  padding: 4px 10px;
  border-radius: var(--radius-full);
  background: var(--bg-tertiary);
  color: var(--text-secondary);
  font-weight: 500;
}

.status-badge.completed {
  background: rgba(16, 163, 127, 0.1);
  color: var(--success);
}

.status-badge.processing {
  background: rgba(14, 165, 233, 0.1);
  color: var(--info);
}

.status-badge.failed {
  background: rgba(239, 68, 68, 0.1);
  color: var(--error);
}

.pdf-viewer {
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-medium);
  background: white; /* PDF viewer usually needs white background */
  box-shadow: var(--shadow-md);
}

.loading-state {
  text-align: center;
  padding: 80px;
  color: var(--text-tertiary);
}

.spinner {
  width: 48px;
  height: 48px;
  border: 4px solid var(--bg-secondary);
  border-top-color: var(--brand-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 24px;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
