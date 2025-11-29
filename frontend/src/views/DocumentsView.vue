<template>
  <div class="documents-view">
    <div class="header">
      <h3>📚 文档助手</h3>
      <p class="subtitle">上传文档，AI 帮你自动总结摘要和关键点</p>
    </div>

    <div class="main-content">
      <!-- 上传区域 -->
      <div
        class="upload-card"
        :class="{ 'is-dragging': isDragging }"
        @dragover.prevent="isDragging = true"
        @dragleave.prevent="isDragging = false"
        @drop.prevent="handleDrop"
        @click="triggerUpload"
      >
        <input
          ref="fileInput"
          type="file"
          accept=".pdf,.docx,.txt,.md"
          style="display: none"
          @change="handleUpload"
        />
        <div class="upload-content">
          <div class="upload-icon">☁️</div>
          <div class="upload-text">
            <span class="primary-text">点击或拖拽文件到此处上传</span>
            <span class="secondary-text">支持 PDF, Word, TXT, Markdown</span>
          </div>
        </div>
      </div>

      <!-- 文档列表 -->
      <div class="documents-list">
        <div v-if="loading && !documents.length" class="loading-state">
          <div class="spinner"></div>
          <p>加载文档中...</p>
        </div>

        <div v-else-if="documents.length === 0" class="empty-state">
          <div class="empty-icon">📭</div>
          <p>暂无文档，快去上传一个吧</p>
        </div>

        <div v-else class="doc-grid">
          <div
            v-for="doc in documents"
            :key="doc.id"
            class="doc-card"
            @click="router.push(`/documents/${doc.id}`)"
          >
            <div class="doc-icon">{{ getFileIcon(doc.file_type) }}</div>
            <div class="doc-info">
              <div class="doc-header">
                <div
                  class="doc-title"
                  :title="doc.original_filename || doc.filename"
                >
                  {{ doc.original_filename || doc.filename }}
                </div>
                <button class="btn-delete" @click.stop="handleDelete(doc)">
                  🗑️
                </button>
              </div>
              <div class="doc-meta">
                <span class="doc-time">{{ formatTime(doc.created_at) }}</span>
                <span class="doc-size">{{ formatSize(doc.file_size) }}</span>
              </div>
              <div class="doc-status">
                <span class="status-badge" :class="doc.status">
                  {{ getStatusText(doc.status) }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 删除确认弹窗 -->
    <div v-if="showDeleteConfirm" class="modal-overlay" @click="cancelDelete">
      <div class="confirm-dialog" @click.stop>
        <h3 class="confirm-title">删除文档</h3>
        <p class="confirm-message">
          确定要删除 "{{
            documentToDelete?.original_filename || documentToDelete?.filename
          }}" 吗？此操作无法撤销。
        </p>
        <div class="confirm-actions">
          <button class="btn-cancel" @click="cancelDelete">取消</button>
          <button class="btn-confirm-delete" @click="confirmDelete">
            删除
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import api from "@/services/api";

const router = useRouter();
const documents = ref([]);
const loading = ref(false);
const fileInput = ref(null);
const isDragging = ref(false);

// 删除确认弹窗状态
const showDeleteConfirm = ref(false);
const documentToDelete = ref(null);

const loadDocuments = async () => {
  try {
    loading.value = true;
    console.log("📚 开始加载文档...");
    const data = await api.getDocuments();
    console.log("📦 API返回数据:", data);
    console.log("📄 文档数组:", data.documents);
    documents.value = data.documents || [];
    console.log("✅ 文档加载完成，数量:", documents.value.length);
  } catch (error) {
    console.error("Failed to load documents:", error);
  } finally {
    loading.value = false;
  }
};

const triggerUpload = () => {
  fileInput.value?.click();
};

const handleDrop = async (e) => {
  isDragging.value = false;
  const files = e.dataTransfer.files;
  if (files.length > 0) {
    await uploadFile(files[0]);
  }
};

const handleUpload = async (e) => {
  const file = e.target.files?.[0];
  if (file) {
    await uploadFile(file);
  }
};

const uploadFile = async (file) => {
  const formData = new FormData();
  formData.append("file", file);
  // 后端会使用JWT认证的用户ID

  // 乐观更新：先添加一个临时状态
  const tempId = Date.now();
  documents.value.unshift({
    id: tempId,
    original_filename: file.name,
    file_type: file.name.split(".").pop(),
    file_size: file.size,
    created_at: new Date().toISOString(),
    status: "processing",
  });

  try {
    await api.uploadDocument(formData);
    await loadDocuments(); // 重新加载以获取真实数据
  } catch (error) {
    console.error("Failed to upload document:", error);
    // 移除临时项或显示错误
    documents.value = documents.value.filter((d) => d.id !== tempId);
    alert("上传失败，请重试");
  }
};

const handleDelete = (doc) => {
  documentToDelete.value = doc;
  showDeleteConfirm.value = true;
};

const cancelDelete = () => {
  showDeleteConfirm.value = false;
  documentToDelete.value = null;
};

