<template>
  <div
    class="chat-view"
    :class="{ empty: isEmptyChat }"
    @dragover.prevent
    @dragenter.prevent="handleDragEnter"
    @dragleave.prevent="handleDragLeave"
    @drop.prevent="handleDrop"
  >
    <!-- 全屏拖拽遮罩 -->
    <div v-if="isDraggingFile" class="drag-overlay">
      <div class="drag-content">
        <div class="drag-icon">
          <svg
            width="64"
            height="64"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="1.5"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
            <polyline points="17 8 12 3 7 8"></polyline>
            <line x1="12" y1="3" x2="12" y2="15"></line>
          </svg>
        </div>
        <div class="drag-title">在此处拖放文件</div>
        <div class="drag-subtitle">添加任意内容到对话中</div>
      </div>
    </div>

    <!-- 空状态问候语 -->
    <div v-if="isEmptyChat" class="welcome-message">
      <div class="welcome-icon">👋</div>
      <h2 class="welcome-title">{{ currentGreeting }}</h2>
    </div>

    <div
      class="chat-container"
      ref="chatContainer"
      :style="{ visibility: isLoadingSession ? 'hidden' : 'visible' }"
    >
      <div class="chat-inner">
        <div
          v-for="(message, idx) in messages"
          :key="message.id"
          class="message"
          :class="[
            message.role,
            {
              'new-group':
                idx === 0 || messages[idx - 1]?.role !== message.role,
            },
          ]"
        >
          <img
            v-if="message.image_path"
            :src="formatImagePath(message.image_path)"
            alt="图片"
            class="message-image"
            @click="openImage(formatImagePath(message.image_path))"
          />
          <template v-if="message.role === 'assistant'">
            <template v-if="message.status === 'thinking'">
              <div class="thinking-wrapper">
                <div class="thinking-dot"></div>
              </div>
            </template>
            <template v-else>
              <div
                class="md-content"
                :class="{ typing: message.status === 'typing' }"
                v-html="renderMarkdown(getDisplayContent(message))"
              ></div>

              <!-- 相关阅读卡片 -->
              <div v-if="hasRelatedReadings(message)" class="related-reading">
                <div class="related-title">相关阅读</div>
                <div class="related-cards">
                  <a
                    v-for="(item, i) in getRelatedReadings(message).slice(0, 3)"
                    :key="i"
                    :href="item.href"
                    target="_blank"
                    rel="noopener noreferrer"
                    class="related-card"
                  >
                    <div class="card-image-area">
                      <img
                        :src="`https://www.google.com/s2/favicons?domain=${getDomain(
                          item.href
                        )}&sz=128`"
                        class="card-cover-icon"
                        @error="handleFaviconError"
                      />
                    </div>
                    <div class="card-content">
                      <div class="card-source">
                        <img
                          :src="`https://www.google.com/s2/favicons?domain=${getDomain(
                            item.href
                          )}&sz=32`"
                          class="favicon"
                          @error="handleFaviconError"
                        />
                        <span class="domain-text">{{
                          getDomain(item.href)
                        }}</span>
                      </div>
                      <div class="card-title" :title="item.title">
                        {{ item.title }}
                      </div>
                    </div>
                  </a>
                </div>
              </div>
            </template>
          </template>
          <template v-else>
            <div class="user-bubble" v-if="editingMessageId !== message.id">
              <div
                class="md-content"
                v-html="renderMarkdown(message.content)"
              ></div>
            </div>
            <!-- 编辑模式 -->
            <div v-else class="edit-mode-container">
              <textarea
                :id="`edit-textarea-${message.id}`"
                v-model="editingContent"
                class="edit-textarea"
                @input="autoResizeTextarea"
                @keydown.enter.exact.prevent
                @keydown.enter.ctrl="saveEdit(message)"
                @keydown.enter.meta="saveEdit(message)"
              ></textarea>
              <div class="edit-actions">
                <button class="btn-edit-action cancel" @click="cancelEdit">
                  取消
                </button>
                <button class="btn-edit-action save" @click="saveEdit(message)">
                  发送
                </button>
              </div>
            </div>
          </template>

          <div
            class="message-toolbar"
            v-if="
              (message.role === 'user' || message.status === 'done') &&
              editingMessageId !== message.id
            "
          >
            <button
              v-if="message.role === 'user'"
              class="toolbar-icon"
              @click.stop="editMessage(message)"
              title="编辑"
            >
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
                <path
                  d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"
                ></path>
                <path
                  d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"
                ></path>
              </svg>
            </button>
            <button
              class="toolbar-icon"
              @click.stop="copyMessage(message)"
              :title="copiedMessageId === message.id ? '已复制' : '复制'"
            >
              <!-- 复制成功图标 (对号) -->
              <svg
                v-if="copiedMessageId === message.id"
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
                class="text-success"
              >
                <polyline points="20 6 9 17 4 12"></polyline>
              </svg>
              <!-- 默认复制图标 -->
              <svg
                v-else
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                <path
                  d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"
                ></path>
              </svg>
            </button>
            <button
              v-if="
                message.role === 'assistant' &&
                feedbackState.get(message.id) !== 'down'
              "
              class="toolbar-icon"
              :class="{ active: feedbackState.get(message.id) === 'up' }"
              @click.stop="feedbackMessage(message, 'up')"
              title="有帮助"
            >
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
                <path d="M7 10v12"></path>
                <path
                  d="M15 5.88 14 10h5.83a2 2 0 0 1 1.92 2.56l-2.33 8A2 2 0 0 1 17.5 22H4a2 2 0 0 1-2-2v-8a2 2 0 0 1 2-2h2.76a2 2 0 0 0 1.79-1.11L12 2h0a3.13 3.13 0 0 1 3 3.88Z"
                ></path>
              </svg>
            </button>
            <button
              v-if="
                message.role === 'assistant' &&
                feedbackState.get(message.id) !== 'up'
              "
              class="toolbar-icon"
              :class="{ active: feedbackState.get(message.id) === 'down' }"
              @click.stop="feedbackMessage(message, 'down')"
              title="不太好"
            >
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
                <path d="M17 14V2"></path>
                <path
                  d="M9 18.12 10 14H4.17a2 2 0 0 1-1.92-2.56l2.33-8A2 2 0 0 1 6.5 2H20a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2h-2.76a2 2 0 0 0-1.79 1.11L12 22h0a3.13 3.13 0 0 1-3-3.88Z"
                ></path>
              </svg>
            </button>
            <button
              v-if="message.role === 'assistant'"
              class="toolbar-icon"
              :class="{ active: isSpeaking(message.id) }"
              @click.stop="toggleSpeak(message)"
              title="朗读"
            >
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
                <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon>
                <path d="M15.54 8.46a5 5 0 0 1 0 7.07"></path>
                <path d="M19.07 4.93a10 10 0 0 1 0 14.14"></path>
              </svg>
            </button>
            <button
              v-if="message.role === 'assistant'"
              class="toolbar-icon"
              @click.stop="regenerateMessage(message)"
              title="重新生成"
            >
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
                <polyline points="23 4 23 10 17 10"></polyline>
                <polyline points="1 20 1 14 7 14"></polyline>
                <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10"></path>
                <path d="M20.49 15a9 9 0 0 1-14.85 3.36L1 14"></path>
              </svg>
            </button>
            <button
              v-if="message.role === 'assistant'"
              class="toolbar-icon"
              @click.stop="shareMessage(message)"
              title="分享"
            >
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
                <circle cx="18" cy="5" r="3"></circle>
                <circle cx="6" cy="12" r="3"></circle>
                <circle cx="18" cy="19" r="3"></circle>
                <line x1="8.59" y1="13.51" x2="15.42" y2="17.49"></line>
                <line x1="15.41" y1="6.51" x2="8.59" y2="10.49"></line>
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 回到底部按钮 -->
    <button
      v-show="showScrollToBottom"
      class="scroll-to-bottom"
      @click="scrollToBottomSmooth"
      aria-label="回到底部"
    >
      <svg
        width="24"
        height="24"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2.5"
        stroke-linecap="round"
        stroke-linejoin="round"
      >
        <line x1="12" y1="5" x2="12" y2="19"></line>
        <polyline points="6 13 12 19 18 13"></polyline>
      </svg>
    </button>

    <!-- 图片预览遮罩 -->
    <div
      v-if="imagePreviewUrl"
      class="image-preview-overlay"
      @click.self="closeImagePreview"
      @wheel.prevent="handleZoom"
    >
      <div class="preview-controls" @click.stop>
        <button class="control-btn" @click="zoomOut" title="缩小">
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
            <line x1="5" y1="12" x2="19" y2="12"></line>
          </svg>
        </button>
        <span class="zoom-level">{{ Math.round(imageScale * 100) }}%</span>
        <button class="control-btn" @click="zoomIn" title="放大">
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
            <line x1="12" y1="5" x2="12" y2="19"></line>
            <line x1="5" y1="12" x2="19" y2="12"></line>
          </svg>
        </button>
        <div class="divider"></div>
        <button
          class="control-btn close-btn"
          @click="closeImagePreview"
          title="关闭"
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
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      </div>
      <img
        :src="imagePreviewUrl"
        alt="预览图"
        class="image-preview"
        :style="{
          transform: `translate(${imageTranslate.x}px, ${imageTranslate.y}px) scale(${imageScale})`,
          cursor: isDragging ? 'grabbing' : 'grab',
        }"
        @mousedown="startDrag"
        @mousemove="onDrag"
        @mouseup="stopDrag"
        @mouseleave="stopDrag"
        @touchstart="handleTouchStart"
        @touchmove="handleTouchMove"
        @touchend="handleTouchEnd"
        @click.stop
        draggable="false"
      />
    </div>

    <!-- 文本选中浮动按钮 -->
    <Teleport to="body">
      <div
        v-if="showQuoteBtn"
        class="quote-float-btn"
        :style="{ top: `${quoteBtnPos.top}px`, left: `${quoteBtnPos.left}px` }"
        @mousedown.prevent="applyQuote"
      >
        <span
          style="
            font-size: 32px;
            line-height: 0.5;
            margin-right: 4px;
            font-family: Georgia, serif;
            font-weight: 900;
            display: inline-block;
            transform: translateY(4px);
          "
          >”</span
        >
        询问小乐
      </div>
    </Teleport>

    <div class="input-container">
      <div class="input-wrapper">
        <!-- 引用预览条 -->
        <div v-if="quoteText" class="quote-preview-bar">
          <div class="quote-content">
            <svg
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
              class="quote-icon"
            >
              <polyline points="15 10 20 15 15 20"></polyline>
              <path d="M4 4v7a4 4 0 0 0 4 4h12"></path>
            </svg>
            <div class="quote-text">
              “{{
                quoteText.replace(/\n/g, " ").substring(0, 100) +
                (quoteText.length > 100 ? "..." : "")
              }}”
            </div>
          </div>
          <button class="close-quote-btn" @click="clearQuote">
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
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>

        <!-- 图片预览条 (待发送) -->
        <div v-if="pendingPreviewUrl" class="input-preview-area">
          <div class="preview-card">
            <img
              :src="pendingPreviewUrl"
              class="preview-image"
              alt="待发送图片"
            />
            <button class="preview-close-btn" @click="clearPendingFile">
              <svg
                width="14"
                height="14"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
              </svg>
            </button>
          </div>
        </div>

        <div class="input-controls">
          <button class="icon-btn" @click="handleUpload" title="附件">
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
              <line x1="12" y1="5" x2="12" y2="19"></line>
              <line x1="5" y1="12" x2="19" y2="12"></line>
            </svg>
          </button>

          <div
            ref="messageInput"
            class="message-editor"
            contenteditable="true"
            @keydown.enter="handleEnter"
            @input="handleInput"
            data-placeholder="给 小乐 AI 发送消息..."
          ></div>

          <button
            class="icon-btn"
            :class="{ recording: isRecording }"
            @click="handleVoiceInput"
            title="语音输入"
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
              <path
                d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"
              ></path>
              <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
              <line x1="12" y1="19" x2="12" y2="23"></line>
              <line x1="8" y1="23" x2="16" y2="23"></line>
            </svg>
          </button>

          <button
            class="icon-btn voice-mode-btn"
            :class="{
              active: isVoiceMode && buttonMode === 'voice-mode',
              'send-mode': buttonMode === 'send',
              'stop-mode': buttonMode === 'stop',
            }"
            @click="handleMainButton"
            :title="
              buttonMode === 'send'
                ? '发送消息'
                : buttonMode === 'stop'
                ? '停止生成'
                : '语音模式'
            "
          >
            <!-- 发送图标 (向上箭头) -->
            <svg
              v-if="buttonMode === 'send'"
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="#000"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <line x1="12" y1="5" x2="12" y2="19" />
              <polyline points="6,11 12,5 18,11" />
            </svg>

            <!-- 停止图标 -->
            <svg
              v-else-if="buttonMode === 'stop'"
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="currentColor"
            >
              <rect x="6" y="6" width="12" height="12" rx="2"></rect>
            </svg>

            <!-- 语音模式图标 -->
            <svg
              v-else
              width="32"
              height="32"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="1.5"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <circle
                cx="12"
                cy="12"
                r="11.5"
                fill="currentColor"
                opacity="0.15"
              ></circle>
              <line x1="8" y1="13.5" x2="8" y2="10.5"></line>
              <line x1="10.5" y1="15" x2="10.5" y2="9"></line>
              <line x1="13.5" y1="15" x2="13.5" y2="9"></line>
              <line x1="16" y1="13.5" x2="16" y2="10.5"></line>
            </svg>
          </button>
        </div>
      </div>
    </div>

    <input
      ref="fileInput"
      type="file"
      accept="image/*,.pdf,.docx,.txt,.md,.markdown"
      style="display: none"
      @change="handleFileChange"
    />

    <!-- 反馈弹窗 (负面反馈) -->
    <div
      v-if="showFeedbackDialog"
      class="feedback-overlay"
      @click.self="closeFeedbackDialog"
    >
      <div class="feedback-modal">
        <div class="feedback-header">
          <h3>请与我们分享更多信息：</h3>
          <button class="close-btn" @click="closeFeedbackDialog">
            <svg
              width="20"
              height="20"
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
        <div class="feedback-tags">
          <button
            v-for="tag in feedbackTags"
            :key="tag"
            class="feedback-tag"
            :class="{ selected: selectedTags.includes(tag) }"
            @click="toggleTag(tag)"
          >
            {{ tag }}
          </button>
          <button class="feedback-tag more" @click="openMoreFeedback">
            更多...
          </button>
        </div>
        <div class="feedback-actions" v-if="selectedTags.length > 0">
          <button class="btn-submit" @click="submitBadFeedback">
            提交反馈
          </button>
        </div>
      </div>
    </div>

    <!-- 更多反馈弹窗 -->
    <div
      v-if="showMoreFeedbackDialog"
      class="feedback-overlay"
      @click.self="closeMoreFeedbackDialog"
    >
      <div class="feedback-modal large">
        <div class="feedback-header">
          <h3>提供详细反馈</h3>
          <button class="close-btn" @click="closeMoreFeedbackDialog">
            <svg
              width="20"
              height="20"
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
        <textarea
          v-model="customFeedbackText"
          class="feedback-textarea"
          placeholder="请详细描述您遇到的问题，帮助我们改进..."
        ></textarea>
        <div class="feedback-footer">
          <button class="btn-cancel" @click="closeMoreFeedbackDialog">
            取消
          </button>
          <button class="btn-submit" @click="submitCustomFeedback">提交</button>
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
import {
  ref,
  computed,
  watch,
  nextTick,
  onMounted,
  onBeforeUnmount,
} from "vue";
import { useRoute, useRouter } from "vue-router";
import { useChatStore } from "@/stores/chat";
import { storeToRefs } from "pinia";
import { marked } from "marked";
import markedKatex from "marked-katex-extension";
import hljs from "highlight.js";
import "katex/dist/katex.min.css";

import ShareDialog from "@/components/common/ShareDialog.vue";

const route = useRoute();
const router = useRouter();
const chatStore = useChatStore();
const { messages, sessionInfo, isTyping } = storeToRefs(chatStore);
const isEmptyChat = computed(
  () => (messages.value?.length || 0) === 0 && !isTyping.value
);

const messageInput = ref(null);
const chatContainer = ref(null);
const fileInput = ref(null);
const isRecording = ref(false);
const isVoiceMode = ref(false);
const recognition = ref(null); // 语音识别实例
const imagePreviewUrl = ref(null);
const imageScale = ref(1);
const imageTranslate = ref({ x: 0, y: 0 });
const isDragging = ref(false);
const isDraggingFile = ref(false);
const dragCounter = ref(0);
const dragStart = ref({ x: 0, y: 0 });
const showScrollToBottom = ref(false);
const observer = ref(null);

// 待发送文件状态
const pendingFile = ref(null);
const pendingPreviewUrl = ref(null);

// 分享弹窗状态
const showShareDialog = ref(false);
const shareDialogUrl = ref("");
const shareDialogTitle = ref("分享对话");

// 引用功能状态
const quoteText = ref("");
const tempSelectedText = ref("");
const showQuoteBtn = ref(false);
const quoteBtnPos = ref({ top: 0, left: 0 });
const feedbackState = ref(new Map());
const speakingMessageId = ref(null);
const inputContent = ref("");
const shouldScrollToBottom = ref(false); // 标志位：是否需要滚动到底部
const isLoadingSession = ref(true); // 初始就设置为 true，默认隐藏
let currentSpeech = null;

// 反馈相关状态
const showFeedbackDialog = ref(false);
const showMoreFeedbackDialog = ref(false);
const currentFeedbackMessageId = ref(null);
const selectedTags = ref([]);
const customFeedbackText = ref("");
const feedbackTags = [
  "不应该使用记忆",
  "不喜欢此人物",
  "不喜欢这种风格",
  "与事实不符",
  "未完全遵循指令",
];

// 判断是否有输入内容
const hasInputContent = computed(() => {
  return inputContent.value.trim().length > 0 || !!pendingFile.value;
});

// 按钮状态：voice-mode(语音模式) / send(发送) / stop(停止)
const buttonMode = computed(() => {
  if (isTyping.value) return "stop";
  if (hasInputContent.value) return "send";
  return "voice-mode";
});

// 随机选择问候语
const selectRandomGreeting = () => {
  const hour = new Date().getHours();
  let list = [];

  if (hour >= 5 && hour < 11) {
    list = [
      "早上好！新的一天开始了，准备好出发了吗？",
      "早安！今天有什么计划？",
      "一日之计在于晨，加油！",
      "早上好，愿你今天充满活力！",
    ];
  } else if (hour >= 11 && hour < 14) {
    list = [
      "中午好！记得按时吃饭哦。",
      "午休时间，要不要聊聊？",
      "中午好，补充点能量继续前行吧。",
    ];
  } else if (hour >= 14 && hour < 18) {
    list = [
      "下午好！喝杯茶休息一下吧。",
      "下午好，工作学习辛苦了。",
      "午后时光，有什么我可以帮你的？",
    ];
  } else if (hour >= 18 && hour < 23) {
    list = [
      "晚上好！今天过得怎么样？",
      "晚上好，卸下一天的疲惫，聊聊吧。",
      "晚上好，我在听。",
    ];
  } else {
    list = [
      "夜深了，还在忙吗？注意休息哦。",
      "这么晚了，有什么心事吗？",
      "夜深人静，正好思考。我在。",
      "还不睡吗？小乐陪你聊聊。",
    ];
  }

  return list[Math.floor(Math.random() * list.length)];
};

const currentGreeting = ref(selectRandomGreeting());

// 配置 marked 使用 KaTeX 数学公式
marked.use(
  markedKatex({
    throwOnError: false,
    output: "html",
    trust: true, // 允许更多命令
    strict: false, // 宽松模式
  })
);

// 配置 marked 使用代码高亮
const renderer = {
  code(code, lang) {
    const language = hljs.getLanguage(lang) ? lang : "plaintext";
    return `<pre><code class="hljs language-${language}">${
      hljs.highlight(code, { language }).value
    }</code></pre>`;
  },
  link(href, title, text) {
    // 兼容 marked 不同版本的参数传递方式
    let url = href;
    let tit = title;
    let txt = text;

    if (typeof href === "object" && href !== null) {
      url = href.href;
      tit = href.title;
      txt = href.text;
    }

    return `<a href="${url}" title="${
      tit || ""
    }" target="_blank" rel="noopener noreferrer">${txt}</a>`;
  },
};

