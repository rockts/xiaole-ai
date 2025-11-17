<template>
  <div class="schedule-view">
    <div class="card">
      <h3>📅 课程表管理</h3>
      <div class="schedule-content">
        <div v-if="loading" class="loading">加载中...</div>
        <div v-else-if="!schedule || schedule.length === 0" class="empty">
          <p>暂无课程安排</p>
          <button @click="addSchedule" class="btn-primary">添加课程</button>
        </div>
        <div v-else class="schedule-grid">
          <div v-for="item in schedule" :key="item.id" class="schedule-item">
            <div class="schedule-day">{{ item.day }}</div>
            <div class="schedule-time">{{ item.time }}</div>
            <div class="schedule-course">{{ item.course }}</div>
            <div class="schedule-location">{{ item.location }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import api from "@/services/api";

const schedule = ref([]);
const loading = ref(false);

const loadSchedule = async () => {
  try {
    loading.value = true;
    const data = await api.getSchedule();
    schedule.value = data.schedule || [];
  } catch (error) {
    console.error("Failed to load schedule:", error);
  } finally {
    loading.value = false;
  }
};

const addSchedule = () => {
  // TODO: 实现添加课程功能
  alert("添加课程功能开发中...");
};

onMounted(() => {
  loadSchedule();
});
</script>

<style scoped>
.schedule-view {
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

.schedule-content {
  margin-top: 20px;
}

.empty {
  text-align: center;
  padding: 40px;
  color: var(--text-secondary);
}

.btn-primary {
  padding: 10px 24px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  margin-top: 16px;
}

.schedule-grid {
  display: grid;
  gap: 12px;
}

.schedule-item {
  padding: 16px;
  background: var(--input-bg);
  border-radius: 8px;
  display: grid;
  grid-template-columns: auto 1fr auto;
  gap: 12px;
  align-items: center;
}

.schedule-day {
  font-weight: 600;
  color: #667eea;
}

.schedule-time {
  color: var(--text-secondary);
  font-size: 14px;
}

.schedule-course {
  font-weight: 500;
}

.schedule-location {
  color: var(--text-secondary);
  font-size: 14px;
}

.loading {
  text-align: center;
  padding: 40px;
  color: var(--text-secondary);
}
</style>
