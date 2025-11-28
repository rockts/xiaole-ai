<template>
  <div class="sidebar" :class="{ collapsed: isCollapsed }">
    <teleport to="body">
      <div
        v-if="!isCollapsed && isMobile"
        class="sidebar-overlay"
        @click="toggleSidebar"
      ></div>
    </teleport>
    <div class="sidebar-content">
      <!-- 顶部：标题 + 收起按钮 -->
      <div class="sidebar-logo-title">
        <div
          class="logo-wrapper"
          :class="{ 'show-toggle': isCollapsed }"
          @click="handleLogoClick"
        >
          <div class="logo">
            <img :src="logoSrc" alt="Logo" />
          </div>
          <div class="toggle-icon">
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
              <rect x="3" y="3" width="18" height="18" rx="4" ry="4"></rect>
              <line x1="9" y1="3" x2="9" y2="21"></line>
            </svg>
          </div>
        </div>
        <div class="title">小乐 AI 管家</div>
        <button class="collapse-btn" @click="toggleSidebar" title="收起侧边栏">
          <svg
            width="18"
            height="18"
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
          @click="handleMobileNav"
        >
          <span class="nav-icon" v-html="item.icon"></span>
          <span class="nav-label">{{ item.label }}</span>
        </router-link>
      </nav>

      <!-- 最近对话列表 -->
      <div class="sessions-section">
        <!-- 待办任务列表 (显示在历史对话上方) -->
        <div class="tasks-section" v-if="incompleteTasks.length > 0">
          <div class="section-header">
            <span>待办任务</span>
          </div>
          <div class="tasks-list">
            <div
              v-for="task in incompleteTasks"
              :key="task.id"
              class="task-item"
              @click="handleTaskClick(task)"
            >
              <div class="task-status-icon">
                <svg
                  width="14"
                  height="14"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <circle cx="12" cy="12" r="10"></circle>
                </svg>
              </div>
              <div class="task-content">{{ task.title }}</div>
            </div>
          </div>
        </div>

        <div class="section-header">
          <span>历史对话</span>
        </div>

        <div class="sessions-list" @scroll="handleScroll" ref="sessionsListRef">
          <template v-if="loading && sessions.length === 0">
            <div class="loading-skeleton">
              <div class="skeleton-item" v-for="i in 3" :key="i"></div>
            </div>
          </template>

          <template v-else-if="sessions.length === 0">
            <div class="empty-state-sm">
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
          </template>

          <template v-else>
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
              <div
                class="session-content"
                @click="loadSession(session.id || session.session_id)"
              >
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
                  <svg
                    v-if="session.pinned"
                    class="pin-icon"
                    width="14"
                    height="14"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                  >
                    <path
                      d="M12 17v5M9 10.76a2 2 0 0 1-1.11 1.79l-1.78.9A2 2 0 0 0 5 15.24V16a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-.76a2 2 0 0 0-1.11-1.79l-1.78-.9A2 2 0 0 1 15 10.76V7a1 1 0 0 1 1-1 2 2 0 0 0 0-4H8a2 2 0 0 0 0 4 1 1 0 0 1 1 1z"
                    />
                  </svg>
                  {{ session.title || "未命名对话" }}
                </div>
              </div>
              <button
                v-if="
                  hoveredSessionId === (session.id || session.session_id) ||
                  activeMenuSessionId === (session.id || session.session_id) ||
                  isCurrentSession(session)
                "
                class="session-menu-btn"
                aria-label="会话操作菜单"
                aria-haspopup="menu"
                :id="`menu-btn-${session.id || session.session_id}`"
                :ref="
                  (el) => setMenuBtnRef(el, session.id || session.session_id)
                "
                @mousedown.stop.prevent
                @click.stop.prevent="
                  toggleSessionMenu(session.id || session.session_id, $event)
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

              <!-- 菜单弹出层（Teleport到body，避免overflow裁剪） -->
              <teleport to="body">
                <div
                  v-if="
                    activeMenuSessionId === (session.id || session.session_id)
                  "
                  class="session-menu"
                  :style="{
                    position: 'fixed',
                    top: menuPosition.top + 'px',
                    left: menuPosition.left + 'px',
                    right: 'auto',
                    'transform-origin':
                      menuPosition.placement === 'top'
                        ? 'bottom right'
                        : 'top right',
                  }"
                  @click.stop
                >
                  <div :class="['menu-arrow', menuPosition.placement]"></div>
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
              </teleport>
            </div>

            <div v-if="loading && sessions.length > 0" class="loading-more">
              加载中...
            </div>
          </template>
        </div>
      </div>

      <!-- 底部：用户资料 -->
      <div
        class="sidebar-footer user-profile"
        @click="toggleUserMenu"
        @touchstart.stop="toggleUserMenu"
        ref="userMenuRef"
        style="
          cursor: pointer;
          user-select: none;
          -webkit-tap-highlight-color: rgba(0, 0, 0, 0.1);
        "
      >
        <div class="avatar-wrapper">
          <div class="user-avatar-icon">
            <svg
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            >
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
              <circle cx="12" cy="7" r="4" />
            </svg>
          </div>
        </div>
        <div class="user-info">
          <div class="username">{{ username }}</div>
          <div class="user-status">在线</div>
        </div>
        <button class="settings-icon-btn" title="用户菜单">
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
            <circle cx="12" cy="12" r="1"></circle>
            <circle cx="12" cy="5" r="1"></circle>
            <circle cx="12" cy="19" r="1"></circle>
          </svg>
        </button>

        <!-- 用户菜单弹出层 -->
        <teleport to="body">
          <transition name="dropdown">
            <div
              v-if="showUserMenu"
              class="user-dropdown-menu"
              :style="{
                left: userMenuPosition.left + 'px',
                bottom: userMenuPosition.bottom + 'px',
              }"
              @click.stop
            >
              <div class="dropdown-item" @click="openSettingsModal">
                <svg
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                  <circle cx="12" cy="7" r="4"></circle>
                </svg>
                <span>个人中心</span>
              </div>
              <div class="dropdown-item" @click="openSettingsModal">
                <svg
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <circle cx="12" cy="12" r="3" />
                  <path
                    d="M12 1v6m0 6v6M3.93 3.93l4.24 4.24m8.48 8.48l4.24 4.24M1 12h6m6 0h6M3.93 20.07l4.24-4.24m8.48-8.48l4.24-4.24"
                  />
                </svg>
                <span>设置</span>
              </div>
              <div class="dropdown-divider"></div>
              <div class="dropdown-item danger">
                <svg
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
                  <polyline points="16 17 21 12 16 7" />
                  <line x1="21" y1="12" x2="9" y2="12" />
                </svg>
                <span>退出登录</span>
              </div>
            </div>
          </transition>
        </teleport>
      </div>
      <!-- 结束 sidebar-content -->
    </div>

    <!-- 设置弹窗 - 使用 Teleport 渲染到 body 确保最高层级 -->
    <teleport to="body">
      <SettingsModal
        v-if="showSettingsModal"
        @close="showSettingsModal = false"
      />
    </teleport>

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

    <!-- 分享弹窗 -->
    <ShareDialog
      v-if="showShareDialog"
      :title="shareDialogTitle"
      :share-url="shareDialogUrl"
      @close="showShareDialog = false"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, nextTick, watch } from "vue";
