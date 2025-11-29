<template>
  <div class="task-detail-view">
    <div class="card">
      <div class="header">
        <div class="left-section">
          <button @click="goBack" class="back-btn">← 返回</button>
          <h3>任务详情</h3>
        </div>
        <div class="actions">
          <button @click="deleteTask" class="delete-btn">🗑️ 删除</button>
          <button @click="loadTask" class="refresh-btn">🔄 刷新</button>
        </div>
      </div>

      <div v-if="loading" class="loading">加载中...</div>
      <div v-else-if="task">
        <div class="task-info">
          <div class="detail-item">
            <label>标题:</label>
            <div class="value">{{ task.title }}</div>
          </div>
          <div class="detail-item">
            <label>状态:</label>
            <div class="value">
              <span :class="['status-badge', task.status]">{{
                task.status
              }}</span>
            </div>
          </div>
          <div class="detail-item">
            <label>描述:</label>
            <div class="value">{{ task.description || "无描述" }}</div>
          </div>
        </div>

        <!-- 关联提醒板块 -->
        <div v-if="reminders.length > 0" class="reminders-section">
          <h4>🔔 关联提醒 ({{ reminders.length }})</h4>
          <div class="reminders-list">
            <div
              v-for="reminder in reminders"
              :key="reminder.reminder_id"
              class="reminder-item"
              :class="{ disabled: !reminder.enabled }"
            >
              <div class="reminder-header">
                <span class="reminder-time">{{
                  formatReminderTime(reminder)
                }}</span>
                <span
                  class="reminder-status"
                  :class="{ active: reminder.enabled }"
                >
                  {{ reminder.enabled ? "启用" : "已禁用" }}
                </span>
              </div>
              <div class="reminder-content">{{ reminder.content }}</div>
            </div>
          </div>
        </div>

        <div class="steps-section">
          <h4>执行步骤 ({{ steps.length }})</h4>
          <div class="steps-list">
            <div
              v-for="step in steps"
              :key="step.id"
              class="step-item"
              :class="step.status"
            >
              <div class="step-header">
                <span class="step-num">#{{ step.step_num }}</span>
                <span class="step-desc">{{ step.description }}</span>
                <span :class="['status-badge', step.status]">{{
                  step.status
                }}</span>
              </div>

              <!-- 优化后的友好显示 -->
              <div class="step-friendly-content">
                <div class="friendly-row">
                  <span class="icon">🔧</span>
                  <span class="text">{{
                    getFriendlyActionDescription(step)
                  }}</span>
                </div>
                <div v-if="step.result" class="friendly-row result">
                  <span class="icon">📝</span>
                  <span class="text">{{
                    getFriendlyResultDescription(step)
                  }}</span>
                </div>
              </div>

              <!-- 技术详情（默认折叠） -->
              <details class="tech-details">
                <summary>显示技术详情</summary>

                <!-- 原始参数显示 -->
                <div v-if="step.action_params" class="step-params">
                  <div class="params-title">参数:</div>
                  <div class="params-content">
                    <div
                      v-for="(val, key) in parseParams(step.action_params)"
                      :key="key"
                      class="param-row"
                    >
                      <span class="param-key">{{ key }}:</span>
                      <span class="param-val">{{ val }}</span>
                    </div>
                  </div>
                </div>

                <!-- 原始结果显示 -->
                <div v-if="step.result" class="step-result">
                  <div class="result-title">执行结果:</div>
                  <div class="result-content">
                    <div v-if="isJson(step.result)">
                      <div
                        v-if="getJson(step.result).success === false"
                        class="error-text"
                      >
                        ❌ {{ getJson(step.result).error || "执行失败" }}
                      </div>
                      <div v-else-if="getJson(step.result).data">
                        <div class="success-text">
                          {{ getJson(step.result).data }}
                        </div>
                      </div>
                      <div v-else>
                        <pre>{{ formatJson(step.result) }}</pre>
                      </div>
                    </div>
                    <div v-else>
                      <div class="text-result">{{ step.result }}</div>
                    </div>
                  </div>
                </div>
              </details>

              <div v-if="step.error_message" class="step-error">
                <strong>错误:</strong> {{ step.error_message }}
              </div>
            </div>
          </div>
        </div>
      </div>
      <div v-else class="error">未找到任务信息</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import api from "@/services/api";

const route = useRoute();
const router = useRouter();
const task = ref(null);
const steps = ref([]);
const reminders = ref([]); // 新增：关联提醒列表
const loading = ref(false);

const goBack = () => {
  router.push("/tasks");
};

