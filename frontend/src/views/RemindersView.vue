<template>
  <div class="reminders-view">
    <div class="card">
      <h3>🔔 提醒管理</h3>
      <button @click="loadReminders">🔄 刷新</button>
      <div class="reminders-list">
        <div v-if="loading" class="loading">加载中...</div>
        <div v-else-if="reminders.length === 0" class="empty">暂无提醒</div>
        <div
          v-else
          v-for="reminder in reminders"
          :key="reminder.id"
          class="reminder-item"
        >
          <div>{{ reminder.title }}</div>
          <div>{{ reminder.trigger_time }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import api from "@/services/api";

const reminders = ref([]);
const loading = ref(false);

const loadReminders = async () => {
  try {
    loading.value = true;
    const data = await api.getReminders();
    reminders.value = data.reminders || [];
  } catch (error) {
    console.error("Failed to load reminders:", error);
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  loadReminders();
});
</script>

<style scoped>
.reminders-view {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.card {
  background: var(--card-bg);
  border-radius: 12px;
  padding: 20px;
}

.reminders-list {
  margin-top: 20px;
}

.reminder-item {
  padding: 15px;
  background: var(--input-bg);
  border-radius: 8px;
  margin-bottom: 10px;
}
</style>