import { useRouter, useRoute } from "vue-router";
import { useChatStore } from "@/stores/chat";
import { storeToRefs } from "pinia";
import logoImage from "@/assets/logo-xiaole.png";
import ShareDialog from "@/components/common/ShareDialog.vue";
import SettingsModal from "@/components/common/SettingsModal.vue";
import api from "@/services/api";

const router = useRouter();
const route = useRoute();
const chatStore = useChatStore();
const { sessions, loading } = storeToRefs(chatStore);

// 任务数据
const tasks = ref([]);
const incompleteTasks = computed(() =>
  tasks.value.filter((t) => t.status !== "completed").slice(0, 5)
); // 只显示前5个未完成任务

const fetchTasks = async () => {
  try {
    const data = await api.getTasks();
    if (data.success) {
      tasks.value = data.tasks || [];
    }
  } catch (e) {
    console.error("Failed to fetch tasks", e);
  }
};

const handleTaskClick = (task) => {
  router.push(`/task/${task.id}`);
  handleMobileNav();
};

// 移动端检测
const isMobile = ref(window.innerWidth <= 768);

// 使用新的 logo
const logoSrc = computed(() => logoImage);
// 从 localStorage 读取收起状态，移动端默认收起
const savedCollapsed = localStorage.getItem("sidebar-collapsed");
const isCollapsed = ref(
  isMobile.value
    ? true
    : savedCollapsed !== null
    ? savedCollapsed === "true"
    : false
);

