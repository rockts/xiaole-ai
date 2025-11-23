<template>
  <div class="behavior-container">
    <header class="page-header">
      <h1>行为分析</h1>
      <div class="header-actions">
        <select v-model="days" @change="fetchData" class="time-select">
          <option :value="7">最近7天</option>
          <option :value="30">最近30天</option>
          <option :value="90">最近90天</option>
        </select>
        <button @click="fetchData" class="refresh-btn" :disabled="loading">
          <span v-if="loading">加载中...</span>
          <span v-else>刷新</span>
        </button>
      </div>
    </header>

    <div v-if="error" class="error-message">
      {{ error }}
    </div>

    <div v-else-if="loading && !report" class="loading-state">
      <div class="spinner"></div>
      <p>正在分析您的行为数据...</p>
    </div>

    <div v-else-if="report" class="dashboard-grid">
      <!-- 核心指标卡片 -->
      <div class="stats-cards">
        <div class="stat-card">
          <div class="stat-label">总会话数</div>
          <div class="stat-value">
            {{ report.conversation_stats.total_sessions }}
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-label">总消息数</div>
          <div class="stat-value">
            {{ report.conversation_stats.total_messages }}
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-label">平均对话时长</div>
          <div class="stat-value">
            {{ report.conversation_stats.avg_duration_per_session_minutes }}
            <span class="unit">分钟</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-label">平均消息长度</div>
          <div class="stat-value">
            {{ report.conversation_stats.avg_message_length }}
            <span class="unit">字</span>
          </div>
        </div>
      </div>

      <!-- 活跃时间分布 -->
      <div class="chart-section">
        <h2>活跃时间分布</h2>
        <div class="activity-grid">
          <div class="activity-chart">
            <h3>时段分布 (24小时)</h3>
            <div class="bar-chart">
              <div
                v-for="(count, hour) in sortedHourly"
                :key="hour"
                class="bar-item"
              >
                <div class="bar-track">
                  <div
                    class="bar-fill"
                    :style="{ height: getBarHeight(count, maxHourly) + '%' }"
                  ></div>
                </div>
                <div class="bar-label">{{ hour }}点</div>
              </div>
            </div>
          </div>
          <div class="activity-summary">
            <div class="summary-item">
              <span class="label">最活跃时段</span>
              <span class="value"
                >{{ report.activity_pattern.most_active_hour }}点</span
              >
            </div>
            <div class="summary-item">
              <span class="label">最活跃日子</span>
              <span class="value">{{
                report.activity_pattern.most_active_day
              }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 话题偏好 -->
      <div class="topics-section">
        <h2>话题偏好</h2>
        <div class="topics-cloud">
          <div
            v-for="(topic, index) in report.topic_preferences.top_topics"
            :key="index"
            class="topic-tag"
            :style="{
              fontSize: getTopicSize(topic[1]) + 'px',
              opacity: getTopicOpacity(topic[1]),
            }"
          >
            {{ topic[0] }}
            <span class="topic-count">{{ topic[1] }}</span>
          </div>
        </div>
        <div
          v-if="report.topic_preferences.top_topics.length === 0"
          class="empty-topics"
        >
          暂无足够的话题数据
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from "vue";
import axios from "axios";

const days = ref(30);
const loading = ref(false);
const error = ref(null);
const report = ref(null);

// 计算属性：排序后的小时数据
const sortedHourly = computed(() => {
  if (!report.value?.activity_pattern?.hourly_distribution) return {};
  const dist = report.value.activity_pattern.hourly_distribution;
  // 补全0-23小时
  const result = {};
  for (let i = 0; i < 24; i++) {
    result[i] = dist[i] || 0;
  }
  return result;
});

// 计算最大值用于归一化图表高度
const maxHourly = computed(() => {
  if (!report.value?.activity_pattern?.hourly_distribution) return 1;
  const values = Object.values(
    report.value.activity_pattern.hourly_distribution
  );
  return Math.max(...values, 1); // 避免除以0
});

const getBarHeight = (val, max) => {
  return Math.round((val / max) * 100);
};

const getTopicSize = (count) => {
  // 简单的字号映射：12px - 24px
  const max = report.value.topic_preferences.top_topics[0]?.[1] || 1;
  const min = 12;
  const scale = 12;
  return min + (count / max) * scale;
};

const getTopicOpacity = (count) => {
  const max = report.value.topic_preferences.top_topics[0]?.[1] || 1;
  return 0.5 + (count / max) * 0.5;
};

