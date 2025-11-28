<template>
  <div class="loading-view">
    <div class="loading-spinner">
      <div class="spinner"></div>
      <p>{{ message }}</p>
      <button v-if="showRetry" @click="handleRetry" class="retry-btn">
        重试
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";

const props = defineProps({
  timeout: {
    type: Number,
    default: 10000,
  },
});

const message = ref("加载中...");
const showRetry = ref(false);

let timer = null;

onMounted(() => {
  timer = setTimeout(() => {
    message.value = "加载时间过长";
    showRetry.value = true;
  }, props.timeout);
});

const handleRetry = () => {
  window.location.reload();
};
</script>

<style scoped>
.loading-view {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: var(--bg-primary);
}

.loading-spinner {
  text-align: center;
  color: var(--text-secondary);
}

.spinner {
  width: 40px;
  height: 40px;
  margin: 0 auto 20px;
  border: 4px solid var(--border-light);
  border-top-color: var(--primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.retry-btn {
  margin-top: 20px;
  padding: 10px 24px;
  background: var(--primary);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}

.retry-btn:hover {
  opacity: 0.9;
}
</style>