const isJson = (str) => {
  try {
    JSON.parse(str);
    return true;
  } catch (e) {
    return false;
  }
};

const getJson = (str) => {
  try {
    return JSON.parse(str);
  } catch (e) {
    return {};
  }
};

const parseParams = (jsonStr) => {
  try {
    if (typeof jsonStr === "string") {
      return JSON.parse(jsonStr);
    }
    return jsonStr;
  } catch (e) {
    return {};
  }
};

const formatJson = (jsonStr) => {
  try {
    if (typeof jsonStr === "string") {
      return JSON.stringify(JSON.parse(jsonStr), null, 2);
    }
    return JSON.stringify(jsonStr, null, 2);
  } catch (e) {
    return jsonStr;
  }
};

const getFriendlyActionDescription = (step) => {
  try {
    const params = parseParams(step.action_params);
    if (step.action_type === "tool_call") {
      const toolName = params.tool_name;
      const toolParams = params.params || {};

      switch (toolName) {
        case "reminder":
          return `设置提醒：${toolParams.content} (时间: ${toolParams.time_desc})`;
        case "weather":
          return `查询天气：${toolParams.city || "当前城市"} (${
            toolParams.query_type === "now" ? "实时" : "预报"
          })`;
        case "search":
          return `搜索：${toolParams.query}`;
        case "calculator":
          return `计算：${toolParams.expression}`;
        case "time":
          return `查询当前时间`;
        case "system_info":
          return `查询系统信息`;
        case "file":
          return `文件操作：${toolParams.operation} ${toolParams.path || ""}`;
        default:
          return `调用工具：${toolName}`;
      }
    } else if (step.action_type === "user_confirm") {
      return `等待确认：${step.description}`;
    } else if (step.action_type === "wait") {
      return `等待：${params.duration} 秒`;
    }
    return step.description;
  } catch (e) {
    return step.description;
  }
};

const getFriendlyResultDescription = (step) => {
  if (!step.result) return null;
  try {
    const result = getJson(step.result);
    if (result.success === false) {
      return `❌ 失败: ${result.error || "未知错误"}`;
    }

    if (step.action_type === "tool_call") {
      const params = parseParams(step.action_params);
      const toolName = params.tool_name;

      if (toolName === "weather") {
        const data = result.data || result;
        if (data.now)
          return `✅ ${data.city} ${data.now.text} ${data.now.temp}°C`;
        return `✅ 天气数据已获取`;
      } else if (toolName === "reminder") {
        return `✅ 提醒已创建`;
      } else if (toolName === "search") {
        const items = result.data || result;
        return `✅ 找到 ${Array.isArray(items) ? items.length : 0} 条结果`;
      } else if (toolName === "calculator") {
        return `✅ 结果: ${result.data || result.result}`;
      }
    }

    return `✅ 执行完成`;
  } catch (e) {
    return step.result;
  }
};

const formatReminderTime = (reminder) => {
  try {
    let condition = reminder.trigger_condition;
    if (typeof condition === "string") {
      condition = JSON.parse(condition);
    }
    if (reminder.reminder_type === "time" && condition.datetime) {
      const dt = new Date(condition.datetime);
      return dt.toLocaleString("zh-CN", {
        month: "2-digit",
        day: "2-digit",
        hour: "2-digit",
        minute: "2-digit",
      });
    }
    return "未知时间";
  } catch (e) {
    return "时间解析错误";
  }
};

const loadTask = async () => {
  try {
    loading.value = true;
    const taskId = route.params.id;
    const data = await api.getTask(taskId);

    if (data.success && data.task) {
      task.value = data.task;
      steps.value = data.steps || [];

      // 加载关联提醒
      try {
        const allReminders = await api.getReminders(false); // false = 获取所有状态的提醒
        if (allReminders && Array.isArray(allReminders)) {
          reminders.value = allReminders.filter(
            (r) => r.task_id === parseInt(taskId)
          );
        }
      } catch (remError) {
        console.error("Failed to load reminders:", remError);
      }
    }
  } catch (error) {
    console.error("Failed to load task:", error);
  } finally {
    loading.value = false;
  }
};

const deleteTask = async () => {
  if (!confirm("确定要删除这个任务吗？关联的提醒也会被删除。")) return;

  try {
    const result = await api.deleteTask(route.params.id);
    if (result.success) {
      router.push("/tasks");
    } else {
      alert("删除失败: " + (result.error || "未知错误"));
    }
  } catch (error) {
    console.error("Failed to delete task:", error);
    alert("删除出错");
  }
};