const fetchData = async () => {
  loading.value = true;
  error.value = null;
  try {
    // 使用相对路径，通过 Vite 代理转发
    const response = await axios.get(`/analytics/behavior?days=${days.value}`);
    report.value = response.data;
  } catch (err) {
    console.error("Failed to fetch behavior data:", err);
    error.value = "无法加载行为分析数据，请稍后再试。";
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  fetchData();
});
</script>

<style scoped>
.behavior-container {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
  color: #e0e0e0;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.page-header h1 {
  font-size: 1.8rem;
  font-weight: 600;
  color: #fff;
}

.header-actions {
  display: flex;
  gap: 1rem;
}

.time-select {
  padding: 0.5rem 1rem;
  border-radius: 8px;
  background: #2d2d2d;
  border: 1px solid #404040;
  color: #fff;
  cursor: pointer;
}

.refresh-btn {
  padding: 0.5rem 1.5rem;
  border-radius: 8px;
  background: #4caf50;
  border: none;
  color: white;
  cursor: pointer;
  transition: background 0.2s;
}

.refresh-btn:hover {
  background: #45a049;
}

.refresh-btn:disabled {
  background: #404040;
  cursor: not-allowed;
}

.dashboard-grid {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

/* 统计卡片 */
.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
}

.stat-card {
  background: #1e1e1e;
  padding: 1.5rem;
  border-radius: 12px;
  border: 1px solid #333;
  text-align: center;
}

.stat-label {
  color: #888;
  font-size: 0.9rem;
  margin-bottom: 0.5rem;
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  color: #4caf50;
}

.unit {
  font-size: 1rem;
  color: #666;
  font-weight: normal;
}

/* 图表区域 */
.chart-section,
.topics-section {
  background: #1e1e1e;
  padding: 1.5rem;
  border-radius: 12px;
  border: 1px solid #333;
}

h2 {
  font-size: 1.2rem;
  margin-bottom: 1.5rem;
  color: #ccc;
  border-left: 4px solid #4caf50;
  padding-left: 1rem;
}

.activity-grid {
  display: flex;
  gap: 2rem;
}

.activity-chart {
  flex: 1;
}

.bar-chart {
  display: flex;
  align-items: flex-end;
  height: 200px;
  gap: 4px;
  padding-top: 20px;
}

.bar-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  height: 100%;
}

.bar-track {
  flex: 1;
  width: 100%;
  background: #2d2d2d;
  border-radius: 4px;
  position: relative;
  display: flex;
  align-items: flex-end;
}

.bar-fill {
  width: 100%;
  background: #4caf50;
  border-radius: 4px;
  transition: height 0.3s ease;
  min-height: 2px;
}

.bar-label {
  font-size: 0.7rem;
  color: #666;
  margin-top: 4px;
  transform: scale(0.8);
}

.activity-summary {
  width: 200px;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  justify-content: center;
  border-left: 1px solid #333;
  padding-left: 2rem;
}

.summary-item {
  display: flex;
  flex-direction: column;
}

.summary-item .label {
  color: #888;
  font-size: 0.9rem;
}

.summary-item .value {
  font-size: 1.5rem;
  color: #fff;
  font-weight: 600;
}

/* 话题云 */
.topics-cloud {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  padding: 1rem;
}

.topic-tag {
  background: #2d2d2d;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  color: #fff;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: transform 0.2s;
}

.topic-tag:hover {
  transform: scale(1.05);
  background: #3d3d3d;
}

.topic-count {
  background: rgba(255, 255, 255, 0.1);
  padding: 2px 6px;
  border-radius: 10px;
  font-size: 0.8em;
}

.empty-topics {
  text-align: center;
  color: #666;
  padding: 2rem;
}

.error-message {
  background: rgba(244, 67, 54, 0.1);
  color: #f44336;
  padding: 1rem;
  border-radius: 8px;
  text-align: center;
}

.loading-state {
  text-align: center;
  padding: 4rem;
  color: #888;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #333;
  border-top-color: #4caf50;
  border-radius: 50%;
  margin: 0 auto 1rem;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 768px) {
  .activity-grid {
    flex-direction: column;
  }

  .activity-summary {
    width: 100%;
    border-left: none;
    border-top: 1px solid #333;
    padding-left: 0;
    padding-top: 1rem;
    flex-direction: row;
    justify-content: space-around;
  }

  .bar-label {
    display: none; /* 移动端隐藏密集标签 */
  }

  .bar-item:nth-child(4n + 1) .bar-label {
    display: block; /* 每4个显示一个 */
  }
}
</style>
