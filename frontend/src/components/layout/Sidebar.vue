<template>
  <div
    class="sidebar"
    :class="{ collapsed: isCollapsed, 'mobile-open': isMobileOpen }"
  >
    <div class="sidebar-inner">
      <div class="sidebar-header">
        <div class="sidebar-logo">
          <svg class="sidebar-logo-icon" viewBox="0 0 48 48" aria-hidden="true">
            <circle
              cx="24"
              cy="24"
              r="22"
              stroke="currentColor"
              stroke-width="2"
              fill="none"
            />
            <path
              d="M12 20C12 14.477 16.477 10 22 10H26C31.523 10 36 14.477 36 20V24"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
            />
            <rect
              x="8"
              y="22"
              width="5"
              height="8"
              rx="2"
              fill="currentColor"
            />
            <rect
              x="35"
              y="22"
              width="5"
              height="8"
              rx="2"
              fill="currentColor"
            />
            <path
              d="M18 15C18 13 19.5 12 21 12C22 12 22.8 12.5 23 13.5C23.5 12.8 24.5 12 26 12C27.5 12 29 13 29 15C29 15.8 28.5 16.5 28 17C28.8 17.3 29.5 18 29.5 19C29.5 20.2 28.5 21 27 21H21C19.5 21 18.5 20.2 18.5 19C18.5 18 19.2 17.3 20 17C19.5 16.5 18 15.8 18 15Z"
              fill="currentColor"
            />
            <circle cx="19" cy="28" r="1.5" fill="currentColor" />
            <circle cx="29" cy="28" r="1.5" fill="currentColor" />
            <path
              d="M19 33C19 33 21 35 24 35C27 35 29 33 29 33"
              stroke="currentColor"
              stroke-width="1.5"
              stroke-linecap="round"
            />
          </svg>
          <span>小乐 AI</span>
        </div>
        <button
          class="sidebar-collapse-btn"
          @click="toggleCollapse"
          title="收起侧边栏"
        >
          <svg
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <line x1="3" y1="6" x2="21" y2="6"></line>
            <line x1="3" y1="12" x2="21" y2="12"></line>
            <line x1="3" y1="18" x2="21" y2="18"></line>
          </svg>
        </button>
      </div>

      <div class="sidebar-section">
        <button class="new-chat-btn" @click="newChat">
          <span>新对话</span>
        </button>
      </div>

      <div class="sidebar-section">
        <router-link
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          class="nav-item"
          active-class="active"
        >
          <span class="nav-icon" v-html="item.icon"></span>
          <span>{{ item.label }}</span>
        </router-link>
      </div>
    </div>

    <div class="sidebar-footer">
      <div class="section-header">历史对话</div>
      <div class="sessions-scroll">
        <div v-if="loading" class="loading">加载中...</div>
        <div v-else-if="sessions.length === 0" class="empty">暂无历史对话</div>
        <div
          v-else
          v-for="session in sessions"
          :key="session.id || session.session_id"
          class="session-item"
          :class="{
            active: currentSessionId === (session.id || session.session_id),
          }"
          @click="loadSession(session.id || session.session_id)"
        >
          <div class="session-title">{{ session.title || "未命名对话" }}</div>
          <div class="session-time">{{ formatTime(session.created_at) }}</div>
        </div>
      </div>
    </div>
  </div>
  <div
    class="sidebar-overlay"
    :class="{ active: isMobileOpen }"
    @click="closeMobile"
  ></div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRouter, useRoute } from "vue-router";
import { useChatStore } from "@/stores/chat";
import { storeToRefs } from "pinia";

const router = useRouter();
const route = useRoute();
const chatStore = useChatStore();
const { sessions, loading } = storeToRefs(chatStore);

const isCollapsed = ref(false);
const isMobileOpen = ref(false);

const currentSessionId = computed(() => route.params.sessionId);

const navItems = [
  {
    path: "/memory",
    label: "记忆",
    icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96.44 2.5 2.5 0 0 1-2.96-3.08 3 3 0 0 1-.34-5.58 2.5 2.5 0 0 1 1.32-4.24 2.5 2.5 0 0 1 1.98-3A2.5 2.5 0 0 1 9.5 2Z"/><path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96.44 2.5 2.5 0 0 0 2.96-3.08 3 3 0 0 0 .34-5.58 2.5 2.5 0 0 0-1.32-4.24 2.5 2.5 0 0 0-1.98-3A2.5 2.5 0 0 0 14.5 2Z"/></svg>',
  },
  {
    path: "/reminders",
    label: "提醒",
    icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>',
  },
  {
    path: "/tasks",
    label: "任务",
    icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 11 12 14 22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/></svg>',
  },
  {
    path: "/documents",
    label: "文档",
    icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>',
  },
  {
    path: "/schedule",
    label: "课程表",
    icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>',
  },
  {
    path: "/tools",
    label: "工具",
    icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/></svg>',
  },
  {
    path: "/settings",
    label: "设置",
    icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M12 1v6m0 6v6m0-12l-5.2-3m10.4 0L12 7m0 6l-5.2 3m10.4 0L12 13"/></svg>',
  },
];

const toggleCollapse = () => {
  if (window.innerWidth <= 768) {
    isMobileOpen.value = !isMobileOpen.value;
  } else {
    isCollapsed.value = !isCollapsed.value;
  }
};

const toggle = () => {
  toggleCollapse();
};

const closeMobile = () => {
  isMobileOpen.value = false;
};

const newChat = () => {
  chatStore.clearCurrentSession();
  router.push("/chat");
};

const loadSession = (sessionId) => {
  router.push(`/chat/${sessionId}`);
  if (window.innerWidth <= 768) {
    closeMobile();
  }
};

// 暴露toggle方法给父组件
defineExpose({
  toggle,
});

const formatTime = (timestamp) => {
  if (!timestamp) return "";
  const date = new Date(timestamp);
  const now = new Date();
  const diff = now - date;
  const days = Math.floor(diff / (1000 * 60 * 60 * 24));

  if (days === 0) return "今天";
  if (days === 1) return "昨天";
  if (days < 7) return `${days}天前`;
  return date.toLocaleDateString("zh-CN");
};

onMounted(() => {
  chatStore.loadSessions();
});
</script>
