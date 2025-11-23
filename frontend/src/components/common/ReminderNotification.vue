<template>
  <Teleport to="body">
    <div v-if="currentReminder" class="reminder-overlay">
      <div class="reminder-card">
        <div class="reminder-header">
          <span class="icon">⏰</span>
          <h3>{{ currentReminder.title || "提醒" }}</h3>
        </div>

        <div
          class="reminder-content"
          v-if="
            currentReminder.content &&
            currentReminder.content !== currentReminder.title
          "
        >
          {{ currentReminder.content }}
        </div>

        <div class="reminder-time">
          {{ formatTime(currentReminder.triggered_at) }}
        </div>

        <div class="auto-snooze-info" v-if="timeLeft > 0">
          <span class="timer-count">{{ timeLeft }}</span> 秒后自动稍后提醒 ({{
            snoozeDuration
          }}分钟)
        </div>

        <div class="reminder-actions">
          <div class="snooze-group">
            <select
              v-model="snoozeDuration"
              class="snooze-select"
              @change="resetAutoCloseTimer"
              @focus="resetAutoCloseTimer"
            >
              <option :value="5">5分钟</option>
              <option :value="10">10分钟</option>
              <option :value="30">30分钟</option>
              <option :value="60">1小时</option>
            </select>
            <button class="btn-snooze" @click="snoozeReminder">稍后提醒</button>
          </div>
          <button class="btn-confirm" @click="confirmReminder">我知道了</button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from "vue";
import { useWebSocket } from "@/composables/useWebSocket";
import api from "@/services/api";

const { on } = useWebSocket();
const currentReminder = ref(null);
const timeLeft = ref(60); // 60秒倒计时
// 从 localStorage 读取上次的选择，默认为 5
const savedDuration = localStorage.getItem("lastSnoozeDuration");
const snoozeDuration = ref(
  savedDuration ? parseInt(savedDuration, 10) || 5 : 5
);
let autoCloseTimer = null;
let currentAudio = null; // 存储当前播放的音频对象
let loopTimer = null; // 循环播放定时器
let isStopped = false; // 标记是否已停止播放

const formatTime = (isoString) => {
  if (!isoString) return "";
  return new Date(isoString).toLocaleString();
};

// 启动自动关闭倒计时
const startAutoCloseTimer = () => {
  stopAutoCloseTimer();
  const startTime = Date.now();
  const duration = 60 * 1000; // 60秒
  timeLeft.value = 60;

  autoCloseTimer = setInterval(() => {
    const elapsed = Date.now() - startTime;
    const remaining = Math.ceil((duration - elapsed) / 1000);
    timeLeft.value = remaining > 0 ? remaining : 0;

    if (elapsed >= duration) {
      // 倒计时结束，自动稍后提醒（默认5分钟）
      autoSnooze();
    }
  }, 1000);
};

// 停止倒计时（用户选择稍后时间时）
const resetAutoCloseTimer = () => {
  // 用户交互时重新开始倒计时
  if (currentReminder.value) {
    startAutoCloseTimer();
  }
};

const stopAutoCloseTimer = () => {
  if (autoCloseTimer) {
    clearInterval(autoCloseTimer);
    autoCloseTimer = null;
  }
};