const navItems = [
  {
    path: "/memory",
    label: "记忆",
    icon: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" xmlns="http://www.w3.org/2000/svg"><path d="M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z"></path></svg>',
  },
  {
    path: "/behavior",
    label: "行为分析",
    icon: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" xmlns="http://www.w3.org/2000/svg"><path d="M18 20V10"></path><path d="M12 20V4"></path><path d="M6 20v-6"></path></svg>',
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
    path: "/tools",
    label: "工具",
    icon: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" xmlns="http://www.w3.org/2000/svg"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"></path></svg>',
  },
];

const isActive = (path) => route.path.startsWith(path);
const isCurrentSession = (session) =>
  route.params.sessionId == (session.id || session.session_id);

const handleMobileNav = () => {
  if (isMobile.value) {
    isCollapsed.value = true;
  }
};

const newChat = () => {
  chatStore.clearCurrentSession();
  router.push("/chat");
  handleMobileNav();
};
const loadSession = (id) => {
  router.push(`/chat/${id}`);
  handleMobileNav();
};

const showSettingsModal = ref(false);
const showUserMenu = ref(false);
const userMenuPosition = ref({ left: 0, bottom: 0 });
const userMenuRef = ref(null);
const username = ref("游戏小乐乐"); // 默认值，后续从localStorage加载

const openSettingsModal = () => {
  showSettingsModal.value = true;
  showUserMenu.value = false;
  handleMobileNav();
};

const updateUserMenuPosition = () => {
  if (!userMenuRef.value) return;
  const rect = userMenuRef.value.getBoundingClientRect();
  const isMobile = window.innerWidth <= 768;

  if (isMobile) {
    // 移动端：使用侧边栏的左侧位置，保持宽度一致
    userMenuPosition.value = {
      left: 8, // 与侧边栏对齐
      bottom: 70,
    };
  } else {
    // 桌面端：根据实际位置计算
    userMenuPosition.value = {
      left: rect.left + 8,
      bottom: window.innerHeight - rect.top + 8,
    };
  }
};

const toggleUserMenu = (event) => {
  // 阻止事件冒泡和默认行为
  if (event) {
    event.stopPropagation();
    event.preventDefault();
  }

  if (!showUserMenu.value) {
    updateUserMenuPosition();
    showUserMenu.value = true;
  } else {
    showUserMenu.value = false;
  }
};

const handleLogoClick = () => {
  if (isCollapsed.value) {
    toggleSidebar();
  }
};

// 加载用户名
const loadUserProfile = () => {
  const saved = localStorage.getItem("xiaole_settings");
  if (saved) {
    const settings = JSON.parse(saved);
    if (settings.nickname) {
      username.value = settings.nickname;
    }
  }
};

// 悬停和菜单状态
const hoveredSessionId = ref(null);
const activeMenuSessionId = ref(null);
const editingSessionId = ref(null);
const editingTitle = ref("");
const showDeleteConfirm = ref(false);
const deletingSessionId = ref(null);

// 会话列表元素，用于检测滚动条是否出现
const sessionsListRef = ref(null);
const menuBtnRefs = ref({});
const setMenuBtnRef = (el, id) => {
  if (el) menuBtnRefs.value[id] = el;
  else delete menuBtnRefs.value[id];
};
const menuPosition = ref({ top: 0, left: 0, placement: "bottom" });

