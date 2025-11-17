<template>
  <div class="task-detail-view">
    <div class="card">
      <h3>任务详情</h3>
      <div v-if="loading" class="loading">加载中...</div>
      <div v-else-if="task">
        <div class="detail-item">
          <label>标题:</label>
          <div>{{ task.title }}</div>
        </div>
        <div class="detail-item">
          <label>状态:</label>
          <div>{{ task.status }}</div>
        </div>
        <div class="detail-item">
          <label>描述:</label>
          <div>{{ task.description }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRoute } from "vue-router";
import api from "@/services/api";

const route = useRoute();
const task = ref(null);
const loading = ref(false);

onMounted(async () => {
  try {
    loading.value = true;
    task.value = await api.getTask(route.params.id);
  } catch (error) {
    console.error("Failed to load task:", error);
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>
.task-detail-view {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.card {
  background: var(--card-bg);
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px var(--shadow-light);
}

.detail-item {
  margin: 15px 0;
  padding: 15px;
  background: var(--input-bg);
  border-radius: 8px;
}

.detail-item label {
  font-weight: 600;
  color: var(--text-secondary);
  display: block;
  margin-bottom: 8px;
}
</style>