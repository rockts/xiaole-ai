<template>
  <div>
    <div class="reminders-view">
      <div class="card">
        <div class="header">
          <h3>🔔 提醒管理</h3>
          <div class="controls">
            <label class="toggle-label">
              <input
                type="checkbox"
                v-model="showDisabled"
                @change="loadReminders"
              />
              显示已禁用
            </label>
          </div>
        </div>

        <div class="reminders-list">
          <div v-if="loading" class="loading">加载中...</div>
          <div v-else-if="reminders.length === 0" class="empty">暂无提醒</div>
          <div
            v-else
            v-for="reminder in reminders"
            :key="reminder.reminder_id"
            class="reminder-item"
            :class="{ disabled: !reminder.enabled }"
          >
            <div class="reminder-main">
              <div class="reminder-header">
                <span class="reminder-title">{{
                  reminder.title || "未命名提醒"
                }}</span>
                <span class="reminder-type" :class="reminder.reminder_type">
                  {{ formatType(reminder.reminder_type) }}
                </span>
                <span
                  class="reminder-priority"
                  :class="'p' + reminder.priority"
                >
                  P{{ reminder.priority }}
                </span>
              </div>
              <div
                class="reminder-content"
                v-if="reminder.content && reminder.content !== reminder.title"
              >
                {{ reminder.content }}
              </div>
              <div class="reminder-condition">
                <span class="icon">⏰</span>
                {{ formatCondition(reminder) }}
              </div>
              <div class="reminder-meta">
                <span v-if="reminder.repeat" class="tag repeat">🔁 重复</span>
                <span
                  v-if="timeRemainingMap[reminder.reminder_id]"
                  class="tag time-left"
                >
                  ⏳ {{ timeRemainingMap[reminder.reminder_id] }}
                </span>
                <span class="created-at"
                  >创建于: {{ formatDate(reminder.created_at) }}</span
                >
              </div>
            </div>

            <div class="reminder-actions">
              <label class="switch">
                <input
                  type="checkbox"
                  :checked="reminder.enabled"
                  @change="toggleReminder(reminder)"
                />
                <span class="slider round"></span>
              </label>
              <button
                class="btn-icon"
                @click="requestDelete(reminder.reminder_id)"
                title="删除"
              >
                <svg
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <polyline points="3 6 5 6 21 6"></polyline>
                  <path
                    d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"
                  ></path>
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 删除确认对话框 -->
      <div
        v-if="showDeleteConfirm"
        class="modal-overlay"
        @click.self="cancelDelete"
      >
        <div class="confirm-dialog">
          <h3 class="confirm-title">删除提醒</h3>
          <p class="confirm-message">确定要删除这个提醒吗？此操作无法撤销。</p>
          <div class="confirm-actions">
            <button class="btn-cancel" @click="cancelDelete">取消</button>
            <button class="btn-delete" @click="confirmDelete">删除</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from "vue";
import api from "@/services/api";
import { useWebSocket } from "@/composables/useWebSocket";

const reminders = ref([]);
const loading = ref(false);
const showDisabled = ref(false); // 默认只显示启用的提醒
const showDeleteConfirm = ref(false);
const deletingReminderId = ref(null);
const timeRemainingMap = ref({});
let timerInterval = null;

const updateTimeRemaining = () => {
  const now = Date.now();
  const map = {};

  reminders.value.forEach((r) => {
    if (!r.enabled || r.reminder_type !== "time") return;

    let condition = r.trigger_condition;
    if (typeof condition === "string") {
      try {
        condition = JSON.parse(condition);
      } catch (e) {
        return;
      }
    }
    if (!condition || !condition.datetime) return;

    let nextTime = new Date(condition.datetime).getTime();

    // 如果是重复提醒，且已经触发过，计算下一次触发时间
    if (r.repeat && r.repeat_interval) {
      const interval = r.repeat_interval * 1000;
      if (r.last_triggered) {
        const last = new Date(r.last_triggered).getTime();
        nextTime = last + interval;
      }
    }

    const diff = nextTime - now;
    if (diff < 0) {
      map[r.reminder_id] = "即将触发";
    } else {
      const seconds = Math.floor(diff / 1000);
      const minutes = Math.floor(seconds / 60);
      const hours = Math.floor(minutes / 60);
      const days = Math.floor(hours / 24);

      if (days > 0) {
        map[r.reminder_id] = `${days}天 ${hours % 24}小时后`;
      } else if (hours > 0) {
        map[r.reminder_id] = `${hours}小时 ${minutes % 60}分后`;
      } else if (minutes > 0) {
        map[r.reminder_id] = `${minutes}分钟后`;
      } else {
        map[r.reminder_id] = `${seconds}秒后`;
      }
    }
  });
  timeRemainingMap.value = map;
};