// 分页加载
const pageSize = 20;
const currentPage = ref(1);
const displayedSessions = computed(() => {
  // 将置顶的会话排在前面,然后按更新时间倒序
  const sorted = [...sessions.value].sort((a, b) => {
    const aPinned = a.pinned || false;
    const bPinned = b.pinned || false;
    // 置顶会话优先
    if (aPinned && !bPinned) return -1;
    if (!aPinned && bPinned) return 1;
    // 同为置顶或同为非置顶时,按更新时间倒序
    const aTime = new Date(a.updated_at || a.created_at).getTime();
    const bTime = new Date(b.updated_at || b.created_at).getTime();
    return bTime - aTime;
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
  // 滚动时关闭菜单，避免位置错位
  if (activeMenuSessionId.value) {
    activeMenuSessionId.value = null;
  }
};

// 确保初次渲染时有滚动条：如果列表未能产生滚动，自动多加载几页
const ensureScrollable = async () => {
  await nextTick();
  const el = sessionsListRef.value;
  if (!el) return;
  let guard = 20; // 最多尝试 20 次，避免死循环
  while (
    el.scrollHeight <= el.clientHeight &&
    displayedSessions.value.length < sessions.value.length &&
    guard-- > 0
  ) {
    currentPage.value++;
    await nextTick();
  }
};

const updateMenuPosition = (id, evt) => {
  const btn =
    menuBtnRefs.value[id] || document.getElementById(`menu-btn-${id}`);
  if (!btn) return;

  // 尝试获取实际菜单尺寸 (需要在 nextTick 后调用)
  const menuEl = document.querySelector(".session-menu");
  const width = menuEl ? menuEl.offsetWidth : 180;
  const height = menuEl ? menuEl.offsetHeight : 200;

  const rect = btn.getBoundingClientRect();
  const windowWidth = window.innerWidth;
  const windowHeight = window.innerHeight;
  const gap = 6;

  // 默认策略：右对齐 (菜单右边缘与按钮右边缘对齐)
  let left = rect.right - width;
  // 如果右对齐导致左边溢出 (按钮太靠左)，则改为左对齐
  if (left < gap) {
    left = rect.left;
  }
  // 再次检查是否溢出屏幕右侧
  if (left + width > windowWidth - gap) {
    left = windowWidth - width - gap;
  }
  // 再次检查是否溢出屏幕左侧
  if (left < gap) {
    left = gap;
  }

  // 垂直策略
  let top = rect.bottom + gap;
  let placement = "bottom";

  // 检查底部空间
  if (top + height > windowHeight - gap) {
    // 底部空间不足，尝试向上
    const topPosition = rect.top - gap - height;
    if (topPosition > gap) {
      top = topPosition;
      placement = "top";
    } else {
      // 上下都不够，选择空间更大的一侧并限制高度(CSS中处理滚动)或强制贴边
      if (rect.top > windowHeight - rect.bottom) {
        top = gap; // 贴顶
        // 这里理想情况应该设置 max-height，但简化处理先保证位置
      } else {
        top = windowHeight - height - gap; // 贴底
      }
    }
  }

  menuPosition.value = { top, left, placement };
};

const toggleSessionMenu = async (id, evt) => {
  console.log("Menu toggle:", id, "current:", activeMenuSessionId.value);
  if (activeMenuSessionId.value === id) {
    activeMenuSessionId.value = null;
    return;
  }
  activeMenuSessionId.value = id;
  await nextTick();
  updateMenuPosition(id, evt);
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
    await api.updateSession(id, { title: newTitle });

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

const showShareDialog = ref(false);
const shareDialogUrl = ref("");
const shareDialogTitle = ref("分享对话");
const shareSession = async (id) => {
  activeMenuSessionId.value = null;
  const session = sessions.value.find((s) => (s.id || s.session_id) === id);
  const title = session?.title || "未命名对话";
  shareDialogTitle.value = title;
  shareDialogUrl.value = `${window.location.origin}/share/${id}`;
  showShareDialog.value = true;
};

const pinSession = async (id) => {
  activeMenuSessionId.value = null;
  const session = sessions.value.find((s) => (s.id || s.session_id) === id);
  if (!session) return;

  try {
    // 切换置顶状态
    const isPinned = session.pinned || false;
    await api.updateSession(id, { pinned: !isPinned });

    session.pinned = !isPinned;
    // 重新排序会话列表,置顶的会话排在前面
    await chatStore.loadSessions(true);
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
    await api.deleteSession(id);

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
  } catch (error) {
    console.error("删除失败:", error);
    alert("删除失败,请重试");
  }
};

const toggleSidebar = () => {
  isCollapsed.value = !isCollapsed.value;
  // 保存到 localStorage
  localStorage.setItem("sidebar-collapsed", isCollapsed.value.toString());
};

const toggle = () => {
  isCollapsed.value = !isCollapsed.value;
  // 保存到 localStorage
  localStorage.setItem("sidebar-collapsed", isCollapsed.value.toString());
};
defineExpose({ toggle });

let clickOutsideHandler = null;

onMounted(() => {
  chatStore.loadSessions();
  fetchTasks();
  loadUserProfile();

  // 点击外部关闭菜单
  clickOutsideHandler = (e) => {
    // 检查点击是否在菜单按钮或菜单内部
    const isMenuBtn = e.target.closest(".session-menu-btn");
    const isMenu = e.target.closest(".session-menu");

    if (!isMenuBtn && !isMenu && activeMenuSessionId.value) {
      console.log("Closing menu due to outside click");
      activeMenuSessionId.value = null;
    }

    // 用户菜单关闭逻辑
    const isUserProfile = e.target.closest(".user-profile");
    if (!isUserProfile && showUserMenu.value) {
      showUserMenu.value = false;
    }
  };
  document.addEventListener("click", clickOutsideHandler);
  // 初次挂载后，尝试保证出现滚动条
  ensureScrollable();

  // 强制显示移动端滚动条
  nextTick(() => {
    if (window.innerWidth <= 768) {
      const sessionsList = document.querySelector(".sessions-list");
      if (sessionsList) {
        // 强制设置滚动条样式
        sessionsList.style.cssText += `
          overflow-y: scroll !important;
          -webkit-overflow-scrolling: touch !important;
          scrollbar-width: auto !important;
        `;

        // 添加滚动指示器（上下渐变）
        const sessionsSection = document.querySelector(".sessions-section");
        if (
          sessionsSection &&
          sessionsList.scrollHeight > sessionsList.clientHeight
        ) {
          sessionsSection.style.cssText += `
            position: relative;
          `;
          // 上渐变
          const topGradient = document.createElement("div");
          topGradient.className = "scroll-indicator-top";
          topGradient.style.cssText = `
            position: absolute;
            top: 0;
            left: 0;
            right: 14px;
            height: 20px;
            background: linear-gradient(to bottom, var(--bg-primary), transparent);
            pointer-events: none;
            z-index: 10;
          `;
          // 下渐变
          const bottomGradient = document.createElement("div");
          bottomGradient.className = "scroll-indicator-bottom";
          bottomGradient.style.cssText = `
            position: absolute;
            bottom: 0;
            left: 0;
            right: 14px;
            height: 30px;
            background: linear-gradient(to top, var(--bg-primary), transparent);
            pointer-events: none;
            z-index: 10;
          `;
          sessionsSection.appendChild(topGradient);
          sessionsSection.appendChild(bottomGradient);

          console.log("Mobile scrollbar forced with indicators");
        }
      }
    }
  });

  // 窗口变化时关闭菜单或重算
  const onResize = () => {
    const newIsMobile = window.innerWidth <= 768;
    if (isMobile.value !== newIsMobile) {
      isMobile.value = newIsMobile;
      // 切换到移动端时自动收起，切换到桌面端时如果之前是收起的（且不是用户手动收起...这里简化处理，切换模式重置或保持）
      // 简单策略：切换到移动端必定收起
      if (newIsMobile) {
        isCollapsed.value = true;
      }
    }

    if (activeMenuSessionId.value)
      updateMenuPosition(activeMenuSessionId.value);
  };
  window.addEventListener("resize", onResize);
  window.__sidebar_onResize = onResize;
});

onUnmounted(() => {
  if (clickOutsideHandler) {
    document.removeEventListener("click", clickOutsideHandler);
  }
  if (window.__sidebar_onResize) {
    window.removeEventListener("resize", window.__sidebar_onResize);
    delete window.__sidebar_onResize;
  }
});

// 监听会话数据变化，数据到达后再次检查是否需要自动扩展分页
watch(
  () => sessions.value.length,
  () => {
    ensureScrollable();
  }
);
</script>

<style scoped>
.sidebar {
  display: flex;
  flex-direction: column;
  width: 245px;
  min-width: 245px;
  flex: 0 0 245px;
  height: 100vh;
  background: var(--bg-primary);
  border-right: 1px solid var(--border-light);
  transition: all var(--duration-normal) var(--ease-out);
  z-index: 900;
  box-sizing: border-box;
  padding-bottom: env(safe-area-inset-bottom);
}

.sidebar.collapsed {
  width: 70px;
  min-width: 70px;
  flex: 0 0 70px;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .sidebar {
    position: fixed;
    top: 0;
    left: 0;
    height: 100vh;
    height: 100dvh; /* 使用动态视口高度，更准确 */
    width: 245px !important; /* 移动端展开时宽度固定 */
    min-width: 245px !important;
    flex: 0 0 245px !important;
    transform: translateX(0);
    box-shadow: var(--shadow-lg);
    z-index: 1000;
    padding-bottom: 0; /* 移除sidebar的padding，让footer自己处理 */
  }

  .sidebar.collapsed {
    width: 245px !important;
    min-width: 245px !important;
    flex: 0 0 245px !important;
    transform: translateX(-100%);
  }

  /* 移动端隐藏收起按钮，因为有遮罩层点击关闭 */
  .collapse-btn {
    display: none !important;
  }
}

.sidebar-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 0;
  gap: 0;
  min-height: 0;
  overflow: hidden;
}

.sidebar-logo-title {
  flex: 0 0 auto;
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: 8px 12px 4px;
  min-height: 40px;
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
  display: flex !important;
  align-items: center;
  justify-content: center;
  border: none;
  background: transparent;
  cursor: pointer;
  border-radius: 6px;
  transition: all var(--duration-fast) var(--ease-out);
  padding: 0;
}

.collapse-btn svg {
  display: block;
  width: 18px;
  height: 18px;
}

.collapse-btn:hover {
  background: var(--bg-hover);
}

.collapse-btn svg {
  stroke: var(--icon-color);
}

.sidebar.collapsed .title,
.sidebar.collapsed .nav-label,
.sidebar.collapsed .sessions-section,
.sidebar.collapsed .collapse-btn {
  display: none !important;
}

.sidebar.collapsed .sidebar-logo-title {
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 6px;
  padding: var(--space-xs);
}

.sidebar.collapsed .nav-item {
  justify-content: center;
  padding: 10px;
}

.sidebar.collapsed .sidebar-footer {
  display: flex;
}

.sidebar.collapsed .settings-btn {
  justify-content: center;
  padding: 10px;
  display: flex !important;
}

.sidebar.collapsed .settings-btn .nav-icon {
  display: flex !important;
}

.sidebar.collapsed .settings-btn .nav-label {
  display: none !important;
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
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.sidebar-nav {
  flex: 0 0 auto;
  display: flex;
  flex-direction: column;
  gap: 0;
  overflow: visible;
  padding: 0 8px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: 6px 12px;
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
  color: var(--icon-color);
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
  font-size: 14px;
}

.tasks-section {
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding-bottom: 8px;
  margin-bottom: 8px;
  border-bottom: 1px solid var(--border-light);
}

.tasks-list {
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding-right: 8px;
}

.task-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: background var(--duration-fast);
  font-size: 13px;
  color: var(--text-secondary);
}

.task-item:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.task-status-icon {
  display: flex;
  align-items: center;
  color: var(--text-tertiary);
}

.task-content {
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.sidebar.collapsed .tasks-section {
  display: none;
}

.sessions-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
  max-height: calc(100vh - 200px);
  gap: 0;
  margin: 0;
  padding: 0 0 0 8px;
  overflow: hidden;
}

.sessions-list {
  flex: 1;
  overflow-y: auto;
  padding-right: 8px;
}

.section-header {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 2px 4px;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 4px;
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

/* 滚动条视觉（保留在组件内，避免全局污染） */
.sessions-list::-webkit-scrollbar {
  width: 8px;
}
.sessions-list::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.06);
  border-radius: 4px;
}
[data-theme="dark"] .sessions-list::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.06);
}
.sessions-list::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.3);
  border-radius: 4px;
}
[data-theme="dark"] .sessions-list::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.3);
}