// 停止播放
const stopPlayback = () => {
  isStopped = true; // 标记为已停止

  if (currentAudio) {
    currentAudio.pause();
    currentAudio.currentTime = 0;
    currentAudio.src = ""; // 强制断开源
    currentAudio = null;
  }
  if (loopTimer) {
    clearTimeout(loopTimer);
    loopTimer = null;
  }
}; // 播放提示音（循环播放直到停止）
const playSound = async () => {
  stopPlayback(); // 先停止之前的
  isStopped = false; // 重置停止标记

  const playSequence = async () => {
    if (!currentReminder.value || isStopped) return;

    try {
      // 1. 播放提示音 (Ding)
      await playFallbackSound();

      if (isStopped) return; // 再次检查

      // 2. 播放语音
      if (currentReminder.value) {
        // 优先使用后端生成的动态语音文本，如果没有则使用原始内容
        const textToSpeak =
          currentReminder.value.voice_text || currentReminder.value.content;

        if (textToSpeak) {
          try {
            const response = await api.synthesizeVoice(textToSpeak);

            if (isStopped) return; // 合成后再次检查

            if (response.success && response.audio_base64) {
              // 如果已经被停止了，就不播放了
              if (!currentReminder.value || isStopped) return;

              const audio = new Audio(
                `data:${response.mime};base64,${response.audio_base64}`
              );
              currentAudio = audio;

              await new Promise((resolve) => {
                audio.onended = resolve;
                audio.onerror = resolve; // 出错也继续
                audio.play().catch((e) => {
                  console.warn("Voice play failed:", e);
                  resolve();
                });
              });

              currentAudio = null;
            }
          } catch (voiceError) {
            console.warn("Voice synthesis failed:", voiceError);
          }
        }
      }

      // 3. 循环：如果还在显示，等待5秒后再次播放
      if (currentReminder.value && !isStopped) {
        loopTimer = setTimeout(playSequence, 5000);
      }
    } catch (error) {
      console.warn("Sound sequence failed:", error);
    }
  };

  playSequence();
};

// 备用：使用 Web Audio API 生成提示音
const playFallbackSound = async () => {
  return new Promise((resolve) => {
    try {
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      if (!AudioContext) {
        resolve();
        return;
      }

      const ctx = new AudioContext();

      // 尝试恢复音频上下文（解决浏览器自动播放策略限制）
      if (ctx.state === "suspended") {
        ctx.resume().catch(console.warn);
      }

      // Ding (高音)
      const osc1 = ctx.createOscillator();
      const gain1 = ctx.createGain();
      osc1.connect(gain1);
      gain1.connect(ctx.destination);

      osc1.type = "sine";
      osc1.frequency.setValueAtTime(880, ctx.currentTime); // A5
      gain1.gain.setValueAtTime(0.1, ctx.currentTime);
      gain1.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.5);

      osc1.start(ctx.currentTime);
      osc1.stop(ctx.currentTime + 0.5);

      // Dong (低音)
      const osc2 = ctx.createOscillator();
      const gain2 = ctx.createGain();
      osc2.connect(gain2);
      gain2.connect(ctx.destination);

      osc2.type = "sine";
      osc2.frequency.setValueAtTime(698.46, ctx.currentTime + 0.4); // F5
      gain2.gain.setValueAtTime(0.1, ctx.currentTime + 0.4);
      gain2.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 1.5);

      osc2.start(ctx.currentTime + 0.4);
      osc2.stop(ctx.currentTime + 1.5);

      // 约1.5秒后结束
      setTimeout(resolve, 1500);
    } catch (e) {
      console.error("Failed to play sound:", e);
      resolve();
    }
  });
};

const snoozeReminder = async () => {
  const reminder = currentReminder.value;
  if (!reminder) return;

  stopAutoCloseTimer();
  stopPlayback(); // 停止播放

  // 立即关闭弹窗
  currentReminder.value = null;

  const id = reminder.reminder_id;
  try {
    const duration = parseInt(snoozeDuration.value, 10) || 5;
    // 保存用户的选择到 localStorage
    localStorage.setItem("lastSnoozeDuration", duration);

    await api.snoozeReminder(id, duration);
    console.log(`Reminder ${id} snoozed for ${duration} minutes`);
  } catch (error) {
    console.error("Failed to snooze reminder:", error);
  }
};

// 自动稍后提醒（超时未操作）
const autoSnooze = async () => {
  const reminder = currentReminder.value;
  if (!reminder) return;

  stopAutoCloseTimer();
  stopPlayback();

  currentReminder.value = null;
  const id = reminder.reminder_id;

  try {
    // 使用用户选择的时间（或默认值）
    const duration = parseInt(snoozeDuration.value, 10) || 5;
    // 自动触发也保存这个偏好（或者不保存？保存比较好，保持一致性）
    localStorage.setItem("lastSnoozeDuration", duration);

    await api.snoozeReminder(id, duration);
    console.log(
      `Reminder ${id} auto-snoozed for ${duration} minutes due to inactivity`
    );
  } catch (error) {
    console.error("Failed to auto-snooze reminder:", error);
  }
};