marked.use({ renderer });

marked.setOptions({
  breaks: true,
  gfm: true,
  sanitize: false, // 关键：不对 HTML 进行转义
  headerIds: false,
});

const sessionId = computed(() => route.params.sessionId);

watch(
  sessionId,
  async (newId) => {
    if (newId) {
      isLoadingSession.value = true;
      await chatStore.loadSession(newId);
      // 立即设置滚动位置（在渲染前）
      await nextTick();
      await nextTick();
      // 使用 requestAnimationFrame 确保在浏览器绘制前完成
      requestAnimationFrame(() => {
        if (chatContainer.value) {
          chatContainer.value.scrollTop = chatContainer.value.scrollHeight;
        }
        // 立即显示，因为滚动已经在绘制前完成
        requestAnimationFrame(() => {
          isLoadingSession.value = false;
        });
      });
    } else {
      chatStore.clearCurrentSession();
      isLoadingSession.value = false;
    }
  },
  { immediate: true }
);

watch(
  messages,
  () => {
    // 如果正在加载会话，不触发自动滚动（由 loadSession 负责初始定位）
    if (isLoadingSession.value) return;

    nextTick(() => {
      // 只在用户发送消息后或 AI 正在打字时才滚动
      if (shouldScrollToBottom.value || isTyping.value) {
        setTimeout(() => {
          scrollToBottom();
          // AI 打字过程中持续滚动到底部
          if (isTyping.value) {
            shouldScrollToBottom.value = true;
          } else {
            shouldScrollToBottom.value = false;
          }
        }, 50); // 减少延迟，更快响应
      }
    });
  },
  { deep: true }
);