.session-item {
  position: relative;
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  padding: 6px 12px;
  margin-bottom: 2px;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: background var(--duration-fast) var(--ease-out);
  z-index: 1;
}
.session-item:hover {
  background: var(--bg-hover);
  z-index: 10;
}
.session-item.active {
  background: var(--bg-active);
  z-index: 10;
}
.session-item.pinned {
  background: var(--bg-secondary);
}

.session-content {
  flex: 1;
  min-width: 0;
  pointer-events: auto;
}
.session-title {
  font-size: 14px;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.pin-icon {
  display: inline-block;
  vertical-align: -2px;
  margin-right: 6px;
  stroke: currentColor;
  color: var(--brand-primary);
}

.session-title-input {
  width: 100%;
  font-size: 14px;
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
  color: var(--icon-color);
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease-out);
  pointer-events: auto;
  z-index: 100;
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
  min-width: 180px;
  background: var(--bg-primary);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-md);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.18), 0 1px 0 rgba(0, 0, 0, 0.06);
  padding: 4px;
  z-index: 9999;
  animation: slideDown 0.15s ease-out;
}

.menu-arrow {
  position: absolute;
  width: 10px;
  height: 10px;
  background: var(--bg-primary);
  transform: rotate(45deg);
  z-index: -1; /* 让箭头在边框外层阴影之下 */
  box-shadow: -1px -1px 0 0 var(--border-light);
}
.menu-arrow.bottom {
  top: -5px;
  right: 18px;
  box-shadow: -1px -1px 0 0 var(--border-light);
}
.menu-arrow.top {
  bottom: -5px;
  right: 18px;
  box-shadow: 1px 1px 0 0 var(--border-light);
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
  font-size: 14px;
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
  padding: var(--space-md);
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
  flex-grow: 0;
  padding: 2px 8px;
  /* 为 iOS/全面屏添加底部安全区内边距，避免遮挡用户栏 */
  padding-bottom: calc(2px + env(safe-area-inset-bottom));
  padding-bottom: calc(2px + constant(safe-area-inset-bottom));
  border-top: 1px solid var(--border-light);
  background: var(--bg-primary);
  z-index: 5;
}
.settings-btn {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  width: 100%;
  padding: 8px 12px;
  background: transparent;
  color: var(--icon-color);
  border: none;
  border-radius: var(--radius-md);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease-out);
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

