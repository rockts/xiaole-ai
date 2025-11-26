<template>
  <div class="top-bar">
    <button
      class="mobile-menu-btn"
      @click="toggleSidebar"
      aria-label="打开菜单"
    >
      <svg
        width="24"
        height="24"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      >
        <line x1="3" y1="12" x2="21" y2="12"></line>
        <line x1="3" y1="6" x2="21" y2="6"></line>
        <line x1="3" y1="18" x2="21" y2="18"></line>
      </svg>
    </button>

    <div class="top-bar-center">
      <input
        v-if="isEditingTitle && isChatPage"
        ref="titleInput"
        v-model="editingTitle"
        class="title-input"
        @blur="saveTitleEdit"
        @keydown.enter="saveTitleEdit"
        @keydown.esc="cancelTitleEdit"
      />
      <span
        v-else
        class="page-title"
        :class="{ editable: isChatPage }"
        @dblclick="startEditTitle"
      >
        {{ pageTitle }}
      </span>
    </div>

    <div class="top-bar-right">
      <!-- 桌面端：保留主题切换和提醒；移动端：隐藏这些重复/次要功能 -->
      <button
        class="icon-btn"
        @click="toggleTheme"
        aria-label="切换主题"
        v-if="!isMobile"
      >
        <svg
          v-if="isDark"
          width="20"
          height="20"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
        >
          <circle cx="12" cy="12" r="5" />
          <line x1="12" y1="1" x2="12" y2="3" />
          <line x1="12" y1="21" x2="12" y2="23" />
          <line x1="4.22" y1="4.22" x2="5.64" y2="5.64" />
          <line x1="18.36" y1="18.36" x2="19.78" y2="19.78" />
          <line x1="1" y1="12" x2="3" y2="12" />
          <line x1="21" y1="12" x2="23" y2="12" />
          <line x1="4.22" y1="19.78" x2="5.64" y2="18.36" />
          <line x1="18.36" y1="5.64" x2="19.78" y2="4.22" />
        </svg>
        <svg
          v-else
          width="20"
          height="20"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
        >
          <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
        </svg>
      </button>

      <!-- 移动端：仅保留“分享”按钮（避免与侧边栏重复） -->
      <button
        v-if="isMobile && hasSharableSession"
        class="icon-btn"
        @click="shareCurrent"
        aria-label="分享当前对话"
      >
        <svg
          width="20"
          height="20"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
        >
          <circle cx="18" cy="5" r="3"></circle>
          <circle cx="6" cy="12" r="3"></circle>
          <circle cx="18" cy="19" r="3"></circle>
          <line x1="8.59" y1="13.51" x2="15.42" y2="17.49"></line>
          <line x1="15.41" y1="6.51" x2="8.59" y2="10.49"></line>
        </svg>
      </button>

      <!-- 提醒按钮：仅桌面端显示 -->
      <div class="reminder-container" v-if="!isMobile">
        <button
          class="icon-btn reminder-btn"
          @click="toggleReminders"
          aria-label="提醒"
        >
          <svg
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path>
            <path d="M13.73 21a2 2 0 0 1-3.46 0"></path>
          </svg>
          <span v-if="activeRemindersCount > 0" class="badge">{{
            activeRemindersCount
          }}</span>
        </button>

        <transition name="dropdown">
          <div v-if="showReminders" class="reminder-dropdown">
            <ReminderListPopup
              :reminders="reminders"
              :loading="loadingReminders"
              :time-remaining-map="timeRemainingMap"
              @close="closeReminders"
              @delete="handleDeleteReminder"
            />
          </div>
        </transition>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, onMounted, onBeforeUnmount, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useChatStore } from "@/stores/chat";
import { storeToRefs } from "pinia";
import api from "@/services/api";
import { useWebSocket } from "@/composables/useWebSocket";
import ReminderListPopup from "@/components/common/ReminderListPopup.vue";

const route = useRoute();
const router = useRouter();
const chatStore = useChatStore();
const { messages, currentSessionId } = storeToRefs(chatStore);
const emit = defineEmits(["toggle-sidebar"]);
// 移动端判断
const isMobile = ref(window.innerWidth <= 768);
const showMore = ref(false);
const moreBtnRef = ref(null);
const moreDropdownRef = ref(null);

const toggleMore = () => {
  showMore.value = !showMore.value;
};
const closeMore = () => {
  showMore.value = false;
};
const openSidebar = () => {
  emit("toggle-sidebar");
  closeMore();
};
const goto = (path) => {
  router.push(path);
  closeMore();
};

const shareCurrent = () => {
  const sessionId = route.params.sessionId;
  if (sessionId) {
    const url = `${window.location.origin}/share/${sessionId}`;
    window.open(url, "_blank");
    closeMore();
  } else {
    alert("当前没有可分享的对话");
  }
};

const isDark = ref(false);
const isEditingTitle = ref(false);
const editingTitle = ref("");
const titleInput = ref(null);

