<template>
  <div class="tasks-view">
    <div class="card">
      <h3>✅ 任务管理</h3>
      <div class="tasks-header">
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
            <div class="task-meta">
              <span :class="['status-badge', task.status]">{{
                getStatusText(task.status)
              }}</span>
              <span class="task-time">{{ formatTaskTime(task) }}</span>
            </div>
          </div>
          <button class="delete-btn" @click.stop="confirmDelete(task.id)">
            🗑️
          </button>
        </div>
      </div>
    </div>

    <!-- 删除确认对话框 -->
    <div v-if="showDeleteConfirm" class="modal-overlay" @click="cancelDelete">
      <div class="confirm-dialog" @click.stop>
        <h3 class="confirm-title">永久删除任务</h3>
        <p class="confirm-message">删除后，该任务将不可恢复。确认删除吗？</p>
        <div class="confirm-actions">
          <button class="btn-cancel" @click="cancelDelete">取消</button>
          <button class="btn-delete" @click="deleteTask">删除</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from "vue";
import { useRouter } from "vue-router";
import api from "@/services/api";

const router = useRouter();
const tasks = ref([]);
const loading = ref(false);
const statusFilter = ref("");
const showDeleteConfirm = ref(false);
const taskToDelete = ref(null);

const loadTasks = async () => {
  try {
    loading.value = true;
    const data = await api.getTasks(statusFilter.value);
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

const confirmDelete = (id) => {
  taskToDelete.value = id;
  showDeleteConfirm.value = true;
};

const cancelDelete = () => {
  showDeleteConfirm.value = false;
  taskToDelete.value = null;
};

const deleteTask = async () => {
  const id = taskToDelete.value;
  showDeleteConfirm.value = false;

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
  } finally {
    taskToDelete.value = null;
  }
};

const getStatusText = (status) => {
  const statusMap = {
    pending: "待处理",
    in_progress: "执行中",
    waiting: "等待中",
    completed: "已完成",
    failed: "失败",
    cancelled: "已取消",
  };
  return statusMap[status] || status;
};

const formatTaskTime = (task) => {
  const now = new Date();

  // 根据状态显示不同的时间
  if (task.status === "completed" && task.completed_at) {
    const completedAt = new Date(task.completed_at);
    const createdAt = new Date(task.created_at);
    const duration = Math.floor((completedAt - createdAt) / 1000 / 60); // 分钟
    const timeAgo = formatTimeAgo(completedAt, now);
    return `✅ ${timeAgo}完成 · 用时 ${formatDuration(duration)}`;
  }

  if (task.status === "in_progress" && task.started_at) {
    const startedAt = new Date(task.started_at);
    const duration = Math.floor((now - startedAt) / 1000 / 60); // 分钟
    const timeAgo = formatTimeAgo(startedAt, now);
    return `▶️ ${timeAgo}开始 · 已运行 ${formatDuration(duration)}`;
  }

  if (task.status === "failed" && task.updated_at) {
    const failedAt = new Date(task.updated_at);
    const timeAgo = formatTimeAgo(failedAt, now);
    return `❌ ${timeAgo}失败`;
  }

  // 待处理、等待中等状态显示创建时间
  if (task.created_at) {
    const createdAt = new Date(task.created_at);
    const timeAgo = formatTimeAgo(createdAt, now);
    return `📅 ${timeAgo}创建`;
  }

  return "";
};

const formatTimeAgo = (date, now) => {
  const seconds = Math.floor((now - date) / 1000);

  if (seconds < 60) return "刚刚";
  if (seconds < 3600) return `${Math.floor(seconds / 60)}分钟前`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}小时前`;
  if (seconds < 2592000) return `${Math.floor(seconds / 86400)}天前`;
  return date.toLocaleDateString("zh-CN");
};

const formatDuration = (minutes) => {
  if (minutes < 1) return "不到1分钟";
  if (minutes < 60) return `${minutes}分钟`;
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;
  return mins > 0 ? `${hours}小时${mins}分钟` : `${hours}小时`;
};

// 监听刷新事件
const handleRefresh = () => {
  loadTasks();
};

onMounted(() => {
  loadTasks();
  window.addEventListener("refresh-tasks", handleRefresh);
});

onUnmounted(() => {
  window.removeEventListener("refresh-tasks", handleRefresh);
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
  padding: 16px;
  background: var(--input-bg);
  border-radius: 10px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  transition: all 0.2s;
  cursor: pointer;
  border: 1px solid transparent;
}

.task-item:hover {
  background: var(--tab-hover);
  border-color: var(--primary-color);
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.task-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex: 1;
  min-width: 0;
}

.task-title {
  font-weight: 500;
  font-size: 15px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.task-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.task-time {
  font-size: 12px;
  color: #888;
}

.status-badge {
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 600;
  white-space: nowrap;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.status-badge.pending {
  background: #e2e8f0;
  color: #4a5568;
}
.status-badge.in_progress {
  background: #ebf8ff;
  color: #3182ce;
}
.status-badge.waiting {
  background: #fef3c7;
  color: #92400e;
}
.status-badge.completed {
  background: #c6f6d5;
  color: #2f855a;
}
.status-badge.failed {
  background: #fed7d7;
  color: #c53030;
}
.status-badge.cancelled {
  background: #e5e7eb;
  color: #6b7280;
}

.delete-btn {
  padding: 8px 12px;
  background: transparent;
  border: 1px solid #fee;
  border-radius: 6px;
  cursor: pointer;
  font-size: 16px;
  transition: all 0.2s;
  flex-shrink: 0;
}

.delete-btn:hover {
  background: #fee;
  border-color: #fcc;
  transform: scale(1.1);
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
.btn-delete {
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease-out;
}

.btn-cancel {
  background: var(--bg-secondary);
  color: var(--text-primary);
}

.btn-cancel:hover {
  background: var(--bg-hover);
}

.btn-delete {
  background: var(--error);
  color: white;
}

.btn-delete:hover {
  background: #dc2626;
  box-shadow: 0 2px 8px rgba(239, 68, 68, 0.3);
}
</style>