const renderMarkdown = (content) => {
  if (!content) return "";
  // 预处理 LaTeX 分隔符，兼容 \[ \] 和 \( \)
  // 确保 block 公式 $$ 独占一行
  let preprocessed = content
    .replace(/\\\[([\s\S]*?)\\\]/g, (_, match) => `\n$$\n${match}\n$$\n`)
    .replace(/\\\(([\s\S]*?)\\\)/g, (_, match) => `$${match}$`);

  // 尝试修复常见的 LaTeX 格式问题
  // 1. 修复 \begin{equation} 没有包裹在 $$ 中的情况
  preprocessed = preprocessed.replace(
    /(?<!\$)\n\\begin\{([a-z]+)\}([\s\S]*?)\\end\{\1\}(?!\$)/g,
    "\n$$\n\\begin{$1}$2\\end{$1}\n$$\n"
  );

  // 2. 修复缺失开头 $ 的常见物理/数学公式 (针对 \mu_0 I$ 等情况)
  // 匹配模式：非$字符 + (\命令 + 可选下标 + 可选空格 + 可选变量) + $
  preprocessed = preprocessed.replace(
    /(^|[^\$])(\\[a-zA-Z]+(?:_[a-zA-Z0-9]+)?(?:\s+[a-zA-Z](?:_[a-zA-Z0-9]+)?)?)\$/g,
    "$1$$$2$$"
  );

  // 3. 修复缺失结尾 $ 的情况 (针对 $\varepsilon_0 后直接跟中文的情况)
  preprocessed = preprocessed.replace(
    /\$(\\[a-zA-Z]+(?:_[a-zA-Z0-9]+)?)(?=\s*[\u4e00-\u9fa5]|，|。|；)/g,
    "$$$1$$"
  );

  // 4. 自动包裹独立的 LaTeX 公式块 (针对 \oiint, \begin{equation} 等未包裹的情况)
  // 匹配行首的常见数学命令
  preprocessed = preprocessed.replace(
    /(^|\n)(\s*\\(oiint|iint|int|frac|sum|prod|lim|begin|mathbf|mathcal|partial)[\s\S]+?)(\n|$)/g,
    (match, p1, p2, p3, p4) => {
      // 如果已经包含 $ 或 $$，则不处理
      if (p2.includes("$")) return match;
      return `${p1}$$\n${p2.trim()}\n$$${p4}`;
    }
  );

  return marked.parse(preprocessed);
};

const copiedMessageId = ref(null);
const editingMessageId = ref(null);
const editingContent = ref("");
const isSavingEdit = ref(false); // 防止重复提交

const copyMessage = async (message) => {
  try {
    const text = message?.content || "";
    if (!text) return;
    await navigator.clipboard.writeText(text);

    // 显示复制成功状态
    copiedMessageId.value = message.id;
    setTimeout(() => {
      if (copiedMessageId.value === message.id) {
        copiedMessageId.value = null;
      }
    }, 2000);
  } catch (_) {}
};

const editMessage = (message) => {
  // 编辑用户消息：将消息内容填充到输入框
  if (message?.role !== "user") return;
  editingMessageId.value = message.id;
  editingContent.value = message.content;

  // 自动调整高度
  nextTick(() => {
    const textarea = document.getElementById(`edit-textarea-${message.id}`);
    if (textarea) {
      textarea.style.height = "auto";
      textarea.style.height = textarea.scrollHeight + "px";
      textarea.focus();
    }
  });
};

const cancelEdit = () => {
  editingMessageId.value = null;
  editingContent.value = "";
};

const saveEdit = async (message) => {
  if (isSavingEdit.value) return;

  const newContent = editingContent.value.trim();
  if (!newContent || newContent === message.content) {
    cancelEdit();
    return;
  }

  isSavingEdit.value = true;
  try {
    // 找到当前消息的索引
    const index = messages.value.findIndex((m) => m.id === message.id);
    if (index !== -1) {
      // 如果是已保存的消息（非临时ID），调用后端删除该消息及其后续消息
      if (message.id && !String(message.id).startsWith("temp-")) {
        await chatStore.deleteMessageApi(message.id);
      }

      // 1. 更新当前消息内容
      messages.value[index].content = newContent;
      // 标记为临时ID，等待发送成功后更新为新ID
      messages.value[index].id = `temp-edit-${Date.now()}`;

      // 2. 删除当前消息之后的所有消息（通常是 AI 的回复）
      // 注意：splice 会修改原数组
      if (index < messages.value.length - 1) {
        messages.value.splice(index + 1);
      }

      // 3. 退出编辑模式
      cancelEdit();

      // 4. 重新发送请求
      // 注意：chatStore.sendMessage 不会重复添加用户消息，只会触发 AI 回复
      await chatStore.sendMessage(newContent, null, router);
    }
  } catch (e) {
    console.error("Save edit failed:", e);
  } finally {
    isSavingEdit.value = false;
  }
};

const autoResizeTextarea = (e) => {
  const target = e.target;
  target.style.height = "auto";
  target.style.height = target.scrollHeight + "px";
};

const isSpeaking = (messageId) => {
  return speakingMessageId.value === messageId;
};

const toggleSpeak = (message) => {
  if (!message?.content) return;

  // 如果正在朗读当前消息，则停止
  if (isSpeaking(message.id)) {
    stopSpeech();
    return;
  }

  // 停止之前的朗读
  stopSpeech();

  // 开始新的朗读
  try {
    const utterance = new SpeechSynthesisUtterance(message.content);
    utterance.lang = "zh-CN";
    utterance.rate = 1.0;
    utterance.pitch = 1.0;
    utterance.volume = 1.0;

    utterance.onstart = () => {
      speakingMessageId.value = message.id;
    };

    utterance.onend = () => {
      speakingMessageId.value = null;
      currentSpeech = null;
    };

    utterance.onerror = () => {
      speakingMessageId.value = null;
      currentSpeech = null;
    };

    currentSpeech = utterance;
    window.speechSynthesis.speak(utterance);
  } catch (error) {
    console.error("朗读失败:", error);
    speakingMessageId.value = null;
  }
};

const stopSpeech = () => {
  if (currentSpeech) {
    window.speechSynthesis.cancel();
    speakingMessageId.value = null;
    currentSpeech = null;
  }
};

