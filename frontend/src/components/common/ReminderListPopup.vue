<template>
  <div class="reminder-popup">
    <div class="popup-header">
      <h3>未完成提醒 ({{ reminders.length }})</h3>
      <button class="close-btn" @click="$emit('close')">
        <svg
          width="18"
          height="18"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
        >
          <line x1="18" y1="6" x2="6" y2="18"></line>
          <line x1="6" y1="6" x2="18" y2="18"></line>
        </svg>
      </button>
    </div>

    <div class="popup-content">
      <div v-if="loading" class="loading">加载中...</div>
      <div v-else-if="reminders.length === 0" class="empty">
        <div class="empty-icon">🎉</div>
        <p>暂无未完成提醒</p>
      </div>
      <div v-else class="reminders-list">
        <div
          v-for="reminder in reminders"
          :key="reminder.reminder_id"
          class="reminder-item"
        >
          <div class="reminder-main">
            <div class="reminder-top">
              <span class="reminder-title">{{ reminder.title }}</span>
              <span
                v-if="timeRemainingMap[reminder.reminder_id]"
                class="time-badge"
                :class="{
                  urgent:
                    timeRemainingMap[reminder.reminder_id].includes('秒') ||
                    timeRemainingMap[reminder.reminder_id] === '即将触发',
                }"
              >
                {{ timeRemainingMap[reminder.reminder_id] }}
              </span>
            </div>
            <div
              class="reminder-desc"
              v-if="reminder.content && reminder.content !== reminder.title"
            >
              {{ reminder.content }}
            </div>
            <div class="reminder-footer">
              <span class="condition-text">
                {{ formatCondition(reminder) }}
              </span>
            </div>
          </div>
          <div class="reminder-actions">
            <button
              class="action-btn delete"
              @click.stop="$emit('delete', reminder.reminder_id)"
              title="删除"
            >
              <svg
                width="14"
                height="14"
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
  </div>
</template>

<script setup>
import { defineProps } from "vue";

const props = defineProps({
  reminders: {
    type: Array,
    default: () => [],
  },
  loading: {
    type: Boolean,
    default: false,
  },
  timeRemainingMap: {
    type: Object,
    default: () => ({}),
  },
});

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
        ? new Date(condition.datetime).toLocaleString([], {
            month: "numeric",
            day: "numeric",
            hour: "2-digit",
            minute: "2-digit",
          })
        : "无效时间";
    case "weather":
      return `${condition.location || "本地"} - ${
        condition.condition || "任意天气"
      }`;
    case "behavior":
      return `不活跃 > ${condition.inactive_hours}h`;
    case "habit":
      return `习惯: ${condition.pattern}`;
    default:
      return "自定义条件";
  }
};
</script>

<style scoped>
.reminder-popup {
  width: 320px;
  max-height: 480px;
  background: var(--bg-primary);
  border-radius: 12px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.15);
  border: 1px solid var(--border-light);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.popup-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid var(--border-light);
  background: var(--bg-secondary);
}

.popup-header h3 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.close-btn {
  background: transparent;
  border: none;
  color: var(--text-tertiary);
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  display: flex;
}

.close-btn:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.popup-content {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.loading {
  text-align: center;
  padding: 20px;
  color: var(--text-tertiary);
  font-size: 13px;
}

.empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  color: var(--text-tertiary);
}

.empty-icon {
  font-size: 32px;
  margin-bottom: 8px;
}

.empty p {
  margin: 0;
  font-size: 13px;
}

.reminders-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.reminder-item {
  display: flex;
  gap: 10px;
  padding: 10px;
  background: var(--bg-secondary);
  border-radius: 8px;
  border: 1px solid transparent;
  transition: all 0.2s;
}

.reminder-item:hover {
  border-color: var(--border-medium);
  background: var(--bg-hover);
}

.reminder-main {
  flex: 1;
  min-width: 0;
}

.reminder-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 4px;
  gap: 8px;
}

.reminder-title {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.time-badge {
  font-size: 11px;
  padding: 2px 6px;
  border-radius: 10px;
  background: rgba(33, 150, 243, 0.1);
  color: #2196f3;
  white-space: nowrap;
  flex-shrink: 0;
}

.time-badge.urgent {
  background: rgba(244, 67, 54, 0.1);
  color: #f44336;
}

.reminder-desc {
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 4px;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.reminder-footer {
  display: flex;
  align-items: center;
}

.condition-text {
  font-size: 11px;
  color: var(--text-tertiary);
}

.reminder-actions {
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.action-btn {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: transparent;
  border-radius: 4px;
  cursor: pointer;
  color: var(--text-tertiary);
  transition: all 0.2s;
}

.action-btn:hover {
  background: var(--bg-primary);
}

.action-btn.delete:hover {
  color: var(--error);
  background: rgba(244, 67, 54, 0.1);
}
</style>
