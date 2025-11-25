<template>
  <Transition name="voice-fade">
    <div v-if="visible" class="voice-mode-dialog" @click.self="handleClose">
      <div class="voice-content">
        <!-- 顶部操作栏 -->
        <div class="voice-header">
          <button class="voice-selector-btn" @click="showVoiceSelector = true">
            <svg
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            >
              <circle cx="12" cy="12" r="3"></circle>
              <path
                d="M12 1v6m0 6v6m-5.2-5.2l4.2 4.2m0-8.4l4.2-4.2m-8.4 0l4.2 4.2m0 0l4.2 4.2"
              ></path>
            </svg>
          </button>
        </div>

        <!-- 中央AI头像区域 -->
        <div class="voice-avatar-area">
          <div class="avatar-wrapper">
            <div class="avatar-brain" :style="pulseStyle">
              <img class="ai-avatar-img" src="/logo-xiaole.svg" alt="AI头像" />
              <div class="neural-glow" :class="{ speaking: isSpeaking }"></div>
            </div>
          </div>
          <!-- 简洁语音历史面板 -->
          <div class="voice-history" v-if="voiceHistory.length">
            <div class="voice-history-list">
              <div
                v-for="m in voiceHistory"
                :key="m.id"
                class="vh-item"
                :class="m.role"
              >
                <span
                  class="vh-role"
                  v-text="m.role === 'user' ? '我' : '小乐'"
                ></span>
                <span class="vh-text" v-text="truncate(m.content)"></span>
              </div>
            </div>
          </div>
        </div>

        <!-- 底部操作区 -->
        <div class="voice-footer">
          <button
            class="voice-action-btn mic-btn"
            :class="{ active: isListening }"
            @click="toggleListening"
          >
            <svg
              v-if="!isListening"
              width="32"
              height="32"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            >
              <path
                d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"
              ></path>
              <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
              <line x1="12" y1="19" x2="12" y2="23"></line>
              <line x1="8" y1="23" x2="16" y2="23"></line>
            </svg>
            <svg
              v-else
              width="32"
              height="32"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            >
              <rect x="7" y="4" width="10" height="16" rx="5" />
              <line x1="12" y1="19" x2="12" y2="23"></line>
              <line x1="8" y1="23" x2="16" y2="23"></line>
            </svg>
          </button>

          <button class="voice-action-btn close-btn" @click="handleClose">
            <svg
              width="32"
              height="32"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            >
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>
      </div>

      <!-- 语音选择器 -->
      <VoiceSelector
        :visible="showVoiceSelector"
        :current-voice="currentVoice"
        @update:visible="showVoiceSelector = $event"
        @select="handleVoiceSelect"
      />
    </div>
  </Transition>
</template>

<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount } from "vue";
import { useChatStore } from "@/stores/chat";
import VoiceSelector from "./VoiceSelector.vue";