const regenerateMessage = async (message) => {
  try {
    if (message?.role !== "assistant") return;

    // 找到当前 AI 消息的索引
    const index = messages.value.findIndex((m) => m.id === message.id);
    if (index === -1) return;

    let lastUserMessage = null;
    // 向前查找最近的用户消息
    for (let i = index - 1; i >= 0; i--) {
      if (messages.value[i].role === "user") {
        lastUserMessage = messages.value[i];
        break;
      }
    }

    if (!lastUserMessage) return;

    // 保存必要信息
    const userMsgId = lastUserMessage.id;
    const content = lastUserMessage.content;

    // 1. 立即从前端移除 (防止重复点击)
    const userMsgIndex = messages.value.findIndex((m) => m.id === userMsgId);

    if (userMsgIndex !== -1) {
      // 删除从用户消息开始的所有后续消息
      messages.value.splice(userMsgIndex);
    } else {
      // 如果找不到用户消息，至少删除当前的 AI 消息
      chatStore.deleteMessage(message.id);
    }

    // 2. 立即插入新消息
    messages.value.push({
      id: `temp-regen-${Date.now()}`,
      role: "user",
      content: content,
      timestamp: new Date().toISOString(),
    });

    // 3. 后端操作 (异步执行)
    if (userMsgId && !String(userMsgId).startsWith("temp-")) {
      await chatStore.deleteMessageApi(userMsgId);
    }

    // 4. 重新发送
    await chatStore.sendMessage(content, null, router);
  } catch (e) {
    console.error("Regenerate failed:", e);
  }
};

const shareMessage = async (message) => {
  if (!message?.content) return;

  // 使用当前会话的分享链接
  const sessionId = route.params.sessionId;
  if (sessionId) {
    shareDialogTitle.value = sessionInfo.value?.title || "分享对话";
    shareDialogUrl.value = `${window.location.origin}/share/${sessionId}`;
    showShareDialog.value = true;
  } else {
    // 如果没有会话ID（例如新对话未保存），回退到复制文本
    try {
      await navigator.clipboard.writeText(message.content);
      alert("内容已复制到剪贴板");
    } catch (e) {
      console.error("Copy failed:", e);
    }
  }
};

const formatImagePath = (path) => {
  if (!path) return "";
  // 如果是 base64 或 blob 或 http 开头，直接返回
  if (
    path.startsWith("data:") ||
    path.startsWith("blob:") ||
    path.startsWith("http")
  ) {
    return path;
  }
  // 如果路径不是以 / 开头，添加 / 前缀
  if (!path.startsWith("/")) {
    return "/" + path;
  }
  return path;
};

const scrollToTop = () => {
  if (!chatContainer.value) return;
  chatContainer.value.scrollTo({
    top: 0,
    behavior: "smooth",
  });
};

const scrollToBottom = () => {
  if (!chatContainer.value) return;
  const container = chatContainer.value;
  container.scrollTo({
    top: container.scrollHeight,
    behavior: "smooth",
  });
};

const onScroll = () => {
  const el = chatContainer.value;
  if (!el) return;
  // 检查是否接近底部
  const nearBottom = el.scrollHeight - el.scrollTop - el.clientHeight < 140;
  showScrollToBottom.value = !nearBottom;

  // 滚动时隐藏引用按钮，避免位置错乱
  if (showQuoteBtn.value) {
    showQuoteBtn.value = false;
  }
};

const scrollToBottomSmooth = () => {
  scrollToBottom();
};

const openImage = (src) => {
  if (!src) return;
  imagePreviewUrl.value = src;
  imageScale.value = 1;
  imageTranslate.value = { x: 0, y: 0 };
  try {
    document.body.style.overflow = "hidden";
  } catch (_) {}
};

const closeImagePreview = () => {
  imagePreviewUrl.value = null;
  try {
    document.body.style.overflow = "";
  } catch (_) {}
};

const handleZoom = (e) => {
  const delta = e.deltaY > 0 ? -0.1 : 0.1;
  const newScale = Math.max(0.1, Math.min(5, imageScale.value + delta));
  imageScale.value = parseFloat(newScale.toFixed(2));
};

const zoomIn = () => {
  const newScale = Math.min(5, imageScale.value + 0.2);
  imageScale.value = parseFloat(newScale.toFixed(2));
};

const zoomOut = () => {
  const newScale = Math.max(0.1, imageScale.value - 0.2);
  imageScale.value = parseFloat(newScale.toFixed(2));
};

const startDrag = (e) => {
  e.preventDefault();
  isDragging.value = true;
  dragStart.value = {
    x: e.clientX - imageTranslate.value.x,
    y: e.clientY - imageTranslate.value.y,
  };
};

const onDrag = (e) => {
  if (!isDragging.value) return;
  e.preventDefault();
  imageTranslate.value = {
    x: e.clientX - dragStart.value.x,
    y: e.clientY - dragStart.value.y,
  };
};

const stopDrag = () => {
  isDragging.value = false;
};

// 触摸手势支持
const touchStartDistance = ref(0);
const touchStartScale = ref(1);
const lastTouchPos = ref({ x: 0, y: 0 });

const getDistance = (t1, t2) => {
  const dx = t1.clientX - t2.clientX;
  const dy = t1.clientY - t2.clientY;
  return Math.sqrt(dx * dx + dy * dy);
};

const handleTouchStart = (e) => {
  if (e.touches.length === 1) {
    // 单指拖拽
    isDragging.value = true;
    lastTouchPos.value = { x: e.touches[0].clientX, y: e.touches[0].clientY };
  } else if (e.touches.length === 2) {
    // 双指缩放
    isDragging.value = false;
    const dist = getDistance(e.touches[0], e.touches[1]);
    touchStartDistance.value = dist;
    touchStartScale.value = imageScale.value;
  }
};

const handleTouchMove = (e) => {
  e.preventDefault(); // 防止滚动

  if (e.touches.length === 1 && isDragging.value) {
    // 处理拖拽
    const dx = e.touches[0].clientX - lastTouchPos.value.x;
    const dy = e.touches[0].clientY - lastTouchPos.value.y;
    imageTranslate.value = {
      x: imageTranslate.value.x + dx,
      y: imageTranslate.value.y + dy,
    };
    lastTouchPos.value = { x: e.touches[0].clientX, y: e.touches[0].clientY };
  } else if (e.touches.length === 2) {
    // 处理缩放
    const dist = getDistance(e.touches[0], e.touches[1]);
    if (touchStartDistance.value > 0) {
      const scale = dist / touchStartDistance.value;
      const newScale = touchStartScale.value * scale;
      imageScale.value = Math.max(
        0.1,
        Math.min(5, parseFloat(newScale.toFixed(2)))
      );
    }
  }
};

const handleTouchEnd = (e) => {
  if (e.touches.length === 0) {
    isDragging.value = false;
  }
};

// 委托点击 Markdown 图片放大预览
const onChatClick = (e) => {
  const target = e.target;
  if (!target) return;
  if (
    target.tagName === "IMG" &&
    target.closest &&
    target.closest(".md-content")
  ) {
    const src = target.currentSrc || target.src;
    openImage(src);
  }
};

// 引用功能
const applyQuote = () => {
  if (!tempSelectedText.value) return;

  // 每次引用只保留最后一次的内容，覆盖之前的引用
  quoteText.value = tempSelectedText.value;

  showQuoteBtn.value = false;
  tempSelectedText.value = ""; // 清除临时选中

  // 清除选区，避免视觉干扰
  const sel = window.getSelection();
  if (sel) sel.removeAllRanges();
};

const clearQuote = () => {
  quoteText.value = "";
};

// 监听文本选择
const handleSelection = () => {
  const selection = window.getSelection();

  // 基础检查：是否有选区，是否折叠（光标状态）
  if (!selection || selection.rangeCount === 0 || selection.isCollapsed) {
    showQuoteBtn.value = false;
    return;
  }

  const text = selection.toString().trim();

  // 检查是否有文本内容，且长度至少为3
  if (!text || text.length < 3) {
    showQuoteBtn.value = false;
    return;
  }

  // 检查选区是否在聊天容器内
  // 只要起点或终点在容器内即可
  const isInside =
    chatContainer.value &&
    (chatContainer.value.contains(selection.anchorNode) ||
      chatContainer.value.contains(selection.focusNode));

  if (isInside) {
    const range = selection.getRangeAt(0);
    const rect = range.getBoundingClientRect();

    tempSelectedText.value = text;

    // 计算位置，优先显示在上方，如果空间不足则显示在下方
    const viewportHeight = window.innerHeight;
    const topSpace = rect.top;

    let top;
    if (topSpace > 60) {
      top = rect.top - 45; // 上方
    } else {
      top = rect.bottom + 10; // 下方
    }

    // 水平居中，但防止溢出屏幕
    let left = rect.left + rect.width / 2 - 40;
    if (left < 10) left = 10;
    if (left + 80 > window.innerWidth) left = window.innerWidth - 90;

    quoteBtnPos.value = { top, left };
    showQuoteBtn.value = true;
  } else {
    showQuoteBtn.value = false;
  }
};

// 在 onMounted 中添加 selectionchange 监听
// 注意：selectionchange 是 document 级别的事件

// 反馈相关逻辑
const toggleTag = (tag) => {
  if (selectedTags.value.includes(tag)) {
    selectedTags.value = selectedTags.value.filter((t) => t !== tag);
  } else {
    selectedTags.value.push(tag);
  }
};

const openMoreFeedback = () => {
  showMoreFeedbackDialog.value = true;
};

const closeFeedbackDialog = () => {
  showFeedbackDialog.value = false;
  selectedTags.value = [];
  currentFeedbackMessageId.value = null;
};

const closeMoreFeedbackDialog = () => {
  showMoreFeedbackDialog.value = false;
  customFeedbackText.value = "";
};

const submitBadFeedback = async () => {
  if (!currentFeedbackMessageId.value) return;

  try {
    await chatStore.submitFeedback({
      message_id: currentFeedbackMessageId.value,
      rating: "down",
      tags: selectedTags.value,
      comment: customFeedbackText.value,
    });

    // 更新本地状态
    feedbackState.value.set(currentFeedbackMessageId.value, "down");

    closeFeedbackDialog();
    closeMoreFeedbackDialog();
  } catch (e) {
    console.error("Feedback failed:", e);
  }
};

const submitCustomFeedback = async () => {
  await submitBadFeedback();
};