/* 用户资料底部栏 */
.user-profile {
  position: relative;
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 12px;
  padding: 12px;
  cursor: pointer;
  transition: background var(--duration-fast) var(--ease-out);
}

.user-profile:hover {
  background: var(--bg-hover);
}

.avatar-wrapper {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  overflow: hidden;
  flex-shrink: 0;
  border: 2px solid var(--bg-secondary);
}

.user-avatar-icon {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--brand-gradient);
  color: white;
}

.user-dropdown-menu {
  position: fixed;
  width: 225px; /* 与侧边栏宽度保持一致 */
  background: var(--bg-primary);
  border: 1px solid var(--border-light);
  border-radius: 12px; /* 圆角效果 */
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  padding: 8px;
  z-index: 10000 !important;
  animation: slideUp 0.15s ease-out;
  cursor: default;
  overflow: hidden;
}

@media (max-width: 768px) {
  .user-dropdown-menu {
    /* 移动端保持一致样式 */
    z-index: 10000 !important;
    width: 225px;
  }
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 14px;
  color: var(--text-primary);
  font-size: 14px;
  border-radius: 8px; /* 圆角 */
  cursor: pointer;
  transition: all 0.2s ease;
}

.dropdown-item:hover {
  background: var(--bg-hover);
  transform: translateX(2px);
}

