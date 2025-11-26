<template>
  <div class="app-layout">
    <SidebarModern v-if="authStore.isAuthenticated" ref="sidebarRef" />
    <div class="main-content">
      <TopBar
        v-if="authStore.isAuthenticated"
        @toggle-sidebar="handleToggleSidebar"
      />
      <div class="content-wrapper">
        <router-view v-slot="{ Component }">
          <transition name="page" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </div>
    </div>
    <ReminderNotification v-if="authStore.isAuthenticated" />
  </div>
</template>

<script setup>
import SidebarModern from "@/components/layout/SidebarModern.vue";
import TopBar from "@/components/layout/TopBar.vue";
import ReminderNotification from "@/components/common/ReminderNotification.vue";
import { ref, onMounted, watch } from "vue";
import { useWebSocket } from "@/composables/useWebSocket";
import { useAuthStore } from "@/stores/auth";

// Force rebuild comment
const authStore = useAuthStore();
const sidebarRef = ref(null);

const handleToggleSidebar = () => {
  if (sidebarRef.value) {
    sidebarRef.value.toggle();
  }
};

const { connect, disconnect } = useWebSocket();

onMounted(() => {
  if (authStore.isAuthenticated) {
    connect();
  }
});

watch(
  () => authStore.isAuthenticated,
  (isAuthenticated) => {
    if (isAuthenticated) {
      connect();
    } else {
      disconnect();
    }
  }
);
</script>

<style scoped>
.app-layout {
  display: flex;
  height: 100vh;
  overflow: hidden;
  background: var(--bg-primary);
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  overflow: hidden;
}

.content-wrapper {
  flex: 1;
  overflow: auto;
  background: var(--bg-secondary);
  /* 为移动设备添加底部安全区内边距 */
  padding-bottom: env(safe-area-inset-bottom);
  padding-bottom: constant(safe-area-inset-bottom);
}

@media (max-width: 768px) {
  .main-content {
    padding-top: 52px; /* 顶部栏固定后，所有页面都给内容留出空间 */
  }
  .content-wrapper {
    padding-top: 0;
  }
}
</style>
