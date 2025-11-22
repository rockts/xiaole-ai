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
        <div
          v-else
          v-for="task in tasks"
          :key="task.id"
          class="task-item"
          @click="goToTask(task.id)"
        >
          <div class="task-content">
            <div class="task-title">{{ task.title }}</div>
            <span :class="['status-badge', task.status]">{{
              task.status
            }}</span>
          </div>
          <button class="delete-btn" @click.stop="deleteTask(task.id)">
            🗑️
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

const goToTask = (id) => {
  router.push(`/task/${id}`);
};

const deleteTask = async (id) => {
  if (!confirm("确定要删除这个任务吗？")) return;

  try {
    const result = await api.deleteTask(id);
    if (result.success) {
      await loadTasks();
    } else {
      alert("删除失败: " + (result.error || "未知错误"));
    }
  } catch (error) {
    console.error("Failed to delete task:", error);
    alert("删除出错");
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
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: background 0.2s;
  cursor: pointer;
}

.task-item:hover {
  background: var(--tab-hover);
}

.task-content {
  display: flex;
  align-items: center;
  gap: 15px;
}

.task-title {
  font-weight: 500;
}

.status-badge {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.pending {
  background: #e2e8f0;
  color: #4a5568;
}
.status-badge.in_progress {
  background: #ebf8ff;
  color: #3182ce;
}
.status-badge.completed {
  background: #c6f6d5;
  color: #2f855a;
}
.status-badge.failed {
  background: #fed7d7;
  color: #c53030;
}

.delete-btn {
  padding: 6px 10px;
  background: #fed7d7;
  border: 1px solid #feb2b2;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.delete-btn:hover {
  background: #fc8181;
  color: white;
}
</style>
