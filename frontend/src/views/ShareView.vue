<template>
  <div class="share-page">
    <div class="share-container">
      <header class="share-header">
        <h1 class="title">{{ sessionTitle || "分享的对话" }}</h1>
        <div class="actions">
          <button class="pill" @click="copyLink">复制链接</button>
        </div>
      </header>

      <section v-if="loading" class="loading">加载中...</section>
      <section v-else-if="error" class="error">{{ error }}</section>

      <section v-else class="messages">
        <article
          v-for="(m, idx) in displayMessages"
          :key="idx"
          :class="['msg', m.role]"
        >
          <div class="role">{{ m.role === "user" ? "你" : "小乐" }}</div>
          <div class="content" v-html="formatContent(m.content)"></div>
        </article>
        <div v-if="messages.length > displayMessages.length" class="more-hint">
          仅显示最近 {{ displayLimit }} 条消息
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref, computed } from "vue";
import { useRoute } from "vue-router";
import api from "@/services/api";

const route = useRoute();
const id = route.params.id;
const loading = ref(true);
const error = ref("");
const messages = ref([]);
const sessionTitle = ref("");
const displayLimit = 20;

const displayMessages = computed(() => messages.value.slice(-displayLimit));

const fetchData = async () => {
  try {
    loading.value = true;
    const data = await api.getSession(id);
    sessionTitle.value = data.title || "分享的对话";
    messages.value = data.messages || data.history || [];
    document.title = `${sessionTitle.value} - 分享 - 小乐 AI 管家`;
  } catch (e) {
    console.error(e);
    error.value = "未能加载该分享内容，可能已删除或不可访问。";
  } finally {
    loading.value = false;
  }
};

const copyLink = async () => {
  const url = window.location.href;
  try {
    if (navigator.clipboard?.writeText) {
      await navigator.clipboard.writeText(url);
      alert("已复制链接");
    } else {
      const ta = document.createElement("textarea");
      ta.value = url;
      ta.style.position = "fixed";
      ta.style.opacity = "0";
      document.body.appendChild(ta);
      ta.select();
      document.execCommand("copy");
      document.body.removeChild(ta);
      alert("已复制链接");
    }
  } catch (e) {
    alert("复制失败，请手动复制地址栏链接");
  }
};

const escapeHTML = (s = "") =>
  s.replace(
    /[&<>"']/g,
    (c) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[
        c
      ])
  );
const formatContent = (text = "") => {
  // 简单换行与链接高亮
  const escaped = escapeHTML(text);
  return escaped
    .replace(
      /(https?:\/\/[^\s]+)/g,
      '<a href="$1" target="_blank" rel="noopener">$1</a>'
    )
    .replace(/\n/g, "<br/>");
};

onMounted(fetchData);
</script>

<style scoped>
.share-page {
  display: flex;
  justify-content: center;
  padding: 24px;
}
.share-container {
  width: min(920px, 92vw);
}
.share-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}
.title {
  font-size: 22px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}
.actions .pill {
  border: none;
  background: var(--bg-secondary);
  color: var(--text-primary);
  padding: 8px 14px;
  border-radius: 999px;
  cursor: pointer;
}
.actions .pill:hover {
  background: var(--bg-hover);
}

.loading,
.error {
  padding: 24px 12px;
  color: var(--text-secondary);
}

.messages {
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.msg {
  display: flex;
  gap: 12px;
  padding: 12px 14px;
  border: 1px solid var(--border-light);
  border-radius: 12px;
  background: var(--bg-primary);
}
.msg .role {
  font-weight: 600;
  color: var(--text-secondary);
  width: 42px;
  flex-shrink: 0;
}
.msg .content {
  color: var(--text-primary);
  line-height: 1.6;
  word-break: break-word;
}
.msg.user {
  background: var(--bg-secondary);
}
.more-hint {
  margin-top: 4px;
  color: var(--text-tertiary);
  font-size: 12px;
}
</style>