// 为代码块添加复制按钮等增强，避免重复添加
const enhanceRenderedContent = () => {
  if (!chatContainer.value) return;
  const blocks = chatContainer.value.querySelectorAll(
    ".md-content pre:not([data-has-copy])"
  );

  blocks.forEach((pre) => {
    pre.setAttribute("data-has-copy", "1");

    // 提取语言标签
    const codeEl = pre.querySelector("code");
    const cls = codeEl?.className || "";
    const m = cls.match(/language-([a-z0-9+#-]+)/i);
    const lang = m ? m[1].toLowerCase() : "plaintext";

    // 创建头部容器
    const header = document.createElement("div");
    header.className = "code-header";

    // 语言标签
    const label = document.createElement("span");
    label.className = "code-lang";
    label.textContent = lang;
    header.appendChild(label);

    // 复制按钮
    const btn = document.createElement("button");
    btn.className = "copy-btn";
    btn.type = "button";
    btn.innerHTML = `
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
        <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
      </svg>
      <span class="copy-text">复制代码</span>
    `;
    btn.addEventListener("click", async (e) => {
      e.stopPropagation();
      try {
        const code = pre.querySelector("code");
        const text = code ? code.innerText : pre.innerText;
        await navigator.clipboard.writeText(text);
        const textSpan = btn.querySelector(".copy-text");
        if (textSpan) {
          textSpan.textContent = "已复制";
          btn.classList.add("copied");
          setTimeout(() => {
            textSpan.textContent = "复制代码";
            btn.classList.remove("copied");
          }, 1500);
        }
      } catch (_) {}
    });
    header.appendChild(btn);

    // 将header插入pre顶部
    pre.insertBefore(header, pre.firstChild);
  });
};

const handleInput = () => {
  // 更新输入内容状态
  inputContent.value = messageInput.value?.innerText || "";

  // 处理输入，清理空内容以显示占位符
  if (messageInput.value && messageInput.value.innerText.trim() === "") {
    messageInput.value.innerHTML = "";
  }
};

const handleEnter = (e) => {
  if (!e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
};

const sendMessage = async () => {
  let content = messageInput.value?.innerText?.trim();

  // 如果有引用内容，拼接到消息头部
  if (quoteText.value) {
    // 确保每一行都被引用
    const quote =
      quoteText.value
        .split("\n")
        .map((line) => `> ${line}`)
        .join("\n") + "\n\n";
    content = quote + (content || "");
  }

  // 如果没有内容且没有待发送文件，且不在打字中，则返回
  if ((!content && !pendingFile.value) || isTyping.value) return;

  // 立即清空输入框和引用
  messageInput.value.innerText = "";
  messageInput.value.innerHTML = "";
  inputContent.value = "";
  quoteText.value = ""; // 清空引用

  // 处理待发送文件
  let imagePath = null;
  const currentFile = pendingFile.value;
  const currentPreview = pendingPreviewUrl.value;

  // 清空待发送状态
  pendingFile.value = null;
  pendingPreviewUrl.value = null;

  // 立即添加用户消息到界面末尾（保持对话顺序）
  messages.value.push({
    id: `temp-${Date.now()}`,
    role: "user",
    content: content,
    image_path: currentPreview, // 临时显示本地预览图
    timestamp: new Date().toISOString(),
  });

  // 设置标志位：需要滚动到底部
  shouldScrollToBottom.value = true;

  try {
    // 如果有文件，先上传
    if (currentFile) {
      // 显示上传状态（可选，目前直接用打字状态覆盖）
      imagePath = await chatStore.uploadImage(currentFile);
      if (!imagePath) {
        // 上传失败处理
        messages.value.push({
          id: `error-${Date.now()}`,
          role: "assistant",
          content: "❌ 图片上传失败，请重试。",
          status: "done",
        });
        return;
      }
    }

    // 发送到后端
    await chatStore.sendMessage(content, imagePath, router);
  } catch (e) {
    console.error("Send message failed:", e);
    messages.value.push({
      id: `error-${Date.now()}`,
      role: "assistant",
      content: "❌ 发送失败，请重试。",
      status: "done",
    });
  }

  // 检测是否需要刷新提醒或任务列表
  // 检查用户输入和AI响应
  const lowerContent = (content || "").toLowerCase();
  const needsReminderRefresh = /提醒|闹钟|reminder/.test(lowerContent);
  const needsTaskRefresh = /任务|待办|todo|task/.test(lowerContent);

  // 增加延迟到3秒，确保AI响应和工具执行都已完成
  setTimeout(() => {
    if (needsReminderRefresh) {
      console.log("🔄 触发提醒列表刷新");
      window.dispatchEvent(new CustomEvent("refresh-reminders"));
    }
    if (needsTaskRefresh) {
      console.log("🔄 触发任务列表刷新");
      window.dispatchEvent(new CustomEvent("refresh-tasks"));
    }
  }, 3000);
};

const stopGeneration = () => {
  console.log("停止 AI 生成");
  chatStore.stopGeneration();
};

const handleMainButton = () => {
  if (buttonMode.value === "send") {
    sendMessage();
  } else if (buttonMode.value === "stop") {
    stopGeneration();
  } else {
    toggleVoiceMode();
  }
};

const handleUpload = () => {
  fileInput.value?.click();
};

const handleFileChange = async (e) => {
  const file = e.target.files?.[0];
  if (!file) return;

  // 检查文件类型
  if (file.type.startsWith("image/")) {
    // 图片：添加到待发送列表，显示预览
    pendingFile.value = file;

    // 创建本地预览URL
    const reader = new FileReader();
    reader.onload = (e) => {
      pendingPreviewUrl.value = e.target.result;
    };
    reader.readAsDataURL(file);

    // 聚焦输入框
    nextTick(() => {
      messageInput.value?.focus();
    });
  } else {
    // 处理文档上传 (保持原有逻辑，文档直接上传处理)
    try {
      // 显示加载状态
      chatStore.isTyping = true;

      // 添加用户消息占位
      messages.value.push({
        id: `temp-doc-${Date.now()}`,
        role: "user",
        content: `📄 上传文档：${file.name}`,
        timestamp: new Date().toISOString(),
      });

      // 滚动到底部
      shouldScrollToBottom.value = true;

      const result = await chatStore.uploadDocument(file);

      if (result.success) {
        // 构建总结消息
        let content = `### 📄 文档总结：${file.name}\n\n${result.summary}\n\n#### 💡 关键要点\n`;
        if (Array.isArray(result.key_points)) {
          result.key_points.forEach((p) => (content += `- ${p}\n`));
        }

        content += `\n\n*(处理耗时: ${result.processing_time.toFixed(1)}秒)*`;

        // 添加 AI 回复消息
        // 注意：这里只是前端显示，如果需要持久化到对话历史，
        // 建议后端 upload_document 接口同时也写入 messages 表，
        // 或者前端调用 sendMessage 发送总结内容（但这会再次触发 AI 生成）
        // 目前作为独立功能展示
        messages.value.push({
          id: `doc-summary-${result.document_id}`,
          role: "assistant",
          content: content,
          timestamp: new Date().toISOString(),
          status: "done",
        });

        // 再次滚动
        shouldScrollToBottom.value = true;

        // 关键修复：如果这是新会话，更新路由，确保刷新后不丢失
        if (
          result.session_id &&
          (!route.params.sessionId ||
            route.params.sessionId !== result.session_id)
        ) {
          // 更新 store 状态
          chatStore.currentSessionId = result.session_id;
          // 更新 URL，确保刷新后能加载回话
          // 使用 replace 避免在历史记录中留下空白的新对话页面
          await router.replace(`/chat/${result.session_id}`);
        }
      } else {
        messages.value.push({
          id: `error-${Date.now()}`,
          role: "assistant",
          content: `❌ 文档处理失败: ${result.error || "未知错误"}`,
          status: "done",
        });
      }
    } catch (error) {
      console.error("Upload error:", error);
      messages.value.push({
        id: `error-${Date.now()}`,
        role: "assistant",
        content: `❌ 上传失败: ${error.message || "网络错误"}`,
        status: "done",
      });
    } finally {
      chatStore.isTyping = false;
    }
  }
  e.target.value = "";
};

const clearPendingFile = () => {
  pendingFile.value = null;
  pendingPreviewUrl.value = null;
  if (fileInput.value) {
    fileInput.value.value = "";
  }
};

const handleDragEnter = (e) => {
  dragCounter.value++;
  isDraggingFile.value = true;
};

const handleDragLeave = (e) => {
  dragCounter.value--;
  if (dragCounter.value <= 0) {
    isDraggingFile.value = false;
    dragCounter.value = 0;
  }
};

const handleDrop = (e) => {
  isDraggingFile.value = false;
  dragCounter.value = 0;
  const files = e.dataTransfer.files;
  if (files.length > 0) {
    const file = files[0];
    // 复用 handleFileChange 的逻辑，但需要构造一个类似 event 的对象
    handleFileChange({ target: { files: [file], value: "dummy" } });
  }
};

const handleVoice = () => {
  // 语音输入功能
  console.log("语音输入");
};

const handleVoiceInput = () => {
  isRecording.value = !isRecording.value;
  if (isRecording.value) {
    console.log("开始语音输入");
    // TODO: 调用语音识别 API
  } else {
    console.log("停止语音输入");
  }
};

const toggleVoiceMode = () => {
  isVoiceMode.value = !isVoiceMode.value;
  console.log("语音模式:", isVoiceMode.value ? "开启" : "关闭");
  // TODO: 实现语音模式逻辑
};

const canSend = computed(() => {
  return messageInput.value?.innerText?.trim().length > 0;
});

onMounted(() => {
  // 移除自动滚动，让浏览器保持用户的滚动位置
  currentGreeting.value = selectRandomGreeting();

  if (chatContainer.value) {
    chatContainer.value.addEventListener("click", onChatClick);
    chatContainer.value.addEventListener("scroll", onScroll, { passive: true });

    // 使用 MutationObserver 监听 DOM 变化，自动添加代码块头部
    observer.value = new MutationObserver(() => {
      enhanceRenderedContent();
    });
    observer.value.observe(chatContainer.value, {
      childList: true,
      subtree: true,
    });
  }

  // 初始执行一次
  nextTick(enhanceRenderedContent);

  document.addEventListener("selectionchange", handleSelection);
});

onBeforeUnmount(() => {
  // 停止朗读
  stopSpeech();

  if (observer.value) {
    observer.value.disconnect();
  }

  if (chatContainer.value) {
    chatContainer.value.removeEventListener("click", onChatClick);
    chatContainer.value.removeEventListener("scroll", onScroll);
  }
  document.removeEventListener("selectionchange", handleSelection);
});

// 解析引用内容
const extractReferences = (content) => {
  if (!content) return { main: "", refs: [] };

  // 匹配 "参考来源：" 或 "References:" 及其后的内容
  // 使用更严格的正则，确保是在行首或双换行后
  const refRegex =
    /(?:^|\n\n)(?:参考来源|References|Sources)[:：]\s*([\s\S]*)$/i;
  const match = content.match(refRegex);

  if (!match) return { main: content, refs: [] };

  const refBlock = match[1];
  const main = content.substring(0, match.index).trim();

  // 提取链接：1. [Title](URL)
  const linkRegex = /(?:^|\n)\s*\d+\.\s*\[(.*?)\]\((.*?)\)/g;
  const refs = [];
  let linkMatch;

  while ((linkMatch = linkRegex.exec(refBlock)) !== null) {
    refs.push({
      title: linkMatch[1],
      href: linkMatch[2],
      body: "", // 文本解析没有摘要
    });
  }

  // 如果没有提取到有效链接，说明可能不是标准的引用块，不截断
  if (refs.length === 0) return { main: content, refs: [] };

  return { main, refs };
};

const getDisplayContent = (message) => {
  // 如果有结构化的 search_results，我们仍然尝试移除文本中的引用部分，避免重复
  // 如果没有 search_results，我们也移除引用部分，因为会渲染成卡片
  const { main } = extractReferences(message.content);
  return main;
};

const getRelatedReadings = (message) => {
  // 优先使用后端返回的结构化数据（包含摘要）
  if (message.search_results && message.search_results.length > 0) {
    return message.search_results;
  }
  // 否则尝试从文本中解析
  const { refs } = extractReferences(message.content);
  return refs;
};

const hasRelatedReadings = (message) => {
  if (message.search_results && message.search_results.length > 0) return true;
  const { refs } = extractReferences(message.content);
  return refs.length > 0;
};

const getDomain = (url) => {
  try {
    const domain = new URL(url).hostname;
    return domain.replace("www.", "");
  } catch (e) {
    return "web";
  }
};

const handleFaviconError = (e) => {
  e.target.style.opacity = "0";
};

const feedbackMessage = async (message, type) => {
  try {
    const id = message?.id;
    if (!id) return;

    // 如果是点赞 (up)
    if (type === "up") {
      // 如果已经是 up，则取消
      if (feedbackState.value.get(id) === "up") {
        feedbackState.value.delete(id);
        // TODO: 发送取消反馈请求
      } else {
        // 如果是 down，先清除 down
        feedbackState.value.set(id, "up");
        await chatStore.submitFeedback({
          message_id: id,
          rating: "up",
        });
      }
    }
    // 如果是点踩 (down)
    else if (type === "down") {
      // 如果已经是 down，则取消
      if (feedbackState.value.get(id) === "down") {
        feedbackState.value.delete(id);
        // TODO: 发送取消反馈请求
      } else {
        // 打开反馈弹窗
        currentFeedbackMessageId.value = id;
        showFeedbackDialog.value = true;
        // 暂时不立即设置状态，等提交后再设置
        // 或者先设置为 down，如果取消弹窗再撤销？
        // 这里选择：先不设置，提交后设置
      }
    }
  } catch (e) {
    console.error("Feedback error:", e);
  }
};
</script>

<style scoped>
.chat-view {
  display: flex;
  flex-direction: column;
  height: 100%;
  position: relative;
  background: var(--bg-primary);
}
/* 欢迎消息 */
.welcome-message {
  position: absolute;
  top: 35%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  z-index: 10;
  animation: fadeInUp 0.5s ease-out;
}
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translate(-50%, -45%);
  }
  to {
    opacity: 1;
    transform: translate(-50%, -50%);
  }
}
.welcome-icon {
  font-size: 48px;
  margin-bottom: 16px;
}
.welcome-title {
  font-size: 24px;
  font-weight: 500;
  color: var(--text-primary);
  letter-spacing: -0.5px;
}
.welcome-subtitle {
  font-size: 16px;
  color: var(--text-secondary);
}
.chat-view.empty {
  justify-content: center;
  align-items: center;
}
.chat-view.empty .chat-container {
  display: none;
}
.chat-view.empty .input-container {
  position: static;
  background: transparent;
  border-top: none;
  padding: 0;
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
}
.chat-view.empty .input-wrapper {
  max-width: 800px;
  width: 90%;
  box-shadow: none;
  background: var(--bg-secondary);
  border: 1px solid var(--border-medium);
}
.chat-container {
  flex: 1;
  overflow-y: auto;
  padding: 0;
  display: flex;
  justify-content: center;
  background: var(--bg-primary);
  margin-bottom: 100px;
  scroll-behavior: auto; /* 确保初始滚动是瞬间的 */
}
.chat-inner {
  width: 100%;
  max-width: 800px;
  padding: 16px 20px;
  position: relative;
}
.message {
  margin-bottom: 16px;
  display: flex;
  flex-direction: column;
  opacity: 0;
  animation: messageSlideIn 0.3s ease-out forwards;
}
@keyframes messageSlideIn {
  from {
    opacity: 0;
    transform: translateY(6px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
.message.new-group {
  margin-top: 24px;
}
.message.user {
  align-items: flex-end;
}
.message.assistant {
  align-items: flex-start;
}
.user-bubble {
  background: #2f2f2f;
  color: #ececec;
  border-radius: 16px;
  padding: 11px 15px;
  display: inline-block;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.08);
  font-size: 16px;
  max-width: 68%;
  word-wrap: break-word;
  word-break: break-word;
  overflow-wrap: break-word;
  hyphens: auto;
}
[data-theme="light"] .user-bubble {
  background: #f3f4f6;
  color: #1f2937;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}
.user-bubble :deep(p) {
  margin: 0 0 0.5em 0;
  line-height: 1.6;
  color: #ececec;
}
[data-theme="light"] .user-bubble :deep(p) {
  color: #1f2937;
}
.user-bubble :deep(p:last-child) {
  margin-bottom: 0;
}
.message.assistant .md-content {
  font-size: 16px;
  max-width: 100%;
  word-wrap: break-word;
  word-break: break-word;
  overflow-wrap: break-word;
}
.message.assistant .md-content :deep(p) {
  margin: 0 0 0.6em 0;
  line-height: 1.6;
  color: var(--text-primary);
}
.message.assistant .md-content :deep(p:last-child) {
  margin-bottom: 0;
}
.message-content :deep(p:last-child) {
  margin-bottom: 0;
}
.message-content :deep(ul),
.message-content :deep(ol),
.md-content :deep(ul),
.md-content :deep(ol) {
  margin: 0.8em 0;
  padding-left: 2em;
  list-style-position: outside;
}
.message-content :deep(li),
.md-content :deep(li) {
  margin: 0.3em 0;
  line-height: 1.6;
  padding-left: 0.3em;
}
.md-content :deep(ul) {
  list-style-type: disc;
}
.md-content :deep(ol) {
  list-style-type: decimal;
}
.md-content :deep(ul ul) {
  list-style-type: circle;
}
.md-content :deep(ul ul ul) {
  list-style-type: square;
}
.message-content :deep(code),
.md-content :deep(code) {
  background: rgba(175, 184, 193, 0.2);
  padding: 0.2em 0.5em;
  border-radius: 4px;
  font-size: 0.9em;
  font-family: ui-monospace, "SF Mono", Monaco, "Cascadia Code", monospace;
  color: var(--text-primary);
  border: 1px solid rgba(175, 184, 193, 0.25);
  font-weight: 500;
}
.message-content :deep(pre code),
.md-content :deep(pre code) {
  border: none;
  font-weight: 400;
}
.message-content :deep(pre),
.md-content :deep(pre) {
  background: #0d1117;
  padding: 0;
  border-radius: 10px;
  overflow: hidden;
  margin: 1em 0;
  position: relative;
  border: 1px solid rgba(255, 255, 255, 0.12);
  max-width: 100%;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
}
.message-content :deep(pre code),
.md-content :deep(pre code) {
  background: none;
  padding: 16px 20px;
  color: #e6edf3;
  font-family: ui-monospace, "SF Mono", Monaco, "Cascadia Code", "Roboto Mono",
    Menlo, Consolas, monospace;
  font-size: 14px;
  line-height: 1.75;
  display: block;
  white-space: pre;
  overflow-x: auto;
  font-weight: 400;
  letter-spacing: 0.02em;
  tab-size: 2;
}
[data-theme="light"] .message-content :deep(pre) {
  background: #f6f8fa;
  border: 1px solid #e1e4e8;
}
[data-theme="light"] .message-content :deep(pre code) {
  color: #24292e;
}
.message-image {
  max-width: 320px;
  max-height: 180px;
  margin: 12px 0 0 0;
  border-radius: 6px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
  cursor: pointer;
}
.md-content :deep(h1),
.md-content :deep(h2),
.md-content :deep(h3) {
  margin: 0.7em 0 0.4em;
  line-height: 1.2;
}
.md-content :deep(h4),
.md-content :deep(h5),
.md-content :deep(h6) {
  margin: 0.6em 0 0.3em;
}
.md-content :deep(a) {
  color: var(--brand-primary);
  text-decoration: none;
}
.md-content :deep(a:hover) {
  text-decoration: underline;
}
.md-content :deep(blockquote) {
  margin: 0.9em 0;
  padding: 8px 12px;
  border-left: 3px solid var(--border-medium);
  background: var(--bg-secondary);
  border-radius: 6px;
}
.md-content :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 12px 0;
}
.md-content :deep(th),
.md-content :deep(td) {
  border: 1px solid var(--border-light);
  padding: 8px 10px;
}
.md-content :deep(img) {
  max-width: 100%;
  border-radius: 10px;
  border: 1px solid var(--border-light);
}

/* 代码块头部 */
.md-content :deep(.code-header),
.message-content :deep(.code-header) {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(
    180deg,
    rgba(0, 0, 0, 0.4) 0%,
    rgba(0, 0, 0, 0.3) 100%
  );
  border-bottom: 1px solid rgba(255, 255, 255, 0.12);
  padding: 10px 20px;
  backdrop-filter: blur(10px);
  position: relative;
  z-index: 1;
}

.md-content :deep(.code-lang),
.message-content :deep(.code-lang) {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.85);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  padding: 3px 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
}

.md-content :deep(.copy-btn),
.message-content :deep(.copy-btn) {
  border: 1px solid rgba(255, 255, 255, 0.15);
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.75);
  font-size: 12px;
  padding: 6px 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  font-weight: 500;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  display: flex;
  align-items: center;
  gap: 6px;
  user-select: none;
}

.md-content :deep(.copy-btn svg),
.message-content :deep(.copy-btn svg) {
  width: 14px;
  height: 14px;
  opacity: 0.85;
  transition: transform 0.2s ease;
}

.md-content :deep(.copy-btn:hover),
.message-content :deep(.copy-btn:hover) {
  background: rgba(255, 255, 255, 0.18);
  border-color: rgba(255, 255, 255, 0.25);
  color: rgba(255, 255, 255, 0.95);
  transform: translateY(-1px);
}

.md-content :deep(.copy-btn:hover svg),
.message-content :deep(.copy-btn:hover svg) {
  transform: scale(1.1);
}

.md-content :deep(.copy-btn.copied),
.message-content :deep(.copy-btn.copied) {
  background: rgba(46, 160, 67, 0.25);
  border-color: rgba(46, 160, 67, 0.4);
  color: #3fb950;
}

.md-content :deep(.copy-btn.copied svg),
.message-content :deep(.copy-btn.copied svg) {
  opacity: 1;
  transform: scale(1.15);
}

/* 代码滚动条优化 */
.md-content :deep(pre code)::-webkit-scrollbar {
  height: 8px;
}

.md-content :deep(pre code)::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 4px;
}

.md-content :deep(pre code)::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 4px;
}

