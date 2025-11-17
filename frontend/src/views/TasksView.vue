<template>
  <div class="tasks-view">
    <div class="card">
      <h3>✅ 任务管理</h3>
      <div class="tasks-header">
        <button @click="loadTasks">🔄 刷新</button>
        <select v-model="statusFilter" @change="loadTasks">
          <option value="">全部状态</option>
          <option value="pending">待处理</option>
          <option value="in_progress">执行中</option>
          <option value="completed">已完成</option>
        </select>
      </div>

      <div class="tasks-list">
        <div v-if="loading" class="loading">加载中...</div>
        <div v-else-if="tasks.length === 0" class="empty">暂无任务</div>
        <router-link
          v-else
          v-for="task in tasks"
          :key="task.id"
          :to="`/task/${task.id}`"
          class="task-item"
        >
          <div class="task-title">{{ task.title }}</div>
          <div class="task-status">{{ task.status }}</div>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import api from "@/services/api";

const tasks = ref([]);
const loading = ref(false);
const statusFilter = ref("");

const loadTasks = async () => {
  try {
    loading.value = true;
    const data = await api.getTasks("default_user", statusFilter.value);
    tasks.value = data.tasks || [];
  } catch (error) {
    console.error("Failed to load tasks:", error);
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  loadTasks();
});
</script>

<style scoped>
.tasks-view {
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

.tasks-header {
  display: flex;
  gap: 10px;
  margin: 15px 0;
}

.tasks-header button,
.tasks-header select {
  padding: 10px 20px;
  border-radius: 8px;
  border: none;
  cursor: pointer;
}

.tasks-header button {
  background: #667eea;
  color: white;
}

.tasks-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 20px;
}

.task-item {
  padding: 15px;
  background: var(--input-bg);
  border-radius: 8px;
  text-decoration: none;
  color: inherit;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: background 0.2s;
}

.task-item:hover {
  background: var(--tab-hover);
}

.task-title {
  font-weight: 500;
}

.task-status {
  padding: 4px 12px;
  background: #667eea;
  color: white;
  border-radius: 4px;
  font-size: 12px;
}
</style>
