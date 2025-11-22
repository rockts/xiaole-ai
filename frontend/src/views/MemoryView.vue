<template>
  <div class="memory-view">
    <div class="page-header">
      <h1 class="page-title">记忆管理</h1>
      <p class="page-description">查看和管理 AI 学习的记忆内容</p>
    </div>

    <div class="stats-section">
      <div v-if="loading" class="stats-skeleton">
        <div class="skeleton-stat" v-for="i in 4" :key="i"></div>
      </div>
      <div v-else class="stats-grid">
        <div class="stat-card" v-for="item in aggregatedStats" :key="item.key">
          <div class="stat-value">{{ item.value }}</div>
          <div class="stat-label">{{ item.label }}</div>
        </div>
      </div>

      <div v-if="topTags.length" class="tags-section">
        <div class="section-title">标签分布</div>
        <div class="tags-grid">
          <div
            class="tag-item"
            v-for="t in topTags"
            :key="t.key"
            :class="{ active: activeTag === t.key }"
            @click="filterByTag(t.key)"
          >
            <span class="tag-label">{{ t.label }}</span>
            <span class="tag-count">{{ t.value }}</span>
          </div>
        </div>
      </div>
    </div>

    <div class="search-section">
      <div class="search-bar">
        <svg
          class="search-icon"
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
        >
          <circle cx="11" cy="11" r="8"></circle>
          <path d="m21 21-4.35-4.35"></path>
        </svg>
        <input
          v-model="searchQuery"
          type="text"
          class="search-input"
          placeholder="搜索记忆内容..."
          @keyup.enter="handleSearch"
        />
        <div class="search-actions">
          <button
            class="btn-sm"
            @click="handleSearch"
            :disabled="memoriesLoading"
          >
            关键词
          </button>
          <button
            class="btn-sm"
            @click="handleSemanticSearch"
            :disabled="memoriesLoading"
          >
            语义搜索
          </button>
          <button
            class="btn-sm btn-primary"
            @click="loadAllMemories"
            :disabled="memoriesLoading"
          >
            全部
          </button>
        </div>
      </div>

      <!-- 移除相对时间显示切换，统一使用绝对时间 -->
    </div>

    <div class="memory-section">
      <div v-if="memoriesLoading" class="list-skeleton">
        <div class="skeleton-item" v-for="i in 5" :key="i"></div>
      </div>

      <div v-else-if="memories.length === 0" class="empty-state">
        <svg
          width="64"
          height="64"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="1.5"
        >
          <path
            d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96.44 2.5 2.5 0 0 1-2.96-3.08 3 3 0 0 1-.34-5.58 2.5 2.5 0 0 1 1.32-4.24 2.5 2.5 0 0 1 1.98-3A2.5 2.5 0 0 1 9.5 2Z"
          />
        </svg>
        <p class="empty-title">暂无记忆</p>
        <p class="empty-description">
          {{
            searchQuery
              ? "未找到匹配的记忆内容"
              : "开始对话后，AI 会自动记录重要信息"
          }}
        </p>
      </div>

      <div v-else class="memory-list">
        <div class="memory-card" v-for="memory in memories" :key="memory.id">
          <div class="memory-header">
            <span class="memory-tag">{{
              formatTag(memory.tag) || "未分类"
            }}</span>
            <span class="memory-time">{{ formatTime(memory.timestamp) }}</span>
          </div>
          <div class="memory-content">{{ memory.content }}</div>
          <div class="memory-actions">
            <button
              class="btn-icon"
              @click="copyContent(memory.content)"
              title="复制"
            >
              <svg
                width="14"
                height="14"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
              >
                <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                <path
                  d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"
                ></path>
              </svg>
            </button>
            <button class="btn-icon" @click="startEdit(memory)" title="编辑">
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
            </button>
            <button
              class="btn-icon"
              @click="deleteMemory(memory.id)"
              title="删除"
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
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 编辑弹窗 -->
    <div v-if="editingMemory" class="modal-overlay" @click="cancelEdit">
      <div class="edit-dialog" @click.stop>
        <h3 class="dialog-title">编辑记忆</h3>
        <div class="form-group">
          <label>内容</label>
          <textarea
            v-model="editContent"
            rows="5"
            class="form-input"
          ></textarea>
        </div>
        <div class="form-group">
          <label>标签</label>
          <input v-model="editTag" type="text" class="form-input" />
        </div>
        <div class="dialog-actions">
          <button class="btn-cancel" @click="cancelEdit">取消</button>
          <button class="btn-save" @click="saveEdit">保存</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from "vue";