.md-content :deep(pre code)::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.3);
}
.message-toolbar {
  display: flex;
  gap: 2px;
  margin-top: 4px;
  transition: opacity 0.2s;
}
.message.assistant .message-toolbar {
  opacity: 1;
}
.message.user .message-toolbar {
  opacity: 0;
  justify-content: flex-end;
}
.message.user:hover .message-toolbar {
  opacity: 1;
}
.toolbar-icon {
  background: none;
  border: none;
  padding: 5px;
  cursor: pointer;
  color: var(--text-tertiary);
  border-radius: 5px;
  transition: all 0.15s;
  width: 26px;
  height: 26px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.toolbar-icon svg {
  width: 15px;
  height: 15px;
}
.toolbar-icon:hover {
  background: var(--bg-hover);
  color: var(--text-secondary);
}
.toolbar-icon.active {
  background: var(--bg-active);
  color: var(--text-primary);
}
.message.user .toolbar-icon {
  color: rgba(255, 255, 255, 0.5);
}
[data-theme="light"] .message.user .toolbar-icon {
  color: var(--text-tertiary);
}
.message.user .toolbar-icon:hover {
  background: rgba(255, 255, 255, 0.15);
  color: rgba(255, 255, 255, 0.9);
}
[data-theme="light"] .message.user .toolbar-icon:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}
.message.user .toolbar-icon.active {
  background: rgba(255, 255, 255, 0.2);
  color: #fff;
}
[data-theme="light"] .message.user .toolbar-icon.active {
  background: var(--bg-active);
  color: var(--text-primary);
}
.input-container {
  padding: 12px 16px 16px;
  border-top: none;
  background: transparent;
  flex-shrink: 0;
}
.input-wrapper {
  max-width: 800px;
  margin: 0 auto;
  display: flex;
  flex-direction: column; /* 改为纵向布局以容纳预览图 */
  gap: 8px;
  align-items: stretch; /* 撑满宽度 */
  background: var(--bg-secondary);
  border: 1px solid var(--border-light);
  border-radius: 22px;
  padding: 8px 10px; /* 调整内边距 */
  transition: all 0.2s ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
  min-height: 50px;
  position: relative;
}
.input-wrapper:focus-within {
  border-color: var(--text-tertiary);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}