// 提醒相关状态
const showReminders = ref(false);
const reminders = ref([]);
const loadingReminders = ref(false);
const timeRemainingMap = ref({});
let timerInterval = null;

const activeRemindersCount = computed(() => reminders.value.length);

// 判断当前回话是否有可分享内容
const hasMessages = computed(() => (messages.value?.length || 0) > 0);
const hasSharableSession = computed(() => {
  if (!isChatPage.value) return false;
  const routeSessionId = route.params.sessionId;
  if (!routeSessionId) return false;
  if (currentSessionId.value && currentSessionId.value !== routeSessionId) {
    return false;
  }
  return hasMessages.value;
});

const toggleReminders = () => {
  showReminders.value = !showReminders.value;
  if (showReminders.value) {
    // 每次打开刷新一次，虽然有 websocket 自动更新
    loadReminders();
  }
};

const closeReminders = () => {
  showReminders.value = false;
};

const updateTimeRemaining = () => {
  const now = Date.now();
  const map = {};

  reminders.value.forEach((r) => {
    if (!r.enabled || r.reminder_type !== "time") return;

    let condition = r.trigger_condition;
    if (typeof condition === "string") {
      try {
        condition = JSON.parse(condition);
      } catch (e) {
        return;
      }
    }
    if (!condition || !condition.datetime) return;

    let nextTime = new Date(condition.datetime).getTime();

    if (r.repeat && r.repeat_interval) {
      const interval = r.repeat_interval * 1000;
      if (r.last_triggered) {
        const last = new Date(r.last_triggered).getTime();
        nextTime = last + interval;
      }
    }

    const diff = nextTime - now;
    if (diff < 0) {
      map[r.reminder_id] = "即将触发";
    } else {
      const seconds = Math.floor(diff / 1000);
      const minutes = Math.floor(seconds / 60);
      const hours = Math.floor(minutes / 60);
      const days = Math.floor(hours / 24);

      if (days > 0) {
        map[r.reminder_id] = `${days}天 ${hours % 24}小时后`;
      } else if (hours > 0) {
        map[r.reminder_id] = `${hours}小时 ${minutes % 60}分后`;
      } else if (minutes > 0) {
        map[r.reminder_id] = `${minutes}分钟后`;
      } else {
        map[r.reminder_id] = `${seconds}秒后`;
      }
    }
  });
  timeRemainingMap.value = map;
};

const loadReminders = async () => {
  try {
    loadingReminders.value = true;
    // 只获取启用的提醒
    const data = await api.getReminders("default_user", true);
    reminders.value = data.reminders || [];
    updateTimeRemaining();
  } catch (error) {
    console.error("Failed to load reminders:", error);
  } finally {
    loadingReminders.value = false;
  }
};

const handleDeleteReminder = async (id) => {
  try {
    await api.deleteReminder(id);
    reminders.value = reminders.value.filter((r) => r.reminder_id !== id);
  } catch (error) {
    console.error("Failed to delete reminder:", error);
    alert("删除失败");
  }
};

const isChatPage = computed(() => route.path.startsWith("/chat"));

const pageTitle = computed(() => {
  // 如果是聊天页面,显示当前会话标题
  if (isChatPage.value) {
    const sessionInfo = chatStore.sessionInfo;
    if (sessionInfo?.title) {
      return sessionInfo.title;
    }
    return "新对话";
  }
  return route.meta.title || "小乐 AI 管家";
});

const startEditTitle = () => {
  if (!isChatPage.value) return;
  isEditingTitle.value = true;
  editingTitle.value = pageTitle.value;
  setTimeout(() => {
    if (titleInput.value) {
      titleInput.value.focus();
      titleInput.value.select();
    }
  }, 0);
};

const saveTitleEdit = async () => {
  const newTitle = editingTitle.value.trim();
  if (!newTitle || newTitle === pageTitle.value) {
    isEditingTitle.value = false;
    return;
  }

  const sessionId = route.params.sessionId;
  if (!sessionId) {
    isEditingTitle.value = false;
    return;
  }

  try {
    await api.updateSession(sessionId, { title: newTitle });

    // 更新当前会话信息
    if (chatStore.sessionInfo) {
      chatStore.sessionInfo.title = newTitle;
    }
    // 重新加载会话列表以更新侧边栏
    await chatStore.loadSessions();
  } catch (error) {
    console.error("标题更新失败:", error);
  }

  isEditingTitle.value = false;
};

const cancelTitleEdit = () => {
  isEditingTitle.value = false;
  editingTitle.value = "";
};

const toggleSidebar = () => {
  emit("toggle-sidebar");
};

const toggleTheme = () => {
  isDark.value = !isDark.value;
  document.documentElement.setAttribute(
    "data-theme",
    isDark.value ? "dark" : "light"
  );
  localStorage.setItem("theme", isDark.value ? "dark" : "light");
};

const handleOutsideClick = (e) => {
  if (!e.target.closest(".reminder-container")) {
    showReminders.value = false;
  }
  // 点击到更多之外则关闭
  const inMore =
    e.target.closest &&
    (e.target.closest(".more-container") || e.target.closest(".more-dropdown"));
  if (!inMore) showMore.value = false;
};