const props = defineProps({
  visible: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(["update:visible", "message", "voice-change"]);

const showVoiceSelector = ref(false);
const isListening = ref(false);
const isSpeaking = ref(false);
const audioLevel = ref(0);
const currentVoice = ref("juniper");
const sessionStartTime = ref(null);

let recognition = null;
let audioContext = null;
let analyser = null;
let animationFrame = null;
let mediaStream = null;
let levelFrame = null;

// 引入全局消息用于展示语音历史
const chatStore = useChatStore();
const voiceHistory = computed(() => {
  const src = chatStore.messages || [];
  // 过滤最近的语音相关轮次（用户voice消息与其后的assistant回复）
  const filtered = [];
  for (let i = src.length - 1; i >= 0 && filtered.length < 20; i--) {
    const m = src[i];
    if (
      m.messageType === "voice" ||
      (m.role === "assistant" &&
        m.content &&
        m.messageType !== "voice-session-end")
    ) {
      filtered.unshift({ id: m.id, role: m.role, content: m.content });
    }
  }
  return filtered;
});

const truncate = (t) => {
  if (!t) return "";
  return t.length > 38 ? t.slice(0, 38) + "…" : t;
};

// 电话模式：不显示状态文本
const statusText = computed(() => "");

// 基于 audioLevel 计算头像脉冲样式
const pulseStyle = computed(() => {
  const lvl = Math.min(1, audioLevel.value / 100); // 归一化
  const scale = 1 + lvl * 0.15; // 最大 15% 放大
  const shadowStrength = (lvl * 0.4).toFixed(2);
  return {
    transform: `scale(${scale})`,
    boxShadow: `0 0 ${20 + lvl * 25}px rgba(102,126,234,${shadowStrength})`,
  };
});

// 初始化语音识别
const initRecognition = () => {
  if ("webkitSpeechRecognition" in window || "SpeechRecognition" in window) {
    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();
    recognition.lang = "zh-CN";
    // 语音电话式：一句一停，尽快出最终结果
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    recognition.onresult = (event) => {
      let finalTranscript = "";
      for (let i = event.resultIndex; i < event.results.length; ++i) {
        const res = event.results[i];
        if (res.isFinal) {
          finalTranscript += res[0].transcript;
        }
      }
      if (finalTranscript) {
        emit("message", {
          type: "voice",
          content: finalTranscript,
          duration: 0,
        });
      }
    };

    recognition.onerror = (event) => {
      console.error("Speech recognition error", event.error);
      isListening.value = false;
      stopAudioVisualization();
    };

    recognition.onend = () => {
      if (isListening.value) {
        try {
          recognition.start();
        } catch (e) {
          console.error("Restart recognition failed:", e);
          isListening.value = false;
          stopAudioVisualization();
        }
      }
    };
    // 语音结束尽快提交一次
    recognition.onspeechend = () => {
      try {
        recognition.stop();
      } catch (e) {}
    };
  }
};

// 音频可视化
const startAudioVisualization = async () => {
  // 不再做mic按钮动画，仅保留音量数据
  try {
    mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
    audioContext = new (window.AudioContext || window.webkitAudioContext)();
    analyser = audioContext.createAnalyser();
    analyser.fftSize = 256;
    const source = audioContext.createMediaStreamSource(mediaStream);
    source.connect(analyser);
    const dataArray = new Uint8Array(analyser.frequencyBinCount);
    const updateLevel = () => {
      analyser.getByteFrequencyData(dataArray);
      // 取前 1/4 频段平均作为音量粗略值
      const slice = dataArray.slice(0, dataArray.length / 4);
      const sum = slice.reduce((a, b) => a + b, 0);
      audioLevel.value = sum / slice.length; // 0-255
      levelFrame = requestAnimationFrame(updateLevel);
    };
    updateLevel();
  } catch (e) {
    console.error("Audio visualization failed:", e);
  }
};

const stopAudioVisualization = () => {
  if (animationFrame) {
    cancelAnimationFrame(animationFrame);
    animationFrame = null;
  }
  if (levelFrame) {
    cancelAnimationFrame(levelFrame);
    levelFrame = null;
  }
  if (mediaStream) {
    mediaStream.getTracks().forEach((track) => track.stop());
    mediaStream = null;
  }
  if (audioContext) {
    audioContext.close();
    audioContext = null;
  }
  audioLevel.value = 0;
};

const toggleListening = () => {
  if (!recognition) {
    alert("您的浏览器不支持语音识别功能，请使用 Chrome 或 Edge 浏览器。");
    return;
  }

  if (isListening.value) {
    recognition.stop();
    isListening.value = false;
    stopAudioVisualization();
  } else {
    try {
      recognition.start();
      isListening.value = true;
      startAudioVisualization();
    } catch (e) {
      console.error("Start recognition failed:", e);
    }
  }
};

const handleClose = () => {
  if (isListening.value) {
    recognition?.stop();
    isListening.value = false;
    stopAudioVisualization();
  }
  // 计算本次语音会话时长
  let duration = 0;
  if (sessionStartTime.value) {
    duration = Math.max(
      0,
      Math.floor((Date.now() - sessionStartTime.value) / 1000)
    );
  }
  // 发出会话结束事件，供父组件渲染结束标签
  emit("session-end", { duration });
  emit("update:visible", false);
};

const handleVoiceSelect = (voice) => {
  currentVoice.value = voice;
  emit("voice-change", voice);
};

watch(
  () => props.visible,
  (val) => {
    if (val) {
      initRecognition();
      // 进入对话框即自动开始监听
      try {
        recognition?.start();
        isListening.value = true;
        startAudioVisualization();
        sessionStartTime.value = Date.now();
      } catch (e) {
        console.error("Auto start recognition failed:", e);
      }
    } else {
      if (isListening.value) {
        recognition?.stop();
        isListening.value = false;
        stopAudioVisualization();
      }
    }
  }
);

onMounted(() => {
  if (props.visible) {
    initRecognition();
    // 若初始即可见，则自动开始监听
    try {
      recognition?.start();
      isListening.value = true;
      startAudioVisualization();
      sessionStartTime.value = Date.now();
    } catch (e) {
      console.error("Auto start on mount failed:", e);
    }
  }
});

onBeforeUnmount(() => {
  if (recognition) {
    recognition.stop();
  }
  stopAudioVisualization();
});

// 暴露方法和会话时长供父组件调用
defineExpose({
  startSpeaking: () => {
    isSpeaking.value = true;
  },
  stopSpeaking: () => {
    isSpeaking.value = false;
  },
  getSessionDuration: () => {
    if (!sessionStartTime.value) return 0;
    return Math.max(
      0,
      Math.floor((Date.now() - sessionStartTime.value) / 1000)
    );
  },
});
</script>

<style scoped>
.voice-mode-dialog {
  position: fixed;
  inset: 0;
  background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
  z-index: 3000;
  display: flex;
  align-items: center;
  justify-content: center;
}

.voice-mode-dialog::before {
  content: "";
  position: absolute;
  inset: 0;
  background: radial-gradient(
    80% 60% at 50% 40%,
    rgba(255, 255, 255, 0.06) 0%,
    rgba(0, 0, 0, 0) 60%
  );
  pointer-events: none;
}

.voice-content {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  position: relative;
}

.voice-header {
  position: absolute;
  top: 20px;
  right: 20px;
  z-index: 10;
}

.voice-selector-btn {
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
  backdrop-filter: blur(10px);
}

.voice-selector-btn:hover {
  background: rgba(255, 255, 255, 0.15);
  transform: scale(1.05);
}

.voice-avatar-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 32px;
}

.voice-history {
  width: 320px;
  max-height: 160px;
  overflow-y: auto;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 12px;
  padding: 8px 10px;
  font-size: 13px;
  backdrop-filter: blur(8px);
}
.voice-history-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.vh-item {
  display: flex;
  gap: 6px;
  line-height: 1.3;
}
.vh-item.user .vh-role {
  color: #ffd479;
}
.vh-item.assistant .vh-role {
  color: #76b6ff;
}
.vh-role {
  font-weight: 600;
}
.vh-text {
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 电话模式已移除字幕区域 */

.avatar-wrapper {
  position: relative;
  width: 200px;
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-brain {
  position: relative;
  width: 160px;
  height: 160px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.12s linear, box-shadow 0.2s ease;
}

.ai-avatar-img {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
  background: #fff;
  box-shadow: inset 0 0 12px rgba(0, 0, 0, 0.3);
}

.neural-glow {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  pointer-events: none;
  background: radial-gradient(
    circle at 50% 50%,
    rgba(102, 126, 234, 0.25),
    transparent 60%
  );
  opacity: 0;
  transition: opacity 0.25s ease;
}
.neural-glow.speaking {
  opacity: 0.9;
}

.voice-status-text {
  font-size: 18px;
  color: rgba(255, 255, 255, 0.8);
  font-weight: 500;
  text-align: center;
  letter-spacing: 0.2px;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.35);
}

.voice-footer {
  padding: 40px;
  display: flex;
  justify-content: center;
  gap: 40px;
}

.voice-action-btn {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.35);
  backdrop-filter: blur(6px);
}

.mic-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
}

.mic-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4);
}

.mic-btn.active {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  box-shadow: 0 10px 28px rgba(245, 87, 108, 0.45);
}

.close-btn {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #fff;
  backdrop-filter: blur(10px);
}

.close-btn:hover {
  background: rgba(255, 77, 77, 0.2);
  border-color: rgba(255, 77, 77, 0.4);
  transform: translateY(-2px);
}

.voice-fade-enter-active,
.voice-fade-leave-active {
  transition: opacity 0.3s ease;
}

.voice-fade-enter-from,
.voice-fade-leave-to {
  opacity: 0;
}

@media (max-width: 520px) {
  .avatar-wrapper {
    width: 160px;
    height: 160px;
  }
  .ai-avatar-img {
    width: 130px;
    height: 130px;
  }
  .voice-footer {
    padding: 24px;
    gap: 24px;
  }
  .voice-action-btn {
    width: 64px;
    height: 64px;
  }
  .voice-selector-btn {
    width: 44px;
    height: 44px;
  }
}
</style>
