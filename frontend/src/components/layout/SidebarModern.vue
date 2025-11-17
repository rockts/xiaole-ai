<template>
  <div class="sidebar" :class="{ collapsed: isCollapsed }">
    <div class="sidebar-content">
      <!-- 顶部：logo + 标题 + 收起按钮 -->
      <div class="sidebar-logo-title">
        <div
          class="logo-wrapper"
          :class="{ 'show-toggle': isCollapsed }"
          @click="isCollapsed && toggleSidebar()"
          :title="isCollapsed ? '展开侧边栏' : ''"
        >
          <div class="logo">
            <img
              v-if="!showFallbackLogo"
              :src="logoSrc"
              alt="小乐logo"
              @error="onLogoError"
            />
            <div v-else class="logo-fallback">乐</div>
          </div>
          <svg
            v-if="isCollapsed"
            class="toggle-icon"
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <rect x="3" y="3" width="18" height="18" rx="4" ry="4"></rect>
            <line x1="15" y1="3" x2="15" y2="21"></line>
          </svg>
        </div>
        <div class="title">小乐 AI 管家</div>
        <button class="collapse-btn" @click="toggleSidebar" title="收起侧边栏">
          <svg
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <rect x="3" y="3" width="18" height="18" rx="4" ry="4"></rect>
            <line x1="9" y1="3" x2="9" y2="21"></line>
          </svg>
        </button>
      </div>

      <!-- 主导航：新对话 + 功能入口 -->
      <nav class="sidebar-nav">
        <router-link
          to="/chat"
          class="nav-item"
          :class="{ active: isActive('/chat') }"
        >
          <span class="nav-icon">
            <svg
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            >
              <line x1="12" y1="5" x2="12" y2="19"></line>
              <line x1="5" y1="12" x2="19" y2="12"></line>
            </svg>
          </span>
          <span class="nav-label">新对话</span>
        </router-link>

        <router-link
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          class="nav-item"
          :class="{ active: isActive(item.path) }"
        >
          <span class="nav-icon" v-html="item.icon"></span>
          <span class="nav-label">{{ item.label }}</span>
        </router-link>
      </nav>

      <!-- 最近对话列表 -->
      <div class="sessions-section">
        <div class="section-header">
          <span>历史对话</span>
        </div>

        <div class="sessions-list" @scroll="handleScroll">
          <div v-if="loading && sessions.length === 0" class="loading-skeleton">
            <div class="skeleton-item" v-for="i in 3" :key="i"></div>
          </div>

          <div v-else-if="sessions.length === 0" class="empty-state-sm">
            <svg
              width="32"
              height="32"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="1.5"
            >
              <path
                d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"
              ></path>
            </svg>
            <p>暂无对话</p>
          </div>

          <div v-else>
            <div
              v-for="session in displayedSessions"
              :key="session.id || session.session_id"
              class="session-item"
              :class="{
                active: isCurrentSession(session),
                pinned: session.pinned,
              }"
              @click="loadSession(session.id || session.session_id)"
              @mouseenter="hoveredSessionId = session.id || session.session_id"
              @mouseleave="hoveredSessionId = null"
            >
              <svg
                v-if="session.pinned"
                class="pin-icon"
                width="12"
                height="12"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
              >
                <path
                  d="M12 17v5M9 10.76a2 2 0 0 1-1.11 1.79l-1.78.9A2 2 0 0 0 5 15.24V16a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-.76a2 2 0 0 0-1.11-1.79l-1.78-.9A2 2 0 0 1 15 10.76V7a1 1 0 0 1 1-1 2 2 0 0 0 0-4H8a2 2 0 0 0 0 4 1 1 0 0 1 1 1z"
                ></path>
              </svg>
              <div class="session-content">
                <input
                  v-if="editingSessionId === (session.id || session.session_id)"
                  v-model="editingTitle"
                  class="session-title-input"
                  @keydown.enter="saveRename(session.id || session.session_id)"
                  @keydown.esc="cancelRename"
                  @blur="saveRename(session.id || session.session_id)"
                  @click.stop
                />
                <div v-else class="session-title">
                  {{ session.title || "未命名对话" }}
                </div>
              </div>
              <button
                v-if="hoveredSessionId === (session.id || session.session_id)"
                class="session-menu-btn"
                @click.stop="
                  toggleSessionMenu(session.id || session.session_id)
                "
              >
                <svg
                  width="14"
                  height="14"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <circle cx="5" cy="12" r="1"></circle>
                  <circle cx="12" cy="12" r="1"></circle>
                  <circle cx="19" cy="12" r="1"></circle>
                </svg>
              </button>

              <!-- 菜单弹出层 -->
              <div
                v-if="
                  activeMenuSessionId === (session.id || session.session_id)
                "
                class="session-menu"
                @click.stop
              >
                <button
                  class="menu-item"
                  @click="renameSession(session.id || session.session_id)"
                >
                  <svg
                    width="14"
                    height="14"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                  >
                    <path
                      d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"
                    ></path>
                    <path
                      d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"
                    ></path>
                  </svg>
                  重命名
                </button>
                <button
                  class="menu-item"
                  @click="shareSession(session.id || session.session_id)"
                >
                  <svg
                    width="14"
                    height="14"
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
                  分享
                </button>
                <button
                  class="menu-item"
                  @click="pinSession(session.id || session.session_id)"
                >
                  <svg
                    width="14"
                    height="14"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                  >
                    <path
                      d="M12 17v5M9 10.76a2 2 0 0 1-1.11 1.79l-1.78.9A2 2 0 0 0 5 15.24V16a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-.76a2 2 0 0 0-1.11-1.79l-1.78-.9A2 2 0 0 1 15 10.76V7a1 1 0 0 1 1-1 2 2 0 0 0 0-4H8a2 2 0 0 0 0 4 1 1 0 0 1 1 1z"
                    ></path>
                  </svg>
                  {{ session.pinned ? "取消置顶" : "置顶" }}
                </button>
                <button
                  class="menu-item danger"
                  @click="confirmDelete(session.id || session.session_id)"
                >
                  <svg
                    width="14"
                    height="14"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                  >
                    <polyline points="3 6 5 6 21 6"></polyline>
                    <path
                      d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"
                    ></path>
                  </svg>
                  删除
                </button>
              </div>
            </div>

            <div v-if="loading && sessions.length > 0" class="loading-more">
              加载中...
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 删除确认对话框 -->
    <div v-if="showDeleteConfirm" class="modal-overlay" @click="cancelDelete">
      <div class="confirm-dialog" @click.stop>
        <h3 class="confirm-title">永久删除对话</h3>
        <p class="confirm-message">删除后，该对话将不可恢复。确认删除吗？</p>
        <div class="confirm-actions">
          <button class="btn-cancel" @click="cancelDelete">取消</button>
          <button class="btn-delete" @click="deleteSession">删除</button>
        </div>
      </div>
    </div>

    <!-- 底部：设置按钮 -->
    <div class="sidebar-footer">
      <button class="settings-btn" @click="goToSettings">
        <svg
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
        >
          <circle cx="12" cy="12" r="3"></circle>
          <path
            d="M12 1v6m0 6v6M3.93 3.93l4.24 4.24m8.48 8.48l4.24 4.24M1 12h6m6 0h6M3.93 20.07l4.24-4.24m8.48-8.48l4.24-4.24"
          ></path>
        </svg>
        <span>设置</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, nextTick } from "vue";