import { useMemoryStore } from "@/stores/memory";
import { storeToRefs } from "pinia";

const memoryStore = useMemoryStore();
const { stats, memories, loading, memoriesLoading } = storeToRefs(memoryStore);

const searchQuery = ref("");
const activeTag = ref(null);
const editingMemory = ref(null);
const editContent = ref("");
const editTag = ref("");

// 统一使用绝对时间显示，移除相对时间开关
const labelMap = {
  total: "总记忆数",
  conversation: "对话记录",
  image: "图片记忆",
  images: "图片记忆",
  fact: "事实",
  facts: "事实",
  schedule: "日程",
  reminder: "提醒",
  reminders: "提醒",
  task: "任务",
  tasks: "任务",
  document: "文档",
  documents: "文档",
  web: "网页",
  tool: "工具",
  tools: "工具",
  other: "其他",
  others: "其他",
};

const toFriendly = (key) => {
  if (!key) return "";
  const k = String(key).toLowerCase();
  return labelMap[k] || k;
};

// 聚合统计：将 conversation:* / image:* 等前缀聚合
const aggregatedStats = computed(() => {
  const out = new Map();
  const raw = stats.value || {};

  // 先把 total 提前
  if (typeof raw.total === "number") {
    out.set("total", {
      key: "total",
      label: toFriendly("total"),
      value: raw.total,
    });
  }

  // 遍历其他键
  Object.entries(raw).forEach(([key, value]) => {
    if (key === "total" || key === "by_tag") return;
    if (typeof value !== "number") return;

    const lower = key.toLowerCase();
    const prefix = lower.includes(":") ? lower.split(":")[0] : lower;
    const groupKey = [
      "conversation",
      "image",
      "images",
      "fact",
      "facts",
      "schedule",
      "reminder",
      "reminders",
      "task",
      "tasks",
      "document",
      "documents",
      "web",
      "tool",
      "tools",
    ].includes(prefix)
      ? prefix
      : prefix; // 未知前缀也按前缀聚合

    const prev = out.get(groupKey);
    const nextVal = (prev?.value || 0) + value;
    out.set(groupKey, {
      key: groupKey,
      label: toFriendly(groupKey),
      value: nextVal,
    });
  });

  // 如果没有 total，但可以从聚合里求和
  if (!out.has("total")) {
    let sum = 0;
    out.forEach((v, k) => {
      if (k !== "total") sum += v.value || 0;
    });
    if (sum > 0)
      out.set("total", {
        key: "total",
        label: toFriendly("total"),
        value: sum,
      });
  }

  // 排序：total 在最前，其余按 value 降序
  const arr = Array.from(out.values());
  arr.sort((a, b) => {
    if (a.key === "total") return -1;
    if (b.key === "total") return 1;
    return (b.value || 0) - (a.value || 0);
  });
  return arr;
});

// Top 标签：优先使用 stats.by_tag，如果没有则从聚合外推
const topTags = computed(() => {
  const raw = stats.value || {};
  const byTag =
    raw.by_tag && typeof raw.by_tag === "object" ? raw.by_tag : null;
  let entries = [];
  if (byTag) {
    entries = Object.entries(byTag).map(([key, value]) => ({
      key,
      label: formatTag(key),
      value: Number(value) || 0,
    }));
  } else {
    // 回退：从 stats 的其它键推断（排除 total）
    entries = Object.entries(raw)
      .filter(
        ([k, v]) => k !== "total" && k !== "by_tag" && typeof v === "number"
      )
      .map(([k, v]) => ({
        key: k,
        label: formatTag(k),
        value: Number(v) || 0,
      }));
  }

  // 合并相同 label（比如 conversation:* -> 对话）
  const merged = new Map();
  for (const e of entries) {
    const prev = merged.get(e.label);
    const nextVal = (prev?.value || 0) + e.value;
    merged.set(e.label, { key: e.label, label: e.label, value: nextVal });
  }
  const arr = Array.from(merged.values());
  arr.sort((a, b) => (b.value || 0) - (a.value || 0));
  return arr.slice(0, 8);
});

// 列表里的 tag 友好化：支持前缀冒号语法
const formatTag = (tag) => {
  if (!tag) return "";
  const lower = String(tag).toLowerCase();
  const prefix = lower.includes(":") ? lower.split(":")[0] : lower;
  return toFriendly(prefix);
};

