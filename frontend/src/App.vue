<template>
  <div class="app-layout">
    <SidebarModern ref="sidebarRef" />
    <div class="main-content">
      <TopBar @toggle-sidebar="handleToggleSidebar" />
      <div class="content-wrapper">
        <router-view v-slot="{ Component }">
          <transition name="page" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </div>
    </div>
  </div>
</template>

<script setup>
import SidebarModern from "@/components/layout/SidebarModern.vue";
import TopBar from "@/components/layout/TopBar.vue";
import { ref, onMounted } from "vue";
import { useWebSocket } from "@/composables/useWebSocket";

const sidebarRef = ref(null);

const handleToggleSidebar = () => {
  if (sidebarRef.value) {
    sidebarRef.value.toggle();
  }
};

const { connect } = useWebSocket();

onMounted(() => {
  connect();
});
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
}
</style>