.dropdown-item svg {
  color: var(--icon-color);
  transition: color 0.2s ease;
}

.dropdown-item:hover svg {
  color: var(--text-primary);
}

.dropdown-item.danger {
  color: var(--error);
}

.dropdown-divider {
  height: 1px;
  background: var(--border-light);
  margin: 4px 0;
}

.user-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.username {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-status {
  font-size: 12px;
  color: var(--success);
  display: flex;
  align-items: center;
  gap: 4px;
}

.user-status::before {
  content: "";
  display: block;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--success);
}

.settings-icon-btn {
  flex-shrink: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  color: var(--text-secondary);
  border-radius: 6px;
  cursor: pointer;
  transition: color 0.2s;
  margin-left: auto; /* 推到最右边 */
}

.user-profile:hover .settings-icon-btn {
  color: var(--text-primary);
  /* 移除背景色，响应用户"去掉外面方框"的请求 */
  background: transparent;
}

/* 收起状态下的用户栏 */
.sidebar.collapsed .user-profile {
  justify-content: center;
  padding: 12px 0;
}

.sidebar.collapsed .user-info,
.sidebar.collapsed .settings-icon-btn {
  display: none;
}

.sidebar.collapsed .avatar-wrapper {
  width: 40px;
  height: 40px;
  border-width: 0;
}