// 监听路由参数变化，当从一个任务详情页跳到另一个时重新加载
watch(
  () => route.params.id,
  (newId) => {
    if (newId) {
      loadTask();
    }
  },
  { immediate: true } // immediate: true 替代 onMounted，首次加载也会触发
);
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

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.left-section {
  display: flex;
  align-items: center;
  gap: 15px;
}

.back-btn {
  background: none;
  border: none;
  font-size: 16px;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 5px 10px;
  border-radius: 6px;
  transition: background 0.2s;
}

.back-btn:hover {
  background: var(--bg-secondary);
  color: var(--text-primary);
}

.actions {
  display: flex;
  gap: 10px;
}

.refresh-btn {
  padding: 8px 16px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.delete-btn {
  padding: 8px 16px;
  background: #fed7d7;
  color: #c53030;
  border: 1px solid #feb2b2;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.delete-btn:hover {
  background: #fc8181;
  color: white;
}

.task-info {
  background: var(--input-bg);
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 20px;
}

.detail-item {
  margin-bottom: 12px;
}

.detail-item label {
  font-weight: 600;
  color: var(--text-secondary);
  margin-right: 10px;
}

.detail-item .value {
  display: inline-block;
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

/* 提醒板块样式 */
.reminders-section {
  margin-bottom: 20px;
  background: #fffaf0; /* 浅橙色背景 */
  border: 1px solid #fbd38d;
  border-radius: 8px;
  padding: 15px;
}

.reminders-section h4 {
  margin: 0 0 10px;
  color: #c05621;
  font-size: 15px;
}

.reminders-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.reminder-item {
  background: white;
  border-radius: 6px;
  padding: 10px;
  border-left: 3px solid #ed8936;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.reminder-item.disabled {
  border-left-color: #cbd5e0;
  opacity: 0.7;
}

.reminder-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 5px;
  font-size: 12px;
}

.reminder-time {
  font-weight: bold;
  color: #2d3748;
}

.reminder-status {
  padding: 1px 6px;
  border-radius: 10px;
  background: #edf2f7;
  color: #718096;
}

.reminder-status.active {
  background: #c6f6d5;
  color: #2f855a;
}

.reminder-content {
  font-size: 14px;
  color: #4a5568;
}

/* 步骤样式优化 */
.steps-section h4 {
  margin: 20px 0 10px;
  color: var(--text-primary);
}

.steps-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.step-item {
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 15px;
  background: var(--bg-primary);
}

.step-item.completed {
  border-left: 4px solid #48bb78;
}
.step-item.failed {
  border-left: 4px solid #f56565;
}
.step-item.in_progress {
  border-left: 4px solid #4299e1;
}

.step-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.step-num {
  font-weight: bold;
  color: var(--text-secondary);
}

.step-desc {
  flex: 1;
  font-weight: 500;
}

/* 友好显示样式 */
.step-friendly-content {
  margin-top: 10px;
  background: var(--bg-secondary);
  border-radius: 6px;
  padding: 10px;
}

.friendly-row {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  font-size: 14px;
  color: var(--text-primary);
  line-height: 1.5;
}

.friendly-row.result {
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px dashed var(--border-color);
  color: #2f855a;
}

.friendly-row .icon {
  font-size: 16px;
  flex-shrink: 0;
}

/* 技术详情折叠样式 */
.tech-details {
  margin-top: 10px;
  font-size: 12px;
}

.tech-details summary {
  cursor: pointer;
  color: var(--text-secondary);
  user-select: none;
  margin-bottom: 5px;
}

.tech-details summary:hover {
  color: var(--text-primary);
}

/* 参数和结果样式优化 */
.step-params,
.step-result {
  margin-top: 10px;
  font-size: 13px;
  background: var(--bg-secondary);
  padding: 10px;
  border-radius: 6px;
}

.params-title,
.result-title {
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: 5px;
  font-size: 12px;
}

.param-row {
  display: flex;
  margin-bottom: 3px;
}

.param-key {
  color: #718096;
  margin-right: 8px;
  min-width: 60px;
}

.param-val {
  color: var(--text-primary);
  font-family: monospace;
}

.success-text {
  color: #2f855a;
  white-space: pre-wrap;
}

.error-text {
  color: #c53030;
  font-weight: 500;
}

.text-result {
  color: var(--text-primary);
  white-space: pre-wrap;
}

.step-error {
  margin-top: 10px;
  color: #c53030;
  font-size: 13px;
  background: #fff5f5;
  padding: 8px;
  border-radius: 4px;
}

pre {
  background: var(--code-bg);
  padding: 8px;
  border-radius: 4px;
  overflow-x: auto;
  margin: 5px 0 0;
}
</style>