import { useRouter, useRoute } from "vue-router";
import { useChatStore } from "@/stores/chat";
import { storeToRefs } from "pinia";
import logoImage from "@/assets/logo-xiaole.png";

const router = useRouter();
const route = useRoute();
const chatStore = useChatStore();
const { sessions, loading } = storeToRefs(chatStore);

// 使用新的 logo
const logoSrc = computed(() => logoImage);
const isCollapsed = ref(false);
const showFallbackLogo = ref(false);
const onLogoError = () => {
  showFallbackLogo.value = true;
};

const navItems = [
  {
    path: "/memory",
    label: "记忆",
    icon: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" xmlns="http://www.w3.org/2000/svg"><path d="M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z"></path></svg>',
  },
  {
    path: "/reminders",
    label: "提醒",
    icon: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" xmlns="http://www.w3.org/2000/svg"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path><path d="M13.73 21a2 2 0 0 1-3.46 0"></path></svg>',
  },
  {
    path: "/tasks",
    label: "任务",
    icon: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" xmlns="http://www.w3.org/2000/svg"><polyline points="9 11 12 14 22 4"></polyline><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"></path></svg>',
  },
  {
    path: "/documents",
    label: "文档",
    icon: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" xmlns="http://www.w3.org/2000/svg"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline></svg>',
  },
  {
    path: "/schedule",
    label: "课程表",
    icon: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" xmlns="http://www.w3.org/2000/svg"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>',
  },
  {
    path: "/tools",
    label: "工具",
    icon: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" xmlns="http://www.w3.org/2000/svg"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"></path></svg>',
  },
];