/* 移动端覆盖：让可滚动区域自适应，避免挤压底部用户栏 */
@media (max-width: 768px) {
  .sidebar-content {
    /* 确保sidebar-content占满高度并使用flex分配 */
    height: 100%;
    max-height: 100vh;
    max-height: 100dvh;
    display: flex;
    flex-direction: column;
    overflow-y: auto; /* 允许整体滚动 */
  }
  .sessions-section {
    /* 限制最大高度，为footer预留空间 */
    max-height: calc(100vh - 200px); /* 为顶部logo+nav+footer预留空间 */
    max-height: calc(100dvh - 200px);
    flex: 1;
    min-height: 0;
    overflow: hidden;
    display: flex;
    flex-direction: column;
  }
  .sessions-list {
    flex: 1;
    overflow-y: scroll !important; /* 强制显示滚动条 */
    overflow-x: hidden;
    -webkit-overflow-scrolling: touch; /* iOS平滑滚动 */
    /* 强制显示滚动条 - 所有浏览器 */
    scrollbar-width: auto !important; /* Firefox - auto比thin更明显 */
    scrollbar-color: rgba(0, 0, 0, 0.5) rgba(0, 0, 0, 0.1) !important;
  }
  /* Chrome/Safari/Edge/移动端 - 强制显示，使用更明显的样式 */
  .sessions-list::-webkit-scrollbar {
    width: 14px !important; /* 加宽滚动条 */
    -webkit-appearance: none !important;
    display: block !important;
    background: rgba(0, 0, 0, 0.05) !important;
  }
  .sessions-list::-webkit-scrollbar-track {
    background: rgba(0, 0, 0, 0.08) !important;
    border-radius: 7px !important;
    margin: 4px 0 !important;
  }
  .sessions-list::-webkit-scrollbar-thumb {
    background: rgba(0, 0, 0, 0.45) !important;
    border-radius: 7px !important;
    border: 3px solid rgba(0, 0, 0, 0.05) !important; /* 边框让滚动条更明显 */
    background-clip: padding-box !important;
    min-height: 50px !important;
  }
  .sessions-list::-webkit-scrollbar-thumb:hover {
    background: rgba(0, 0, 0, 0.6) !important;
    background-clip: padding-box !important;
  }
  .sessions-list::-webkit-scrollbar-thumb:active {
    background: rgba(0, 0, 0, 0.7) !important;
    background-clip: padding-box !important;
  }
  .sidebar-footer {
    /* 确保footer始终在底部显示，增加足够的padding避免被系统UI遮挡 */
    flex-shrink: 0;
    padding: 12px 8px;
    padding-bottom: calc(20px + env(safe-area-inset-bottom));
    background: var(--bg-primary);
    border-top: 1px solid var(--border-light);
    min-height: 60px;
    box-sizing: border-box;
  }
}
</style>

<style>
/* 全局样式用于 Teleport 的遮罩层 */
.sidebar-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 999;
  animation: fadeIn 0.2s ease-out;
  backdrop-filter: blur(2px);
  display: block !important; /* 确保显示，覆盖 app.css 中的 display: none */
}
</style>