const confirmReminder = async () => {
  stopAutoCloseTimer();
  stopPlayback(); // 停止播放

  const reminder = currentReminder.value;
  if (!reminder) return;

  // 立即关闭弹窗（乐观更新），防止卡顿
  currentReminder.value = null;

  const id = reminder.reminder_id;

  try {
    // 调用后端API确认提醒
    await api.confirmReminder(id);
    console.log(`Reminder ${id} confirmed`);

    // 发送全局事件通知列表刷新
    window.dispatchEvent(new CustomEvent("reminder-confirmed"));
  } catch (error) {
    console.error("Failed to confirm reminder:", error);
    // 如果失败了，可能需要提示用户，但暂时不重新打开弹窗，以免打扰
  }
};

let removeListener = null;

onMounted(() => {
  removeListener = on((data) => {
    if (data.type === "reminder") {
      console.log("Received reminder:", data);
      currentReminder.value = data.data;
      // 每次弹窗时，重新读取 localStorage 确保是最新的偏好
      const saved = localStorage.getItem("lastSnoozeDuration");
      if (saved) {
        snoozeDuration.value = parseInt(saved, 10);
      }
      playSound();
      startAutoCloseTimer();
    } else if (data.type === "reminder_deleted") {
      // 如果当前显示的提醒被删除了，关闭弹窗
      if (
        currentReminder.value &&
        currentReminder.value.reminder_id === data.data.reminder_id
      ) {
        stopPlayback();
        stopAutoCloseTimer();
        currentReminder.value = null;
      }
    }
  });
});

onUnmounted(() => {
  stopPlayback();
  stopAutoCloseTimer();
  if (removeListener) removeListener();
});
</script>

<style scoped>
.reminder-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 10000;
  backdrop-filter: blur(4px);
  animation: fadeIn 0.3s ease;
}

.reminder-card {
  background: var(--card-bg, #fff);
  padding: 30px;
  border-radius: 16px;
  width: 90%;
  max-width: 400px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
  text-align: center;
  animation: slideUp 0.3s ease;
  border: 1px solid var(--border-color, #eee);
}

.reminder-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  margin-bottom: 15px;
  color: var(--primary-color, #4caf50);
}

.reminder-header .icon {
  font-size: 2em;
}

.reminder-header h3 {
  margin: 0;
  font-size: 1.5em;
}

.reminder-content {
  font-size: 1.2em;
  margin-bottom: 20px;
  color: var(--text-primary, #333);
  line-height: 1.5;
}

.reminder-time {
  font-size: 0.9em;
  color: var(--text-secondary, #666);
  margin-bottom: 15px;
}

.auto-snooze-info {
  font-size: 0.9em;
  color: var(--warning-color, #ff9800);
  margin-bottom: 20px;
  font-weight: 500;
  background: rgba(255, 152, 0, 0.1);
  padding: 8px 16px;
  border-radius: 20px;
  display: inline-block;
}

.timer-count {
  font-weight: bold;
  font-size: 1.1em;
}

.reminder-actions {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
}

.snooze-group {
  display: flex;
  gap: 8px;
  align-items: center;
}

.snooze-select {
  padding: 10px;
  border-radius: 20px;
  border: 1px solid #ddd;
  background: #f9f9f9;
  font-size: 0.9em;
  outline: none;
  cursor: pointer;
}

.btn-confirm {
  background: var(--primary-color, #4caf50);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 25px;
  font-size: 1em;
  cursor: pointer;
  transition: transform 0.1s, box-shadow 0.2s;
  min-width: 120px;
  width: 100%;
}

.btn-snooze {
  background: #f5f5f5;
  color: #666;
  border: 1px solid #ddd;
  padding: 10px 20px;
  border-radius: 20px;
  font-size: 0.9em;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.btn-snooze:hover {
  background: #e0e0e0;
  color: #333;
}

.btn-confirm:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3);
}

.btn-confirm:active {
  transform: translateY(0);
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
    transform: translateY(20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}
</style>