const isActive = (path) => route.path.startsWith(path);
const isCurrentSession = (session) =>
  route.params.sessionId == (session.id || session.session_id);
const newChat = () => router.push("/chat");
const loadSession = (id) => router.push(`/chat/${id}`);
const goToSettings = () => router.push("/settings");

// 悬停和菜单状态
const hoveredSessionId = ref(null);
const activeMenuSessionId = ref(null);
const editingSessionId = ref(null);
const editingTitle = ref("");
const showDeleteConfirm = ref(false);
const deletingSessionId = ref(null);

// 分页加载
const pageSize = 20;
const currentPage = ref(1);
const displayedSessions = computed(() => {
  // 将置顶的会话排在前面
  const sorted = [...sessions.value].sort((a, b) => {
    const aPinned = a.pinned || false;
    const bPinned = b.pinned || false;
    if (aPinned && !bPinned) return -1;
    if (!aPinned && bPinned) return 1;
    return 0;
  });
  return sorted.slice(0, currentPage.value * pageSize);
});

const handleScroll = (e) => {
  const { scrollTop, scrollHeight, clientHeight } = e.target;
  if (scrollHeight - scrollTop - clientHeight < 50) {
    if (displayedSessions.value.length < sessions.value.length) {
      currentPage.value++;
    }
  }
};

const toggleSessionMenu = (id) => {
  if (activeMenuSessionId.value === id) {
    activeMenuSessionId.value = null;
  } else {
    activeMenuSessionId.value = id;
  }
};

const startRenaming = (session) => {
  activeMenuSessionId.value = null;
  editingSessionId.value = session.id || session.session_id;
  editingTitle.value = session.title || "未命名对话";
  // 等待DOM更新后聚焦输入框
  nextTick(() => {
    const input = document.querySelector(".session-title-input");
    if (input) {
      input.focus();
      input.select();
    }
  });
};

const saveRename = async (id) => {
  const newTitle = editingTitle.value.trim();
  if (
    !newTitle ||
    newTitle ===
      sessions.value.find((s) => (s.id || s.session_id) === id)?.title
  ) {
    cancelRename();
    return;
  }

  try {
    const response = await fetch(`/api/chat/sessions/${id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title: newTitle }),
    });

    if (response.ok) {
      const session = sessions.value.find((s) => (s.id || s.session_id) === id);
      if (session) {
        session.title = newTitle;
      }
      if (
        chatStore.sessionInfo &&
        (chatStore.sessionInfo.id === id ||
          chatStore.sessionInfo.session_id === id)
      ) {
        chatStore.sessionInfo.title = newTitle;
      }
      cancelRename();
    } else {
      console.error("重命名失败:", await response.text());
      alert("重命名失败,请重试");
      cancelRename();
    }
  } catch (error) {
    console.error("重命名失败:", error);
    alert("重命名失败,请重试");
    cancelRename();
  }
};

const cancelRename = () => {
  editingSessionId.value = null;
  editingTitle.value = "";
};

const renameSession = async (id) => {
  const session = sessions.value.find((s) => (s.id || s.session_id) === id);
  if (!session) return;
  startRenaming(session);
};

const shareSession = async (id) => {
  activeMenuSessionId.value = null;
  try {
    // 生成分享链接
    const shareUrl = `${window.location.origin}/share/${id}`;

    // 尝试使用现代剪贴板API
    if (navigator.clipboard && navigator.clipboard.writeText) {
      await navigator.clipboard.writeText(shareUrl);
      alert("分享链接已复制到剪贴板!");
    } else {
      // 降级方案
      const textarea = document.createElement("textarea");
      textarea.value = shareUrl;
      textarea.style.position = "fixed";
      textarea.style.opacity = "0";
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand("copy");
      document.body.removeChild(textarea);
      alert("分享链接已复制到剪贴板!");
    }
  } catch (error) {
    console.error("分享失败:", error);
    alert("分享失败,请重试");
  }
};

const pinSession = async (id) => {
  activeMenuSessionId.value = null;
  const session = sessions.value.find((s) => (s.id || s.session_id) === id);
  if (!session) return;

  try {
    // 切换置顶状态
    const isPinned = session.pinned || false;
    const response = await fetch(`/api/chat/sessions/${id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ pinned: !isPinned }),
    });

    if (response.ok) {
      session.pinned = !isPinned;
      // 重新排序会话列表,置顶的会话排在前面
      await chatStore.loadSessions(true);
    } else {
      alert(isPinned ? "取消置顶失败" : "置顶失败");
    }
  } catch (error) {
    console.error("置顶操作失败:", error);
    alert("操作失败,请重试");
  }
};