// 时间格式化：YYYY-MM-DD HH:mm（本地时区）
const formatTime = (ts) => {
  if (!ts) return "";
  const d = new Date(ts);
  if (isNaN(d.getTime())) return String(ts);
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  const hh = String(d.getHours()).padStart(2, "0");
  const mm = String(d.getMinutes()).padStart(2, "0");
  return `${y}-${m}-${day} ${hh}:${mm}`;
};

const handleSearch = () => {
  activeTag.value = null;
  if (searchQuery.value.trim()) {
    memoryStore.searchMemories(searchQuery.value);
  }
};

const handleSemanticSearch = () => {
  activeTag.value = null;
  if (searchQuery.value.trim()) {
    memoryStore.semanticSearch(searchQuery.value);
  }
};

const loadAllMemories = async () => {
  activeTag.value = null;
  // 加载更长时间范围，避免列表为空（近10年，最多200条）
  searchQuery.value = "";
  await memoryStore.loadRecentMemories(24 * 365 * 10, 200);
  // 同时刷新统计，保持一致
  await memoryStore.loadStats();
};

const filterByTag = async (tag) => {
  // 如果点击的是 friendly label，需要找到对应的原始 key 前缀
  // 这里简化处理，直接传 label，后端支持模糊匹配 tag
  // 或者我们可以反向查找？
  // 实际上 topTags 里的 key 就是原始 key (如 conversation:default) 或者聚合后的 key (如 conversation)
  // 我们传递 key 给后端

  if (activeTag.value === tag) {
    activeTag.value = null;
    await loadAllMemories();
  } else {
    activeTag.value = tag;
    searchQuery.value = "";
    // 传递 tag 给 loadRecentMemories
    await memoryStore.loadRecentMemories(24 * 365 * 10, 200, tag);
  }
};

const startEdit = (memory) => {
  editingMemory.value = memory;
  editContent.value = memory.content;
  editTag.value = memory.tag;
};

const cancelEdit = () => {
  editingMemory.value = null;
  editContent.value = "";
  editTag.value = "";
};

const saveEdit = async () => {
  if (!editingMemory.value) return;

  const success = await memoryStore.updateMemory(
    editingMemory.value.id,
    editContent.value,
    editTag.value
  );

  if (success) {
    cancelEdit();
  } else {
    alert("更新失败，请重试");
  }
};

const copyContent = (text) => {
  navigator.clipboard.writeText(text).then(() => {
    // 可以添加一个简单的提示，这里简化处理
    console.log("已复制");
  });
};

const deleteMemory = async (id) => {
  if (confirm("确定要删除这条记忆吗？")) {
    await memoryStore.deleteMemory(id);
  }
};

onMounted(() => {
  memoryStore.loadStats();
  memoryStore.loadRecentMemories();
});
</script>

<style scoped>
.memory-view {
  max-width: 1200px;
  margin: 0 auto;
  padding: var(--space-xl);
}

.page-header {
  margin-bottom: var(--space-xl);
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: var(--space-xs);
}

.page-description {
  font-size: 13px;
  color: var(--text-secondary);
}

/* 统计卡片 */
.stats-section {
  margin-bottom: var(--space-xl);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: var(--space-md);
  margin-bottom: var(--space-lg);
}

.stat-card {
  background: var(--bg-primary);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-lg);
  padding: var(--space-lg);
  transition: all var(--duration-fast) var(--ease-out);
}

.stat-card:hover {
  border-color: var(--border-medium);
  box-shadow: var(--shadow-sm);
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: var(--space-xs);
}

.stat-label {
  font-size: 12px;
  color: var(--text-secondary);
}

.stats-skeleton {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: var(--space-md);
}

.skeleton-stat {
  height: 90px;
  background: var(--bg-secondary);
  border-radius: var(--radius-lg);
  animation: shimmer 1.5s ease-in-out infinite;
}

/* 标签区域 */
.tags-section {
  background: var(--bg-primary);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-lg);
  padding: var(--space-lg);
}

.section-title {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: var(--space-md);
}

.tags-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: var(--space-sm);
}

.tag-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-sm) var(--space-md);
  background: var(--bg-secondary);
  border-radius: var(--radius-md);
  font-size: 13px;
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease-out);
}

.tag-item:hover {
  background: var(--bg-hover);
}

.tag-item.active {
  background: var(--brand-primary);
  color: var(--text-inverse);
}

.tag-item.active .tag-label,
.tag-item.active .tag-count {
  color: var(--text-inverse);
}

/* 搜索区域 */
.search-section {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  margin-bottom: var(--space-lg);
}