.input-wrapper.drag-over {
  border-color: var(--brand-primary);
  background: var(--bg-tertiary);
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
}
.input-wrapper.drag-over::after {
  content: "释放以添加文件";
  position: absolute;
  inset: 0;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(2px);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  color: var(--brand-primary);
  font-weight: 500;
  border-radius: 22px;
  z-index: 10;
  pointer-events: none;
}
[data-theme="dark"] .input-wrapper.drag-over::after {
  background: rgba(30, 30, 30, 0.8);
}
.input-controls {
  display: flex;
  align-items: center;
  gap: 4px;
  width: 100%;
}
/* 图片预览区域优化 */
.input-preview-area {
  padding: 4px 4px 0 4px;
  display: flex;
  gap: 10px;
  animation: fadeIn 0.2s ease;
}

.preview-card {
  position: relative;
  width: 60px;
  height: 60px;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid var(--border-medium);
  background: var(--bg-tertiary);
}

.preview-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.preview-close-btn {
  position: absolute;
  top: 2px;
  right: 2px;
  width: 18px;
  height: 18px;
  background: rgba(0, 0, 0, 0.6);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  border: none;
  cursor: pointer;
  opacity: 0;
  transition: opacity 0.2s;
  padding: 0;
}

.preview-card:hover .preview-close-btn {
  opacity: 1;
}

.preview-close-btn:hover {
  background: rgba(0, 0, 0, 0.8);
}

.message-editor {
  flex: 1;
  max-height: 200px;
  overflow-y: auto;
  outline: none;
  padding: 9px 4px;
  color: var(--text-primary);
  font-size: 15px;
  line-height: 1.5;
  min-height: 22px;
  border: none;
  background: transparent;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}
.message-editor:empty:before {
  content: attr(data-placeholder);
  color: var(--text-tertiary);
  font-size: 15px;
}
.icon-btn {
  width: 28px;
  height: 28px;
  border: none;
  background: transparent;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  transition: all 0.15s ease;
  color: var(--text-secondary);
  flex-shrink: 0;
}
.icon-btn svg {
  width: 18px;
  height: 18px;
}
.icon-btn:hover:not(:disabled) {
  background: var(--bg-hover);
  color: var(--text-primary);
}
.icon-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
.icon-btn.active {
  background: var(--brand-primary);
  color: var(--text-inverse);
}
.icon-btn.recording {
  background: var(--error);
  color: var(--text-inverse);
  animation: pulse 1.5s ease-in-out infinite;
}
.voice-mode-btn {
  width: 36px;
  height: 36px;
  border-radius: 50%;
}

.voice-mode-btn svg {
  width: 28px;
  height: 28px;
}

.voice-mode-btn.send-mode {
  background: #ffffff;
  color: var(--text-primary);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.25);
  border: 1px solid var(--border-medium);
}
.voice-mode-btn.send-mode:hover {
  background: #ffffff;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.28);
}

/* 停止模式样式 */
.voice-mode-btn.stop-mode {
  background: var(--error);
  color: #fff;
  box-shadow: 0 2px 8px rgba(255, 0, 0, 0.35);
}
.voice-mode-btn.stop-mode:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 14px rgba(255, 0, 0, 0.45);
}

/* 思考与打字效果 */
.thinking-wrapper {
  display: flex;
  align-items: center;
  min-height: 24px;
  padding: 2px 4px;
}
.thinking-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: var(--text-primary);
  box-shadow: 0 0 8px var(--text-primary);
  animation: thinkingPulse 1s ease-in-out infinite;
}
@keyframes thinkingPulse {
  0% {
    transform: scale(0.7);
    opacity: 0.5;
  }
  50% {
    transform: scale(1.6);
    opacity: 1;
  }
  100% {
    transform: scale(0.7);
    opacity: 0.5;
  }
}
.md-content.typing:after {
  content: "";
  display: inline-block;
  width: 6px;
  height: 16px;
  background: var(--text-primary);
  margin-left: 2px;
  animation: caretBlink 0.9s steps(2, start) infinite;
  vertical-align: bottom;
}
@keyframes caretBlink {
  0%,
  49% {
    opacity: 1;
  }
  50%,
  100% {
    opacity: 0;
  }
}

