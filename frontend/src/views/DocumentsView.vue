<template>
  <div class="documents-view">
    <div class="card">
      <h3>📄 文档总结</h3>
      <div class="upload-area">
        <input
          ref="fileInput"
          type="file"
          accept=".pdf,.docx,.txt,.md"
          style="display: none"
          @change="handleUpload"
        />
        <button @click="fileInput?.click()">📁 选择文件</button>
      </div>

      <div class="documents-list">
        <div v-if="loading" class="loading">加载中...</div>
        <div v-else-if="documents.length === 0" class="empty">暂无文档</div>
        <router-link
          v-else
          v-for="doc in documents"
          :key="doc.id"
          :to="`/documents/${doc.id}`"
          class="doc-item"
        >
          <div class="doc-title">{{ doc.title }}</div>
          <div class="doc-time">{{ formatTime(doc.created_at) }}</div>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import api from "@/services/api";

const documents = ref([]);
const loading = ref(false);
const fileInput = ref(null);

const loadDocuments = async () => {
  try {
    loading.value = true;
    const data = await api.getDocuments();
    documents.value = data.documents || [];
  } catch (error) {
    console.error("Failed to load documents:", error);
  } finally {
    loading.value = false;
  }
};

const handleUpload = async (e) => {
  const file = e.target.files?.[0];
  if (file) {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("user_id", "default_user");
    try {
      await api.uploadDocument(formData);
      await loadDocuments();
    } catch (error) {
      console.error("Failed to upload document:", error);
    }
  }
};

const formatTime = (time) => {
  return new Date(time).toLocaleDateString("zh-CN");
};

onMounted(() => {
  loadDocuments();
});
</script>

<style scoped>
.documents-view {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.card {
  background: var(--card-bg);
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px var(--shadow-light);
}

.upload-area {
  margin: 20px 0;
  text-align: center;
}

.upload-area button {
  padding: 12px 30px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
}

.documents-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 20px;
}

.doc-item {
  padding: 15px;
  background: var(--input-bg);
  border-radius: 8px;
  text-decoration: none;
  color: inherit;
  display: flex;
  justify-content: space-between;
}

.doc-item:hover {
  background: var(--tab-hover);
}
</style>