.search-bar {
  flex: 1;
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  background: var(--bg-primary);
  border: 1px solid var(--border-medium);
  border-radius: var(--radius-lg);
  padding: var(--space-sm) var(--space-md);
  transition: all var(--duration-fast) var(--ease-out);
}

.search-bar:focus-within {
  border-color: var(--border-focus);
  box-shadow: 0 0 0 2px rgba(16, 163, 127, 0.1);
}

.search-icon {
  color: var(--text-tertiary);
  flex-shrink: 0;
}

.search-input {
  flex: 1;
  border: none;
  outline: none;
  background: transparent;
  font-size: 13px;
  color: var(--text-primary);
}

.search-input::placeholder {
  color: var(--text-tertiary);
}

.search-actions {
  display: flex;
  gap: var(--space-xs);
}

.btn-sm {
  padding: 6px 12px;
  font-size: 12px;
  font-weight: 500;
  background: transparent;
  color: var(--text-secondary);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease-out);
}

.btn-sm:hover:not(:disabled) {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.btn-sm:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-sm.btn-primary {
  background: var(--brand-primary);
  color: var(--text-inverse);
  border-color: var(--brand-primary);
}

.btn-sm.btn-primary:hover:not(:disabled) {
  background: var(--brand-primary-hover);
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  font-size: 13px;
  color: var(--text-secondary);
  cursor: pointer;
  user-select: none;
}

.checkbox-label input[type="checkbox"] {
  cursor: pointer;
}

/* 记忆列表 */
.memory-section {
  min-height: 400px;
}

.memory-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.memory-card {
  background: var(--bg-primary);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-lg);
  padding: var(--space-lg);
  transition: all var(--duration-fast) var(--ease-out);
}

.memory-card:hover {
  border-color: var(--border-medium);
  box-shadow: var(--shadow-sm);
}

.memory-header {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  margin-bottom: var(--space-md);
}

.memory-tag {
  padding: 4px 10px;
  background: var(--bg-secondary);
  color: var(--text-primary);
  font-size: 11px;
  font-weight: 500;
  border-radius: var(--radius-full);
}

.memory-time {
  font-size: 12px;
  color: var(--text-tertiary);
  margin-left: auto;
}

.memory-content {
  font-size: 14px;
  line-height: 1.6;
  color: var(--text-primary);
  margin-bottom: var(--space-md);
}

.memory-actions {
  display: flex;
  justify-content: flex-end;
}

.btn-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  padding: 0;
  background: transparent;
  border: none;
  border-radius: var(--radius-md);
  color: var(--text-tertiary);
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease-out);
}

.btn-icon:hover {
  background: var(--bg-hover);
  color: var(--error);
}

/* 骨架屏 */
.list-skeleton {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.skeleton-item {
  height: 120px;
  background: var(--bg-secondary);
  border-radius: var(--radius-lg);
  animation: shimmer 1.5s ease-in-out infinite;
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-3xl) var(--space-xl);
  text-align: center;
}

.empty-state svg {
  color: var(--text-tertiary);
  opacity: 0.3;
  margin-bottom: var(--space-lg);
}

.empty-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: var(--space-xs);
}

.empty-description {
  font-size: 13px;
  color: var(--text-secondary);
  max-width: 400px;
}

@keyframes shimmer {
  0% {
    background-position: -200% 0;
  }
  100% {
    background-position: 200% 0;
  }
}

.skeleton-stat,
.skeleton-item {
  background: linear-gradient(
    90deg,
    var(--bg-secondary) 0%,
    var(--bg-tertiary) 50%,
    var(--bg-secondary) 100%
  );
  background-size: 200% 100%;
}

/* 编辑弹窗 */
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
  z-index: 1000;
  animation: fadeIn 0.2s ease-out;
}

.edit-dialog {
  background: var(--bg-primary);
  border-radius: 16px;
  padding: 24px;
  width: 90%;
  max-width: 500px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  animation: slideUp 0.2s ease-out;
}

.dialog-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 20px 0;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.form-input {
  width: 100%;
  padding: 10px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-light);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
}

.form-input:focus {
  border-color: var(--brand-primary);
}

.dialog-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
}

.btn-cancel,
.btn-save {
  padding: 8px 20px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-cancel {
  background: var(--bg-secondary);
  color: var(--text-primary);
}

.btn-cancel:hover {
  background: var(--bg-hover);
}

.btn-save {
  background: var(--brand-primary);
  color: var(--text-inverse);
}

.btn-save:hover {
  background: var(--brand-primary-hover);
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
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
</style>