const confirmDelete = async () => {
  if (!documentToDelete.value) return;

  const doc = documentToDelete.value;
  showDeleteConfirm.value = false; // 立即关闭弹窗

  try {
    await api.deleteDocument(doc.id);
    documents.value = documents.value.filter((d) => d.id !== doc.id);
  } catch (error) {
    console.error("Failed to delete document:", error);
    alert("删除失败");
  } finally {
    documentToDelete.value = null;
  }
};

const formatTime = (time) => {
  return new Date(time).toLocaleDateString("zh-CN");
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
    processing: "AI 分析中...",
    completed: "已完成",
    failed: "分析失败",
  };
  return map[status] || status;
};

onMounted(() => {
  loadDocuments();
});
</script>

<style scoped>
.documents-view {
  padding: var(--space-xl);
  max-width: 1000px;
  margin: 0 auto;
}

.header {
  margin-bottom: var(--space-2xl);
  text-align: center;
}

.header h3 {
  font-size: var(--font-size-2xl);
  margin-bottom: var(--space-sm);
  color: var(--text-primary);
}

.subtitle {
  color: var(--text-secondary);
  font-size: var(--font-size-sm);
}

/* 上传区域 */
.upload-card {
  background: var(--bg-secondary);
  border: 2px dashed var(--border-medium);
  border-radius: var(--radius-xl);
  padding: var(--space-3xl);
  text-align: center;
  cursor: pointer;
  transition: all var(--duration-normal) var(--ease-out);
  margin-bottom: var(--space-2xl);
}

.upload-card:hover,
.upload-card.is-dragging {
  border-color: var(--brand-primary);
  background: var(--bg-hover);
}

.upload-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.upload-text {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.primary-text {
  font-size: 16px;
  font-weight: 500;
  color: var(--text-primary);
}

.secondary-text {
  font-size: 12px;
  color: var(--text-secondary);
}

/* 文档列表网格 */
.doc-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: var(--space-lg);
}

.doc-card {
  background: var(--card-bg);
  border: 1px solid var(--card-border);
  border-radius: var(--radius-lg);
  padding: var(--space-lg);
  display: flex;
  gap: var(--space-md);
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease-out);
  position: relative;
}

.doc-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
  border-color: var(--border-medium);
}

.doc-icon {
  font-size: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 56px;
  height: 56px;
  background: var(--bg-secondary);
  border-radius: var(--radius-md);
  flex-shrink: 0;
}

.doc-info {
  flex: 1;
  min-width: 0; /* 防止文本溢出 */
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 4px;
}

.doc-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.doc-title {
  font-weight: 500;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-size: 15px;
  margin-right: 8px;
  line-height: 1.4;
}

.btn-delete {
  background: none;
  border: none;
  cursor: pointer;
  opacity: 0;
  transition: opacity var(--duration-fast);
  padding: 4px;
  font-size: 14px;
  color: var(--text-tertiary);
}

.btn-delete:hover {
  color: var(--error);
  background: var(--bg-hover);
  border-radius: var(--radius-sm);
}

.doc-card:hover .btn-delete {
  opacity: 1;
}

.btn-delete:hover {
  opacity: 1 !important;
}

.doc-meta {
  display: flex;
  gap: var(--space-md);
  font-size: 12px;
  color: var(--text-tertiary);
}

.doc-status {
  margin-top: 6px;
}

.status-badge {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: var(--radius-full);
  background: var(--bg-tertiary);
  color: var(--text-secondary);
  display: inline-block;
  font-weight: 500;
}

.status-badge.completed {
  background: rgba(16, 163, 127, 0.1);
  color: var(--success);
}

.status-badge.processing {
  background: rgba(14, 165, 233, 0.1);
  color: var(--info);
  animation: pulse 2s infinite;
}

.status-badge.failed {
  background: rgba(239, 68, 68, 0.1);
  color: var(--error);
}

@keyframes pulse {
  0% {
    opacity: 1;
  }
  50% {
    opacity: 0.6;
  }
  100% {
    opacity: 1;
  }
}

.empty-state,
.loading-state {
  text-align: center;
  padding: var(--space-3xl);
  color: var(--text-secondary);
}

.empty-icon {
  font-size: 48px;
  margin-bottom: var(--space-lg);
}

.spinner {
  width: 30px;
  height: 30px;
  border: 3px solid var(--bg-secondary);
  border-top-color: var(--brand-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto var(--space-lg);
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* 删除确认对话框 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  animation: fadeIn 0.15s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.confirm-dialog {
  background: var(--bg-primary);
  border-radius: 16px;
  padding: 24px;
  max-width: 400px;
  width: 90%;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  animation: slideUp 0.2s ease-out;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.confirm-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 12px 0;
}

.confirm-message {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.5;
  margin: 0 0 24px 0;
}

.confirm-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.btn-cancel,
.btn-confirm-delete {
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  border: none;
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease-out);
}

.btn-cancel {
  background: var(--bg-secondary);
  color: var(--text-primary);
}

.btn-cancel:hover {
  background: var(--bg-hover);
}

.btn-confirm-delete {
  background: var(--error);
  color: white;
}

.btn-confirm-delete:hover {
  background: #dc2626;
  box-shadow: 0 2px 8px rgba(239, 68, 68, 0.3);
}
</style>