const { on } = useWebSocket();
let wsUnsubscribe = null;

onMounted(() => {
  const onResize = () => {
    isMobile.value = window.innerWidth <= 768;
  };
  window.addEventListener("resize", onResize);
  window.__topbar_onResize = onResize;
  const savedTheme = localStorage.getItem("theme");
  isDark.value = savedTheme === "dark";
  document.documentElement.setAttribute("data-theme", savedTheme || "light");
  document.addEventListener("click", handleOutsideClick);

  // Reminders init
  loadReminders();
  timerInterval = setInterval(updateTimeRemaining, 1000);
  window.addEventListener("reminder-confirmed", loadReminders);
  window.addEventListener("refresh-reminders", loadReminders);

  wsUnsubscribe = on((data) => {
    if (data.type === "reminder_created" || data.type === "reminder_updated") {
      loadReminders();
    }
  });
});

// 同步网页标题为当前对话标题
const updateDocumentTitle = () => {
  if (isChatPage.value) {
    document.title = pageTitle.value || "新对话";
  } else {
    document.title = route.meta.title || "小乐 AI 管家";
  }
};

// 首次和后续变化都更新
watch(
  [() => route.fullPath, pageTitle, isChatPage],
  () => {
    updateDocumentTitle();
  },
  { immediate: true }
);

onBeforeUnmount(() => {
  document.removeEventListener("click", handleOutsideClick);
  window.removeEventListener("reminder-confirmed", loadReminders);
  window.removeEventListener("refresh-reminders", loadReminders);
  if (timerInterval) clearInterval(timerInterval);
  if (wsUnsubscribe) wsUnsubscribe();
  if (window.__topbar_onResize) {
    window.removeEventListener("resize", window.__topbar_onResize);
    delete window.__topbar_onResize;
  }
});
</script>

<style scoped>
.top-bar {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 52px;
  padding: 0 var(--space-lg);
  background: var(--bg-primary);
  border-bottom: 1px solid var(--border-light);
  position: sticky;
  top: 0;
  z-index: 100;
}

.mobile-menu-btn {
  display: none;
  position: absolute;
  left: var(--space-lg);
  background: transparent;
  border: none;
  padding: 0;
  color: var(--text-primary);
  cursor: pointer;
}

@media (max-width: 768px) {
  .mobile-menu-btn {
    display: flex;
  }

  .top-bar {
    padding: 0 var(--space-md);
    position: fixed;
    left: 0;
    right: 0;
    top: 0;
  }

  .mobile-menu-btn {
    left: var(--space-md);
  }

  .title-input {
    min-width: 100px;
    max-width: 160px;
    font-size: 14px;
    padding: 4px 8px;
  }

  .page-title {
    max-width: 180px;
    font-size: 14px;
    padding: 4px 8px;
  }
}

.top-bar-center {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
}

.page-title {
  font-size: 15px;
  font-weight: 500;
  color: var(--text-primary);
  padding: 6px 12px;
  border-radius: 6px;
  transition: background var(--duration-fast) var(--ease-out);
  /* 防止标题过长撑开 */
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 300px;
  text-align: center;
}

.page-title.editable {
  cursor: pointer;
}

.page-title.editable:hover {
  background: var(--bg-hover);
}

.title-input {
  font-size: 15px;
  font-weight: 500;
  color: var(--text-primary);
  background: var(--bg-secondary);
  border: 1px solid var(--border-medium);
  border-radius: 6px;
  padding: 6px 12px;
  outline: none;
  min-width: 200px;
  max-width: 400px;
  text-align: center;
}

.title-input:focus {
  border-color: var(--brand-primary);
  background: var(--bg-primary);
}

.top-bar-right {
  position: absolute;
  right: var(--space-lg);
  display: flex;
  align-items: center;
  gap: var(--space-md);
}

.more-container {
  position: relative;
}

.more-dropdown {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  min-width: 160px;
  background: var(--bg-primary);
  border: 1px solid var(--border-light);
  border-radius: 8px;
  box-shadow: var(--shadow-lg);
  padding: 6px;
  z-index: 1000;
}

.more-item {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 10px;
  background: transparent;
  border: none;
  color: var(--text-primary);
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}
.more-item:hover {
  background: var(--bg-hover);
}

.icon-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  padding: 0;
  background: transparent;
  border: none;
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease-out);
}

.icon-btn:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.reminder-container {
  position: relative;
}

.reminder-btn {
  position: relative;
}

.badge {
  position: absolute;
  top: -2px;
  right: -2px;
  background: var(--error);
  color: white;
  font-size: 10px;
  font-weight: bold;
  min-width: 16px;
  height: 16px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 4px;
  border: 2px solid var(--bg-primary);
}

.reminder-dropdown {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  z-index: 1000;
}

@media (max-width: 768px) {
  .reminder-dropdown {
    right: -60px;
  }
}
</style>
