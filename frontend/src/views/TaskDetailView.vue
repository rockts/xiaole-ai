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

              <div v-if="step.action_params" class="step-params">
                <strong>参数:</strong>
                <pre>{{ formatJson(step.action_params) }}</pre>
              </div>

              <div v-if="step.result" class="step-result">
                <strong>结果:</strong>
                <div v-if="isJson(step.result)">
                  <div
                    v-if="getJson(step.result).success === false"
                    class="error-text"
                  >
                    ❌ {{ getJson(step.result).error || "执行失败" }}
                  </div>
                  <div v-else-if="getJson(step.result).data">
                    <pre class="result-text">{{
                      getJson(step.result).data
                    }}</pre>
                  </div>
                  <div v-else-if="getJson(step.result).message">
                    <div class="info-text">
                      {{ getJson(step.result).message }}
                    </div>
                  </div>
                  <div v-else>
                    <pre>{{ formatJson(step.result) }}</pre>
                  </div>
                </div>
                <div v-else>
                  <pre>{{ step.result }}</pre>
                </div>
              </div>

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
import { ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import api from "@/services/api";

const route = useRoute();
const router = useRouter();
const task = ref(null);
const steps = ref([]);
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

const loadTask = async () => {
  try {
    loading.value = true;
    const data = await api.getTask(route.params.id);
    if (data.success && data.task) {
      task.value = data.task;
      steps.value = data.steps || [];
    }
  } catch (error) {
    console.error("Failed to load task:", error);
  } finally {
    loading.value = false;
  }
};

const deleteTask = async () => {
  if (!confirm("确定要删除这个任务吗？")) return;

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

onMounted(() => {
  loadTask();
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

.step-params,
.step-result {
  margin-top: 10px;
  font-size: 13px;
}

.step-error {
  margin-top: 10px;
  color: #c53030;
  font-size: 13px;
}

pre {
  background: var(--code-bg);
  padding: 8px;
  border-radius: 4px;
  overflow-x: auto;
  margin: 5px 0 0;
}

.result-text {
  white-space: pre-wrap;
  font-family: inherit;
  background: transparent;
  padding: 0;
  margin: 0;
  color: var(--text-primary);
}

.error-text {
  color: #c53030;
  font-weight: 500;
}

.info-text {
  color: #2b6cb0;
}
</style>