const loadReminders = async () => {
  try {
    loading.value = true;
    // api.getReminders accepts enabledOnly.
    // If showDisabled is true, we want enabledOnly=false.
    // If showDisabled is false, we want enabledOnly=true.
    const data = await api.getReminders(!showDisabled.value);
    reminders.value = data.reminders || [];
    updateTimeRemaining();
  } catch (error) {
    console.error("Failed to load reminders:", error);
  } finally {
    loading.value = false;
  }
};

const toggleReminder = async (reminder) => {
  const newState = !reminder.enabled;
  try {
    // Optimistic update
    reminder.enabled = newState;
    await api.updateReminder(reminder.reminder_id, { enabled: newState });
  } catch (error) {
    console.error("Failed to update reminder:", error);
    // Revert on failure
    reminder.enabled = !newState;
    alert(`更新状态失败: ${error.response?.data?.detail || "请重试"}`);
  }
};

const requestDelete = (id) => {
  deletingReminderId.value = id;
  showDeleteConfirm.value = true;
};

const cancelDelete = () => {
  showDeleteConfirm.value = false;
  deletingReminderId.value = null;
};

const confirmDelete = async () => {
  if (!deletingReminderId.value) return;

  const id = deletingReminderId.value;
  try {
    await api.deleteReminder(id);
    reminders.value = reminders.value.filter((r) => r.reminder_id !== id);
    showDeleteConfirm.value = false;
    deletingReminderId.value = null;
  } catch (error) {
    console.error("Failed to delete reminder:", error);
    alert(`删除失败: ${error.response?.data?.detail || "请重试"}`);
  }
};

// Deprecated: old delete method
const deleteReminder = async (id) => {
  requestDelete(id);
};

const formatType = (type) => {
  const map = {
    time: "时间",
    weather: "天气",
    behavior: "行为",
    habit: "习惯",
  };
  return map[type] || type;
};

const formatCondition = (reminder) => {
  let condition = reminder.trigger_condition;
  if (typeof condition === "string") {
    try {
      condition = JSON.parse(condition);
    } catch (e) {
      return condition;
    }
  }

  if (!condition) return "无触发条件";

  switch (reminder.reminder_type) {
    case "time":
      return condition.datetime
        ? new Date(condition.datetime).toLocaleString()
        : "无效时间";
    case "weather":
      return `${condition.location || "本地"} - ${
        condition.condition || "任意天气"
      }`;
    case "behavior":
      return `不活跃超过 ${condition.inactive_hours} 小时`;
    case "habit":
      return `习惯模式: ${condition.pattern} (${condition.time})`;
    default:
      return JSON.stringify(condition);
  }
};

const formatDate = (dateStr) => {
  if (!dateStr) return "";
  return new Date(dateStr).toLocaleString();
};

const { on } = useWebSocket();
let wsUnsubscribe = null;

onMounted(() => {
  loadReminders();
  // 监听提醒确认事件，刷新列表
  window.addEventListener("reminder-confirmed", loadReminders);
  window.addEventListener("refresh-reminders", loadReminders);

  // 启动倒计时更新
  timerInterval = setInterval(updateTimeRemaining, 1000);

  // 监听 WebSocket 消息，自动刷新列表
  wsUnsubscribe = on((data) => {
    if (
      data.type === "reminder_created" ||
      data.type === "reminder_updated" ||
      data.type === "reminder_deleted"
    ) {
      loadReminders();
    }
  });
});

onUnmounted(() => {
  window.removeEventListener("reminder-confirmed", loadReminders);
  window.removeEventListener("refresh-reminders", loadReminders);
  if (timerInterval) clearInterval(timerInterval);
  if (wsUnsubscribe) {
    wsUnsubscribe();
  }
});
</script>