const confirmDelete = (id) => {
  activeMenuSessionId.value = null;
  deletingSessionId.value = id;
  showDeleteConfirm.value = true;
};

const cancelDelete = () => {
  showDeleteConfirm.value = false;
  deletingSessionId.value = null;
};

const deleteSession = async () => {
  const id = deletingSessionId.value;
  showDeleteConfirm.value = false;

  if (!id) return;

  try {
    const response = await fetch(`/api/chat/sessions/${id}`, {
      method: "DELETE",
    });

    if (response.ok) {
      // 从列表中移除
      const index = sessions.value.findIndex(
        (s) => (s.id || s.session_id) === id
      );
      if (index > -1) {
        sessions.value.splice(index, 1);
      }

      // 如果删除的是当前会话,跳转到新对话
      if (route.params.sessionId == id) {
        router.push("/chat");
      }
    } else {
      alert("删除失败,请重试");
    }
  } catch (error) {
    console.error("删除失败:", error);
    alert("删除失败,请重试");
  }
};

const toggleSidebar = () => {
  isCollapsed.value = !isCollapsed.value;
};

const toggle = () => {
  isCollapsed.value = !isCollapsed.value;
};
defineExpose({ toggle });
onMounted(() => {
  chatStore.loadSessions();
});
</script>

<style scoped>
.sidebar {
  display: flex;
  flex-direction: column;
  width: 260px;
  height: 100vh;
  background: var(--bg-primary);
  border-right: 1px solid var(--border-light);
  transition: width var(--duration-normal) var(--ease-out);
}

.sidebar.collapsed {
  width: 70px;
}

.sidebar-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: var(--space-sm);
  gap: var(--space-sm);
  min-height: 0;
}

.sidebar-logo-title {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-sm) var(--space-md);
}

.logo-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.logo-wrapper.show-toggle {
  cursor: pointer;
}

.logo-wrapper .toggle-icon {
  position: absolute;
  opacity: 0;
  transition: opacity var(--duration-fast) var(--ease-out);
  pointer-events: none;
}

.logo-wrapper.show-toggle:hover .logo {
  opacity: 0;
}

.logo-wrapper.show-toggle:hover .toggle-icon {
  opacity: 1;
}

.collapse-btn {
  margin-left: auto;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: transparent;
  color: var(--text-tertiary);
  cursor: pointer;
  border-radius: 6px;
  transition: all var(--duration-fast) var(--ease-out);
}

.collapse-btn:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.sidebar.collapsed .title,
.sidebar.collapsed .collapse-btn,
.sidebar.collapsed .nav-label,
.sidebar.collapsed .sessions-section,
.sidebar.collapsed .sidebar-footer span {
  display: none;
}

.sidebar.collapsed .sidebar-logo-title {
  justify-content: center;
  padding: var(--space-sm);
}

.sidebar.collapsed .nav-item {
  justify-content: center;
  padding: 10px;
}

.sidebar.collapsed .settings-btn {
  justify-content: center;
  padding: 12px;
}

.logo img {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: transparent;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  object-fit: contain;
  transition: filter var(--duration-fast) var(--ease-out);
}

[data-theme="dark"] .logo img {
  /* 深色主题下显示白色线条 */
  filter: brightness(0) invert(1);
}

[data-theme="light"] .logo img {
  /* 浅色主题下显示深色线条 */
  filter: brightness(0);
}

.logo-fallback {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--brand-primary);
  color: var(--text-inverse);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
}

.title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: 10px var(--space-md);
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  text-decoration: none;
  transition: background var(--duration-fast) var(--ease-out),
    color var(--duration-fast) var(--ease-out);
}

.nav-item:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}
.nav-item.active {
  background: var(--bg-active);
  color: var(--text-primary);
}
.nav-icon {
  display: inline-flex;
  color: var(--text-tertiary);
}
:deep(.nav-icon svg) {
  width: 16px;
  height: 16px;
  stroke: currentColor;
  fill: none;
  flex-shrink: 0;
  display: inline-block;
}
.nav-item.active .nav-icon {
  color: var(--text-primary);
}
.nav-label {
  font-size: 13px;
}

