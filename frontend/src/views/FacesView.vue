<template>
  <div class="faces-view">
    <div class="header">
      <h2>人脸管理</h2>
      <div class="actions">
        <button class="refresh-btn" @click="fetchFaces" :disabled="loading">
          <i class="fas fa-sync-alt" :class="{ 'fa-spin': loading }"></i> 刷新
        </button>
      </div>
    </div>

    <div class="content">
      <div v-if="loading && faces.length === 0" class="loading-state">
        <i class="fas fa-spinner fa-spin"></i> 加载中...
      </div>

      <div v-else-if="faces.length === 0" class="empty-state">
        <i class="fas fa-user-slash"></i>
        <p>暂无注册人脸</p>
        <p class="hint">在对话中发送照片并说"这是[名字]"即可注册</p>
      </div>

      <div v-else class="faces-grid">
        <div v-for="face in faces" :key="face.id" class="face-card">
          <div class="face-avatar">
            <div class="avatar-placeholder">
              {{ face.name.charAt(0) }}
            </div>
          </div>
          <div class="face-info">
            <div class="face-name">{{ face.name }}</div>
            <div class="face-date">
              注册于 {{ formatDate(face.created_at) }}
            </div>
          </div>
          <button class="delete-btn" @click="deleteFace(face)" title="删除">
            <i class="fas fa-trash"></i>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import api from "../services/api";

const faces = ref([]);
const loading = ref(false);

const fetchFaces = async () => {
  loading.value = true;
  try {
    const data = await api.getFaces();
    if (data.success) {
      faces.value = data.faces;
    }
  } catch (error) {
    console.error("Failed to fetch faces:", error);
  } finally {
    loading.value = false;
  }
};

const deleteFace = async (face) => {
  if (!confirm(`确定要删除 "${face.name}" 的人脸数据吗？`)) return;

  try {
    const data = await api.deleteFace(face.id);
    if (data.success) {
      faces.value = faces.value.filter((f) => f.id !== face.id);
    } else {
      alert("删除失败: " + data.error);
    }
  } catch (error) {
    console.error("Failed to delete face:", error);
    alert("删除出错");
  }
};

const formatDate = (dateStr) => {
  if (!dateStr) return "未知时间";
  return new Date(dateStr).toLocaleDateString();
};

onMounted(() => {
  fetchFaces();
});
</script>

<style scoped>
.faces-view {
  height: 100%;
  display: flex;
  flex-direction: column;
  background-color: var(--bg-color);
  color: var(--text-color);
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid var(--border-color);
}

.header h2 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
}

.refresh-btn {
  background: none;
  border: 1px solid var(--border-color);
  color: var(--text-color);
  padding: 8px 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.refresh-btn:hover {
  background-color: var(--hover-color);
}

.content {
  flex: 1;
  overflow-y: auto;
}

.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 300px;
  color: var(--text-secondary);
}

.empty-state i {
  font-size: 3rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

.hint {
  font-size: 0.9rem;
  opacity: 0.7;
}

.faces-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 20px;
}

.face-card {
  background-color: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 15px;
  display: flex;
  align-items: center;
  gap: 15px;
  transition: transform 0.2s, box-shadow 0.2s;
}

.face-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.face-avatar {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background-color: var(--primary-color);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: bold;
  font-size: 1.2rem;
}

.face-info {
  flex: 1;
}

.face-name {
  font-weight: 600;
  font-size: 1.1rem;
  margin-bottom: 4px;
}

.face-date {
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.delete-btn {
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 8px;
  border-radius: 50%;
  transition: all 0.2s;
}

.delete-btn:hover {
  background-color: rgba(255, 0, 0, 0.1);
  color: #ff4d4f;
}
</style>