<style scoped>
.reminders-view {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.card {
  background: var(--card-bg);
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid var(--border-color);
}

.controls {
  display: flex;
  gap: 15px;
  align-items: center;
}

.toggle-label {
  display: flex;
  align-items: center;
  gap: 5px;
  cursor: pointer;
  font-size: 0.9em;
  color: var(--text-secondary);
}

.reminder-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  background: var(--input-bg);
  border-radius: 8px;
  margin-bottom: 12px;
  border-left: 4px solid var(--brand-primary);
  transition: all 0.2s;
}

.reminder-item.disabled {
  opacity: 0.6;
  border-left-color: var(--text-secondary);
  background: rgba(0, 0, 0, 0.2);
}

.reminder-main {
  flex: 1;
}

.reminder-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 6px;
}

.reminder-title {
  font-weight: bold;
  font-size: 1.1em;
}

.reminder-type {
  font-size: 0.8em;
  padding: 2px 6px;
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.1);
}

.reminder-type.time {
  color: #4caf50;
  background: rgba(76, 175, 80, 0.1);
}
.reminder-type.weather {
  color: #2196f3;
  background: rgba(33, 150, 243, 0.1);
}
.reminder-type.behavior {
  color: #ff9800;
  background: rgba(255, 152, 0, 0.1);
}

.reminder-priority {
  font-size: 0.8em;
  font-weight: bold;
}
.p1 {
  color: #f44336;
}
.p2 {
  color: #ff9800;
}
.p3 {
  color: #2196f3;
}

.reminder-content {
  margin-bottom: 8px;
  color: var(--text-primary);
}

.reminder-condition {
  font-size: 0.9em;
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  gap: 5px;
  background: rgba(0, 0, 0, 0.1);
  padding: 4px 8px;
  border-radius: 4px;
  width: fit-content;
}

.reminder-meta {
  margin-top: 8px;
  font-size: 0.8em;
  color: var(--text-secondary);
  display: flex;
  gap: 10px;
}

.tag.repeat {
  color: #9c27b0;
}

.tag.time-left {
  color: #ff9800;
  font-weight: bold;
  background: rgba(255, 152, 0, 0.1);
  padding: 2px 6px;
  border-radius: 4px;
}

.reminder-actions {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  margin-left: 15px;
}

.btn-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  padding: 0;
  background: transparent;
  border: none;
  border-radius: var(--radius-md);
  color: var(--text-tertiary);
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease-out);
}

.btn-icon:hover {
  background: var(--bg-hover);
  color: var(--error);
}

/* Switch Toggle */
.switch {
  position: relative;
  display: inline-block;
  width: 40px;
  height: 20px;
}

.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #ccc;
  transition: 0.4s;
  border-radius: 20px;
}

.slider:before {
  position: absolute;
  content: "";
  height: 16px;
  width: 16px;
  left: 2px;
  bottom: 2px;
  background-color: white;
  transition: 0.4s;
  border-radius: 50%;
}

input:checked + .slider {
  background-color: var(--brand-primary);
}

input:checked + .slider:before {
  transform: translateX(20px);
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
  backdrop-filter: blur(2px);
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
  border: 1px solid var(--border-color);
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
  transition: all var(--duration-fast) var(--ease-out);
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

/* 提醒弹窗样式 */
.remind-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.35);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 99999;
}
.remind-modal {
  background: #fff;
  border-radius: 14px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.18);
  padding: 32px 28px 24px 28px;
  min-width: 320px;
  max-width: 90vw;
  text-align: center;
  animation: fadeInRemind 0.2s;
}
.remind-title {
  font-size: 1.3em;
  font-weight: bold;
  margin-bottom: 12px;
}
.remind-content {
  font-size: 1.1em;
  margin-bottom: 22px;
  color: #333;
}
.remind-confirm-btn {
  background: #4caf50;
  color: #fff;
  border: none;
  border-radius: 8px;
  padding: 10px 32px;
  font-size: 1em;
  cursor: pointer;
  transition: background 0.2s;
}
.remind-confirm-btn:hover {
  background: #388e3c;
}
@keyframes fadeInRemind {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
