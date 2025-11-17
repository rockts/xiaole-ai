<template>
  <div class="tools-view">
    <div class="card">
      <h3>🔧 工具管理</h3>
      <div class="tools-header">
        <button @click="loadTools" class="btn-refresh">🔄 刷新</button>
        <label class="filter-label">
          <input
            type="checkbox"
            v-model="showEnabledOnly"
            @change="loadTools"
          />
          只显示启用的工具
        </label>
      </div>

      <div class="tools-content">
        <div v-if="loading" class="loading">加载中...</div>
        <div v-else-if="tools.length === 0" class="empty">暂无工具</div>
        <div v-else class="tools-grid">
          <div v-for="tool in tools" :key="tool.name" class="tool-card">
            <div class="tool-header">
              <span class="tool-icon">{{ getToolIcon(tool.name) }}</span>
              <span class="tool-name">{{ tool.name }}</span>
              <span class="tool-status" :class="{ enabled: tool.enabled }">
                {{ tool.enabled ? "✓ 已启用" : "✗ 已禁用" }}
              </span>
            </div>
            <div class="tool-description">
              {{ tool.description || "暂无描述" }}
            </div>
          </div>
        </div>
      </div>

      <div class="card" style="margin-top: 20px">
        <h4>📊 工具使用历史</h4>
        <div class="history-list">
          <div v-if="historyLoading" class="loading">加载中...</div>
          <div v-else-if="history.length === 0" class="empty">暂无使用记录</div>
          <div
            v-else
            v-for="item in history"
            :key="item.id"
            class="history-item"
          >
            <div class="history-tool">{{ item.tool_name }}</div>
            <div class="history-time">{{ formatTime(item.created_at) }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import api from "@/services/api";

const tools = ref([]);
const history = ref([]);
const loading = ref(false);
const historyLoading = ref(false);
const showEnabledOnly = ref(true);

const loadTools = async () => {
  try {
    loading.value = true;
    const data = await api.getTools(showEnabledOnly.value);
    tools.value = data.tools || [];
  } catch (error) {
    console.error("Failed to load tools:", error);
  } finally {
    loading.value = false;
  }
};

const loadHistory = async () => {
  try {
    historyLoading.value = true;
    const data = await api.getToolHistory();
    history.value = data.history || [];
  } catch (error) {
    console.error("Failed to load history:", error);
  } finally {
    historyLoading.value = false;
  }
};

const getToolIcon = (name) => {
  const icons = {
    search: "🔍",
    time: "⏰",
    weather: "🌤️",
    file: "📁",
    calculator: "🔢",
    system: "💻",
  };
  return icons[name] || "🔧";
};

const formatTime = (time) => {
  return new Date(time).toLocaleString("zh-CN");
};

onMounted(() => {
  loadTools();
  loadHistory();
});
</script>

<style scoped>
.tools-view {
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

.tools-header {
  display: flex;
  gap: 16px;
  align-items: center;
  margin: 16px 0;
}

.btn-refresh {
  padding: 8px 16px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.filter-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.tools-content {
  margin-top: 20px;
}

.tools-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}

.tool-card {
  padding: 16px;
  background: var(--input-bg);
  border-radius: 8px;
  transition: transform 0.2s;
}

.tool-card:hover {
  transform: translateY(-2px);
}

.tool-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.tool-icon {
  font-size: 20px;
}

.tool-name {
  font-weight: 600;
  flex: 1;
}

.tool-status {
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 4px;
  background: #e0e0e0;
}

.tool-status.enabled {
  background: #4caf50;
  color: white;
}

.tool-description {
  color: var(--text-secondary);
  font-size: 14px;
}

.history-list {
  margin-top: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.history-item {
  padding: 12px;
  background: var(--input-bg);
  border-radius: 6px;
  display: flex;
  justify-content: space-between;
}

.history-tool {
  font-weight: 500;
}

.history-time {
  color: var(--text-secondary);
  font-size: 12px;
}

.loading,
.empty {
  text-align: center;
  padding: 40px;
  color: var(--text-secondary);
}
</style>