.sessions-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
  gap: var(--space-xs);
  margin-top: var(--space-md);
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-xs) var(--space-md);
  font-size: 11px;
  font-weight: 600;
  color: var(--text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.icon-btn-sm {
  display: flex;
  width: 20px;
  height: 20px;
  padding: 0;
  background: transparent;
  border: none;
  border-radius: var(--radius-sm);
  color: var(--text-tertiary);
  cursor: pointer;
}
.icon-btn-sm:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.sessions-list {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.session-item {
  position: relative;
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  padding: 10px var(--space-md);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: background var(--duration-fast) var(--ease-out);
}
.session-item:hover {
  background: var(--bg-hover);
}
.session-item.active {
  background: var(--bg-active);
}
.session-item.pinned {
  background: var(--bg-secondary);
}

.pin-icon {
  flex-shrink: 0;
  color: var(--brand-primary);
  opacity: 0.7;
}

.session-content {
  flex: 1;
  min-width: 0;
}
.session-title {
  font-size: 13px;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.session-title-input {
  width: 100%;
  font-size: 13px;
  color: var(--text-primary);
  background: var(--bg-primary);
  border: 1px solid var(--brand-primary);
  border-radius: 4px;
  padding: 2px 6px;
  outline: none;
}

.session-menu-btn {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  padding: 0;
  background: transparent;
  border: none;
  border-radius: var(--radius-sm);
  color: var(--text-tertiary);
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease-out);
}
.session-menu-btn:hover {
  background: var(--bg-secondary);
  color: var(--text-primary);
}

.session-menu {
  position: absolute;
  top: 100%;
  right: 8px;
  margin-top: 4px;
  min-width: 140px;
  background: var(--bg-primary);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-md);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  padding: 4px;
  z-index: 1000;
  animation: slideDown 0.15s ease-out;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  padding: 8px 12px;
  background: transparent;
  border: none;
  border-radius: 6px;
  color: var(--text-primary);
  font-size: 13px;
  text-align: left;
  cursor: pointer;
  transition: background var(--duration-fast) var(--ease-out);
}

.menu-item:hover {
  background: var(--bg-hover);
}

.menu-item.danger {
  color: var(--error);
}

.menu-item.danger:hover {
  background: rgba(239, 68, 68, 0.1);
}

.menu-item svg {
  flex-shrink: 0;
}

.loading-more {
  padding: 12px;
  text-align: center;
  font-size: 12px;
  color: var(--text-tertiary);
}

.loading-skeleton {
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
}
.skeleton-item {
  height: 40px;
  background: var(--bg-secondary);
  border-radius: var(--radius-md);
  animation: shimmer 1.5s ease-in-out infinite;
}

.empty-state-sm {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: var(--space-xl) var(--space-md);
  text-align: center;
}
.empty-state-sm svg {
  color: var(--text-tertiary);
  opacity: 0.5;
  margin-bottom: var(--space-sm);
}
.empty-state-sm p {
  font-size: 12px;
  color: var(--text-tertiary);
}

.sidebar-footer {
  flex-shrink: 0;
  padding: var(--space-sm);
  border-top: 1px solid var(--border-light);
}
.settings-btn {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  width: 100%;
  padding: 10px var(--space-md);
  background: transparent;
  color: var(--text-secondary);
  border: none;
  border-radius: var(--radius-md);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease-out);
}
.settings-btn svg {
  width: 16px;
  height: 16px;
  stroke: currentColor;
  fill: none;
}
.settings-btn:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

@keyframes shimmer {
  0% {
    background-position: -200% 0;
  }
  100% {
    background-position: 200% 0;
  }
}

/* 删除确认对话框 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  animation: fadeIn 0.15s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.confirm-dialog {
  background: var(--bg-primary);
  border-radius: 16px;
  padding: 24px;
  max-width: 400px;
  width: 90%;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  animation: slideUp 0.2s ease-out;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.confirm-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 12px 0;
}

.confirm-message {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.5;
  margin: 0 0 24px 0;
}

.confirm-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.btn-cancel,
.btn-delete {
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  border: none;
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease-out);
}

.btn-cancel {
  background: var(--bg-secondary);
  color: var(--text-primary);
}

.btn-cancel:hover {
  background: var(--bg-hover);
}

.btn-delete {
  background: var(--error);
  color: white;
}

.btn-delete:hover {
  background: #dc2626;
  box-shadow: 0 2px 8px rgba(239, 68, 68, 0.3);
}
</style>

