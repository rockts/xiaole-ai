<template>
  <Transition name="selector-fade">
    <div
      v-if="visible"
      class="voice-selector-overlay"
      @click.self="handleClose"
    >
      <div class="voice-selector-content">
        <!-- 渐变定义（一次渲染，不占布局） -->
        <svg width="0" height="0" style="position: absolute">
          <defs>
            <linearGradient
              id="gradient-vale"
              x1="0%"
              y1="0%"
              x2="100%"
              y2="100%"
            >
              <stop offset="0%" stop-color="#00C6FF" />
              <stop offset="100%" stop-color="#0072FF" />
            </linearGradient>
            <linearGradient
              id="gradient-juniper"
              x1="0%"
              y1="0%"
              x2="100%"
              y2="100%"
            >
              <stop offset="0%" stop-color="#667eea" />
              <stop offset="100%" stop-color="#764ba2" />
            </linearGradient>
            <linearGradient
              id="gradient-arbor"
              x1="0%"
              y1="0%"
              x2="100%"
              y2="100%"
            >
              <stop offset="0%" stop-color="#34D399" />
              <stop offset="100%" stop-color="#059669" />
            </linearGradient>
          </defs>
        </svg>
        <h3 class="selector-title">选择一种语音</h3>

        <div class="voice-carousel">
          <button
            class="carousel-arrow left"
            @click="prevVoice"
            :disabled="currentIndex === 0"
          >
            <svg
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            >
              <polyline points="15 18 9 12 15 6"></polyline>
            </svg>
          </button>

          <div class="voice-option">
            <div class="voice-avatar-small">
              <svg width="80" height="80" viewBox="0 0 24 24" fill="none">
                <circle
                  cx="12"
                  cy="12"
                  r="10"
                  :fill="voices[currentIndex].color"
                />
              </svg>
            </div>
            <div class="voice-name">{{ voices[currentIndex].name }}</div>
            <div class="voice-desc">{{ voices[currentIndex].description }}</div>
          </div>

          <button
            class="carousel-arrow right"
            @click="nextVoice"
            :disabled="currentIndex === voices.length - 1"
          >
            <svg
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            >
              <polyline points="9 18 15 12 9 6"></polyline>
            </svg>
          </button>
        </div>

        <div class="selector-actions">
          <button class="selector-btn primary" @click="handleConfirm">
            开始新聊天
          </button>
          <button class="selector-btn secondary" @click="handleClose">
            取消
          </button>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { ref, watch } from "vue";

const props = defineProps({
  visible: {
    type: Boolean,
    default: false,
  },
  currentVoice: {
    type: String,
    default: "juniper",
  },
});

const emit = defineEmits(["update:visible", "select"]);

const voices = [
  {
    id: "vale",
    name: "Vale",
    description: "熙明好听",
    color: "url(#gradient-vale)",
  },
  {
    id: "juniper",
    name: "Juniper",
    description: "开放稳达",
    color: "url(#gradient-juniper)",
  },
  {
    id: "arbor",
    name: "Arbor",
    description: "在慢阳时，多才多艺",
    color: "url(#gradient-arbor)",
  },
];

const currentIndex = ref(1); // 默认选择 Juniper

watch(
  () => props.currentVoice,
  (val) => {
    const index = voices.findIndex((v) => v.id === val);
    if (index !== -1) {
      currentIndex.value = index;
    }
  },
  { immediate: true }
);

const prevVoice = () => {
  if (currentIndex.value > 0) {
    currentIndex.value--;
  }
};

const nextVoice = () => {
  if (currentIndex.value < voices.length - 1) {
    currentIndex.value++;
  }
};

const handleConfirm = () => {
  emit("select", voices[currentIndex.value].id);
  emit("update:visible", false);
};

const handleClose = () => {
  emit("update:visible", false);
};
</script>

<style scoped>
.voice-selector-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
}

.voice-selector-content {
  background: linear-gradient(135deg, #2a2a2a 0%, #3a3a3a 100%);
  border-radius: 24px;
  padding: 48px 40px;
  max-width: 560px;
  width: 90%;
  box-shadow: 0 24px 64px rgba(0, 0, 0, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.1);
  position: relative;
}

.selector-title {
  font-size: 24px;
  font-weight: 600;
  color: #fff;
  text-align: center;
  margin: 0 0 40px 0;
}

.voice-carousel {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 24px;
  margin-bottom: 40px;
}

.carousel-arrow {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s;
}

.carousel-arrow:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.15);
  transform: scale(1.05);
}

.carousel-arrow:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.voice-option {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  min-width: 240px;
  padding: 12px 8px;
  border-radius: 16px;
  transition: all 0.25s ease;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: linear-gradient(
    180deg,
    rgba(255, 255, 255, 0.04) 0%,
    rgba(255, 255, 255, 0.02) 100%
  );
}

.voice-avatar-small {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.05);
  border: 2px solid rgba(255, 255, 255, 0.12);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35),
    inset 0 0 24px rgba(255, 255, 255, 0.06);
}

.voice-name {
  font-size: 20px;
  font-weight: 600;
  color: #fff;
  letter-spacing: 0.2px;
}

.voice-desc {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.6);
  text-align: center;
}

.selector-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.selector-btn {
  width: 100%;
  padding: 16px;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
  border: none;
}

.selector-btn.primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
}

.selector-btn.primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4);
}

.selector-btn.secondary {
  background: transparent;
  color: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.selector-btn.secondary:hover {
  background: rgba(255, 255, 255, 0.05);
}

.selector-fade-enter-active,
.selector-fade-leave-active {
  transition: opacity 0.3s ease;
}

.selector-fade-enter-from,
.selector-fade-leave-to {
  opacity: 0;
}

.selector-fade-enter-active .voice-selector-content,
.selector-fade-leave-active .voice-selector-content {
  transition: transform 0.3s ease;
}

.selector-fade-enter-from .voice-selector-content,
.selector-fade-leave-to .voice-selector-content {
  transform: scale(0.95);
}
</style>

<style>
/* SVG gradients */
svg defs {
  position: absolute;
}
</style>