@keyframes pulse {
  0%,
  100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.8;
    transform: scale(1.05);
  }
}
.scroll-to-bottom {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  bottom: 120px;
  width: 48px;
  height: 48px;
  border-radius: 50%;
  border: 1px solid var(--border-medium);
  background: var(--bg-secondary);
  color: var(--text-primary);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 100;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  animation: fadeIn 0.3s ease;
}
.scroll-to-bottom svg {
  opacity: 1;
}
.scroll-to-bottom:hover {
  background: var(--brand-primary);
  color: white;
  transform: translateX(-50%) translateY(-2px);
  box-shadow: 0 6px 24px rgba(0, 0, 0, 0.25);
  border-color: var(--brand-primary);
}
.scroll-to-bottom:active {
  transform: translateX(-50%) translateY(0);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateX(-50%) translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateX(-50%) translateY(0);
  }
}
.image-preview-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.65);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  cursor: zoom-out;
}
.image-preview {
  max-width: 92vw;
  max-height: 92vh;
  border-radius: 12px;
  box-shadow: 0 15px 60px rgba(0, 0, 0, 0.35);
}
@media (max-width: 900px) {
  .input-wrapper {
    max-width: 98vw;
  }
}

/* 移动端适配优化 */
@media (max-width: 768px) {
  .chat-inner {
    padding: 12px 12px;
  }

  .user-bubble {
    max-width: 88%;
    font-size: 15px;
    padding: 10px 14px;
  }

  .message.assistant .md-content {
    font-size: 15px;
  }

  .input-container {
    padding: 8px 10px 10px;
  }

  .input-wrapper {
    padding: 6px 8px;
    border-radius: 20px;
  }

  .welcome-title {
    font-size: 20px;
  }

  .welcome-icon {
    font-size: 40px;
  }

  /* 移动端始终显示工具栏，避免无法操作 */
  .message-toolbar {
    opacity: 1 !important;
    margin-top: 6px;
  }

  .message.user .message-toolbar {
    justify-content: flex-end;
  }

  /* 优化代码块在移动端的显示 */
  .md-content :deep(pre) {
    border-radius: 8px;
    margin: 0.8em 0;
  }

  .md-content :deep(pre code) {
    padding: 12px 14px;
    font-size: 13px;
  }

  /* 调整图片最大宽度 */
  .message-image {
    max-width: 100%;
    max-height: 240px;
  }
}

/* 编辑模式样式 */
.edit-mode-container {
  width: 100%;
  max-width: 68%;
  background: var(--bg-secondary);
  border: 1px solid var(--brand-primary);
  border-radius: 12px;
  padding: 10px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.edit-textarea {
  width: 100%;
  min-height: 60px;
  background: transparent;
  border: none;
  color: var(--text-primary);
  font-size: 16px;
  line-height: 1.6;
  resize: none;
  outline: none;
  font-family: inherit;
}

.edit-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.btn-edit-action {
  padding: 4px 12px;
  border-radius: 6px;
  font-size: 13px;
  cursor: pointer;
  border: 1px solid transparent;
  transition: all 0.2s;
}

.btn-edit-action.cancel {
  background: var(--bg-tertiary);
  color: var(--text-secondary);
}

.btn-edit-action.cancel:hover {
  background: var(--bg-hover);
}

.btn-edit-action.save {
  background: var(--brand-primary);
  color: #fff;
}

.btn-edit-action.save:hover {
  opacity: 0.9;
}

/* 复制成功图标颜色 */
.text-success {
  color: #3fb950;
}

/* 图片预览控制栏 */
.preview-controls {
  position: absolute;
  bottom: 30px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(0, 0, 0, 0.75);
  backdrop-filter: blur(10px);
  padding: 8px 16px;
  border-radius: 24px;
  display: flex;
  align-items: center;
  gap: 12px;
  z-index: 2001;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.control-btn {
  background: transparent;
  border: none;
  color: rgba(255, 255, 255, 0.8);
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.control-btn:hover {
  color: #fff;
  background: rgba(255, 255, 255, 0.1);
}

.zoom-level {
  color: rgba(255, 255, 255, 0.9);
  font-size: 14px;
  font-variant-numeric: tabular-nums;
  min-width: 40px;
  text-align: center;
}

.divider {
  width: 1px;
  height: 16px;
  background: rgba(255, 255, 255, 0.2);
  margin: 0 4px;
}

/* 引用浮动按钮 */
.quote-float-btn {
  position: fixed;
  z-index: 2147483647 !important;
  background: var(--bg-secondary);
  border: 1px solid var(--border-medium);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
  padding: 6px 12px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  font-size: 14px;
  color: var(--text-primary);
  transition: all 0.2s;
  animation: fadeIn 0.2s ease;
  backdrop-filter: blur(4px); /* 增加毛玻璃效果 */
}

.quote-float-btn:hover {
  background: var(--bg-hover);
  transform: translateY(-2px);
}

/* 引用预览条 */
.quote-preview-bar {
  position: absolute;
  bottom: 100%;
  left: 0;
  right: 0;
  margin-bottom: 8px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-medium);
  border-radius: 12px;
  padding: 10px 14px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  z-index: 10;
  height: 44px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.quote-content {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
  overflow: hidden;
}

.quote-icon {
  color: var(--text-tertiary);
  flex-shrink: 0;
}

.quote-text {
  font-size: 13px;
  color: var(--text-secondary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1.5;
}

.close-quote-btn {
  background: transparent;
  border: none;
  color: var(--text-tertiary);
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
}

.close-quote-btn:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

/* 反馈弹窗样式 */
.feedback-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  backdrop-filter: blur(2px);
}

.feedback-modal {
  background: var(--bg-secondary);
  border: 1px solid var(--border-medium);
  border-radius: 12px;
  padding: 20px;
  width: 90%;
  max-width: 400px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.2);
  animation: modalIn 0.2s ease-out;
}

.feedback-modal.large {
  max-width: 500px;
}

@keyframes modalIn {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.feedback-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.feedback-header h3 {
  font-size: 16px;
  font-weight: 600;
  margin: 0;
  color: var(--text-primary);
}

.close-btn {
  background: transparent;
  border: none;
  color: var(--text-tertiary);
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
}

.close-btn:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.feedback-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 20px;
}

.feedback-tag {
  background: var(--bg-tertiary);
  border: 1px solid transparent;
  color: var(--text-secondary);
  padding: 6px 12px;
  border-radius: 16px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.feedback-tag:hover {
  background: var(--bg-hover);
}

.feedback-tag.selected {
  background: var(--brand-primary-bg, rgba(59, 130, 246, 0.1));
  border-color: var(--brand-primary);
  color: var(--brand-primary);
}

.feedback-tag.more {
  background: transparent;
  border: 1px dashed var(--border-medium);
}

.feedback-actions {
  display: flex;
  justify-content: flex-end;
}

.btn-submit {
  background: var(--brand-primary);
  color: #fff;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: opacity 0.2s;
}

.btn-submit:hover {
  opacity: 0.9;
}

.feedback-textarea {
  width: 100%;
  height: 120px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-medium);
  border-radius: 8px;
  padding: 12px;
  color: var(--text-primary);
  font-size: 14px;
  resize: none;
  margin-bottom: 16px;
  outline: none;
}

.feedback-textarea:focus {
  border-color: var(--brand-primary);
}

.feedback-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.btn-cancel {
  background: transparent;
  border: 1px solid var(--border-medium);
  color: var(--text-secondary);
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
}

.btn-cancel:hover {
  background: var(--bg-hover);
}

/* 相关阅读卡片样式 */
.related-reading {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--border-light);
  animation: fadeIn 0.5s ease-out;
  width: 100%;
  overflow: hidden; /* 防止溢出 */
}

.related-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 12px;
}

.related-cards {
  display: flex;
  gap: 12px;
  overflow-x: auto;
  padding-bottom: 8px;
  width: 100%;
  /* 隐藏滚动条但保持功能 */
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none; /* IE/Edge */
}

.related-cards::-webkit-scrollbar {
  display: none; /* Chrome/Safari/Opera */
}

.related-card {
  flex: 1; /* 均分宽度 */
  min-width: 0; /* 防止内容撑开 */
  background: var(--bg-secondary);
  border: 1px solid var(--border-light);
  border-radius: 12px;
  text-decoration: none;
  transition: transform 0.2s, box-shadow 0.2s;
  display: flex;
  flex-direction: column;
  overflow: hidden; /* 确保图片不溢出圆角 */
}

.related-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
  border-color: var(--border-medium);
}

.card-image-area {
  height: 110px;
  background: var(--bg-tertiary);
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid var(--border-light);
  position: relative;
  overflow: hidden;
}

.card-cover-icon {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  object-fit: contain;
  opacity: 0.9;
  transition: transform 0.3s ease;
}

.related-card:hover .card-cover-icon {
  transform: scale(1.1);
}

.card-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 12px;
  flex: 1;
}

.card-source {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--text-secondary);
}

.favicon {
  width: 14px;
  height: 14px;
  border-radius: 2px;
}

.domain-text {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-weight: 500;
}

.card-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-snippet {
  display: none; /* 隐藏摘要以节省空间 */
}

/* 拖拽遮罩样式 */
.drag-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(4px);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: none; /* 让事件穿透，但 dragover 会拦截 */
}

/* 暗色模式适配 */
:global(.dark) .drag-overlay {
  background: rgba(0, 0, 0, 0.7);
}

.drag-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  border-radius: 16px;
  background: var(--bg-secondary);
  box-shadow: var(--shadow-lg);
  border: 2px dashed var(--brand-primary);
  animation: scaleIn 0.2s ease-out;
}

.drag-icon {
  color: var(--brand-primary);
  margin-bottom: 16px;
}

.drag-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.drag-subtitle {
  font-size: 14px;
  color: var(--text-secondary);
}

@keyframes scaleIn {
  from {
    opacity: 0;
    transform: scale(0.9);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}
</style>
