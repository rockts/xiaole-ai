// ...existing code...
<template>
  <div class="schedule-view">
    <div class="card">
      <h3>📅 课程表管理</h3>
      <div class="schedule-content">
        <div v-if="loading" class="loading">加载中...</div>
        <div v-else-if="!scheduleData || !scheduleData.weekdays" class="empty">
          <p>暂无课程安排</p>
          <button @click="addSchedule" class="btn-primary">添加课程</button>
        </div>
        <div v-else class="schedule-table-container">
          <table class="schedule-table">
            <thead>
              <tr>
                <th></th>
                <th v-for="day in scheduleData.weekdays" :key="day">
                  {{ day }}
                </th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(period, pIndex) in scheduleData.periods"
                :key="period"
              >
                <td class="period-cell">{{ period }}</td>
                <td
                  v-for="day in scheduleData.weekdays"
                  :key="day"
                  class="course-cell"
                >
                  <div class="course-content">
                    {{ getCourse(day, pIndex) }}
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import api from "@/services/api";

const scheduleData = ref(null);
const loading = ref(false);

const loadSchedule = async () => {
  try {
    loading.value = true;
    const data = await api.getSchedule();
    if (data.success && data.schedule) {
      scheduleData.value = data.schedule;
    }
  } catch (error) {
    console.error("Failed to load schedule:", error);
  } finally {
    loading.value = false;
  }
};

const getCourse = (day, periodIndex) => {
  if (!scheduleData.value || !scheduleData.value.courses) return "";
  // Backend key format: "periodIndex_day" (e.g. "0_周一")
  const key = `${periodIndex}_${day}`;
  return scheduleData.value.courses[key] || "";
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
  overflow-x: auto;
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

.schedule-table-container {
  overflow-x: auto;
}

.schedule-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 600px;
}

.schedule-table th,
.schedule-table td {
  border: 1px solid var(--border-light);
  padding: 12px;
  text-align: center;
}

.schedule-table th {
  background: var(--bg-secondary);
  font-weight: 600;
  color: var(--text-primary);
}

.period-cell {
  background: var(--bg-secondary);
  font-weight: 500;
  color: var(--text-secondary);
  width: 80px;
}

.course-cell {
  background: var(--bg-primary);
  height: 60px;
}

.course-content {
  font-size: 14px;
  color: var(--text-primary);
  font-weight: 500;
}

.loading {
  text-align: center;
  padding: 40px;
  color: var(--text-secondary);
}
</style>

