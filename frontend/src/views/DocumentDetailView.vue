<template>
  <div class="doc-detail-view">
    <div class="card">
      <h3>文档详情</h3>
      <div v-if="loading" class="loading">加载中...</div>
      <div v-else-if="document">
        <h4>{{ document.title }}</h4>
        <div class="summary">{{ document.summary }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRoute } from "vue-router";
import api from "@/services/api";

const route = useRoute();
const document = ref(null);
const loading = ref(false);

// ...existing code...
onMounted(async () => {
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
});
// ...existing code...
</script>

<style scoped>
.doc-detail-view {
  padding: 20px;
  max-width: 900px;
  margin: 0 auto;
}

.card {
  background: var(--card-bg);
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 2px 8px var(--shadow-light);
}

.summary {
  margin-top: 20px;
  line-height: 1.8;
  white-space: pre-wrap;
}
</style>
