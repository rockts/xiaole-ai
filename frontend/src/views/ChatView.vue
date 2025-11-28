<template>
  <div
    class="chat-view"
    ref="chatViewRoot"
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
              <div
                class="thinking-wrapper"
                style="
                  background: rgba(59, 130, 246, 0.1);
                  padding: 12px;
                  border-radius: 12px;
                  min-width: 80px;
                "
              >
                <div style="display: inline-flex; align-items: center; gap: 6px;">
                  <i style="display: inline-block; width: 8px; height: 8px; background: #3b82f6; border-radius: 50%; animation: thinkingBounce 1.4s ease-in-out 0s infinite;"></i>
                  <i style="display: inline-block; width: 8px; height: 8px; background: #3b82f6; border-radius: 50%; animation: thinkingBounce 1.4s ease-in-out 0.2s infinite;"></i>
                  <i style="display: inline-block; width: 8px; height: 8px; background: #3b82f6; border-radius: 50%; animation: thinkingBounce 1.4s ease-in-out 0.4s infinite;"></i>
                </div>
                <span
                  style="
                    margin-left: 12px;
                    color: var(--text-secondary);
                    font-size: 13px;
                  "
                  >思考中...</span
                >
              </div>
            </template>
            <template v-else>
              <!-- 语音会话结束标签渲染 -->
              <template v-if="message.messageType === 'voice-session-end'">
                <div class="voice-session-tag">
                  <div class="tag-left">
                    <svg
                      width="16"
                      height="16"
                      viewBox="0 0 24 24"
                      fill="currentColor"
                    >
                      <line
                        x1="6"
                        y1="8"
                        x2="6"
                        y2="16"
                        stroke="currentColor"
                        stroke-width="2"
                      />
                      <line
                        x1="10"
                        y1="6"
                        x2="10"
                        y2="18"
                        stroke="currentColor"
                        stroke-width="2"
                      />
                      <line
                        x1="14"
                        y1="6"
                        x2="14"
                        y2="18"
                        stroke="currentColor"
                        stroke-width="2"
                      />
                      <line
                        x1="18"
                        y1="8"
                        x2="18"
                        y2="16"
                        stroke="currentColor"
                        stroke-width="2"
                      />
                    </svg>
                  </div>
                  <div class="tag-main">
                    <div class="tag-title">语音聊天已结束</div>
                    <div class="tag-sub">
                      {{ formatDuration(message.duration || 0) }}
                    </div>
                  </div>
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
                      v-for="(item, i) in getRelatedReadings(message).slice(
                        0,
                        3
                      )"
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
          </template>
          <template v-else>
            <div
              class="user-bubble"
              :class="{ 'voice-message': message.messageType === 'voice' }"
              v-if="editingMessageId !== message.id"
            >
              <div
                class="md-content"
                v-html="renderMarkdown(message.content)"
              ></div>

              <!-- 语音消息额外信息：麦克风图标 + 时长 -->
              <div v-if="message.messageType === 'voice'" class="voice-meta">
                <svg
                  width="12"
                  height="12"
                  viewBox="0 0 24 24"
                  fill="currentColor"
                >
                  <path
                    d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"
                  ></path>
                  <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
                </svg>
                <span class="voice-duration">{{
                  formatDuration(message.duration || 0)
                }}</span>
              </div>
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
              v-if="message.role === 'user' && message.messageType !== 'voice'"
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
              <!-- 实心图标 (Active) -->
              <svg
                v-if="feedbackState.get(message.id) === 'up'"
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="currentColor"
                stroke="none"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <path
                  d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3zM7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3"
                ></path>
              </svg>
              <!-- 空心图标 (Inactive) -->
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
              <!-- 实心图标 (Active) -->
              <svg
                v-if="feedbackState.get(message.id) === 'down'"
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="currentColor"
                stroke="none"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <path
                  d="M10 15v4a3 3 0 0 0 3 3l4-9V2H5.72a2 2 0 0 0-2 1.7l-1.38 9a2 2 0 0 0 2 2.3zm7-13h2.67A2.31 2.31 0 0 1 22 4v7a2.31 2.31 0 0 1-2.33 2H17"
                ></path>
              </svg>
              <!-- 空心图标 (Inactive) -->
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
              v-if="
                message.role === 'assistant' &&
                message.messageType !== 'voice-session-end' &&
                message.noRegen !== true
              "
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
      <!-- 向下箭头：竖线+V形 -->
      <svg
        width="28"
        height="28"
        viewBox="0 0 24 24"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          d="M12 5L12 17"
          stroke="currentColor"
          stroke-width="2.5"
          stroke-linecap="round"
        />
        <path
          d="M7 13L12 18L17 13"
          stroke="currentColor"
          stroke-width="2.5"
          stroke-linecap="round"
          stroke-linejoin="round"
        />
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
            <!-- 录音中状态 (动态音量环) -->
            <svg
              v-if="isRecording"
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              class="voice-visualizer"
            >
              <!-- 背景圆环 -->
              <circle
                cx="12"
                cy="12"
                r="9"
                stroke="currentColor"
                stroke-width="2"
                opacity="0.18"
              />
              <!-- 动态音量环 -->
              <circle
                cx="12"
                cy="12"
                r="9"
                :stroke="'currentColor'"
                stroke-width="3.5"
                fill="none"
                :stroke-dasharray="2 * Math.PI * 9"
                :stroke-dashoffset="
                  2 * Math.PI * 9 * (1 - Math.min(audioLevel, 1))
                "
                stroke-linecap="round"
                style="
                  transition: stroke-dashoffset 0.15s
                    cubic-bezier(0.4, 0, 0.2, 1);
                "
                opacity="0.95"
              />
              <!-- 中心小圆点 -->
              <circle
                cx="12"
                cy="12"
                r="3.2"
                :fill="'currentColor'"
                opacity="0.85"
              />
            </svg>
            <!-- 默认麦克风图标 -->
            <svg
              v-else
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
              active: isVoiceMode && effectiveButtonMode === 'voice-mode',
              'send-mode': effectiveButtonMode === 'send',
              'stop-mode': effectiveButtonMode === 'stop',
            }"
            @click="handleMainButton"
            :disabled="
              isMobile && effectiveButtonMode === 'send' && !hasInputContent
            "
            :title="
              effectiveButtonMode === 'send'
                ? '发送消息'
                : effectiveButtonMode === 'stop'
                ? '停止生成'
                : '语音模式'
            "
          >
            <!-- 发送图标 (向上箭头) -->
            <svg
              v-if="effectiveButtonMode === 'send'"
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
              v-else-if="effectiveButtonMode === 'stop'"
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

    <!-- 回到底部按钮 -->
    <button
      v-show="showScrollToBottom"
      class="scroll-to-bottom"
      @click="scrollToBottomSmooth"
      aria-label="回到底部"
    >
      <!-- 向下箭头：竖线+V形 -->
      <svg
        width="28"
        height="28"
        viewBox="0 0 24 24"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          d="M12 5L12 17"
          stroke="currentColor"
          stroke-width="2.5"
          stroke-linecap="round"
        />
        <path
          d="M7 13L12 18L17 13"
          stroke="currentColor"
          stroke-width="2.5"
          stroke-linecap="round"
          stroke-linejoin="round"
        />
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
            <!-- 录音中状态 (动态音量环) -->
            <svg
              v-if="isRecording"
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              class="voice-visualizer"
            >
              <!-- 背景圆环 -->
              <circle
                cx="12"
                cy="12"
                r="9"
                stroke="currentColor"
                stroke-width="2"
                opacity="0.18"
              />
              <!-- 动态音量环 -->
              <circle
                cx="12"
                cy="12"
                r="9"
                :stroke="'currentColor'"
                stroke-width="3.5"
                fill="none"
                :stroke-dasharray="2 * Math.PI * 9"
                :stroke-dashoffset="
                  2 * Math.PI * 9 * (1 - Math.min(audioLevel, 1))
                "
                stroke-linecap="round"
                style="
                  transition: stroke-dashoffset 0.15s
                    cubic-bezier(0.4, 0, 0.2, 1);
                "
                opacity="0.95"
              />
              <!-- 中心小圆点 -->
              <circle
                cx="12"
                cy="12"
                r="3.2"
                :fill="'currentColor'"
                opacity="0.85"
              />
            </svg>
            <!-- 默认麦克风图标 -->
            <svg
              v-else
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
              active: isVoiceMode && effectiveButtonMode === 'voice-mode',
              'send-mode': effectiveButtonMode === 'send',
              'stop-mode': effectiveButtonMode === 'stop',
            }"
            @click="handleMainButton"
            :disabled="
              isMobile && effectiveButtonMode === 'send' && !hasInputContent
            "
            :title="
              effectiveButtonMode === 'send'
                ? '发送消息'
                : effectiveButtonMode === 'stop'
                ? '停止生成'
                : '语音模式'
            "
          >
            <!-- 发送图标 (向上箭头) -->
            <svg
              v-if="effectiveButtonMode === 'send'"
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
              v-else-if="effectiveButtonMode === 'stop'"
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

    <!-- 回到底部按钮 -->
    <button
      v-show="showScrollToBottom"
      class="scroll-to-bottom"
      @click="scrollToBottomSmooth"
      aria-label="回到底部"
    >
      <!-- 向下箭头：竖线+V形 -->
      <svg
        width="28"
        height="28"
        viewBox="0 0 24 24"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          d="M12 5L12 17"
          stroke="currentColor"
          stroke-width="2.5"
          stroke-linecap="round"
        />
        <path
          d="M7 13L12 18L17 13"
          stroke="currentColor"
          stroke-width="2.5"
          stroke-linecap="round"
          stroke-linejoin="round"
        />
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
            <!-- 录音中状态 (动态音量环) -->
            <svg
              v-if="isRecording"
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              class="voice-visualizer"
            >
              <!-- 背景圆环 -->
              <circle
                cx="12"
                cy="12"
                r="9"
                stroke="currentColor"
                stroke-width="2"
                opacity="0.18"
              />
              <!-- 动态音量环 -->
              <circle
                cx="12"
                cy="12"
                r="9"
                :stroke="'currentColor'"
                stroke-width="3.5"
                fill="none"
                :stroke-dasharray="2 * Math.PI * 9"
                :stroke-dashoffset="
                  2 * Math.PI * 9 * (1 - Math.min(audioLevel, 1))
                "
                stroke-linecap="round"
                style="
                  transition: stroke-dashoffset 0.15s
                    cubic-bezier(0.4, 0, 0.2, 1);
                "
                opacity="0.95"
              />
              <!-- 中心小圆点 -->
              <circle
                cx="12"
                cy="12"
                r="3.2"
                :fill="'currentColor'"
                opacity="0.85"
              />
            </svg>
            <!-- 默认麦克风图标 -->
            <svg
              v-else
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
              active: isVoiceMode && effectiveButtonMode === 'voice-mode',
              'send-mode': effectiveButtonMode === 'send',
              'stop-mode': effectiveButtonMode === 'stop',
            }"
            @click="handleMainButton"
            :disabled="
              isMobile && effectiveButtonMode === 'send' && !hasInputContent
            "
            :title="
              effectiveButtonMode === 'send'
                ? '发送消息'
                : effectiveButtonMode === 'stop'
                ? '停止生成'
                : '语音模式'
            "
          >
            <!-- 发送图标 (向上箭头) -->
            <svg
              v-if="effectiveButtonMode === 'send'"
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
              v-else-if="effectiveButtonMode === 'stop'"
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

    <!-- 回到底部按钮 -->
    <button
      v-show="showScrollToBottom"
      class="scroll-to-bottom"
      @click="scrollToBottomSmooth"
      aria-label="回到底部"
    >
      <!-- 向下箭头：竖线+V形 -->
      <svg
        width="28"
        height="28"
        viewBox="0 0 24 24"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          d="M12 5L12 17"
          stroke="currentColor"
          stroke-width="2.5"
          stroke-linecap="round"
        />
        <path
          d="M7 13L12 18L17 13"
          stroke="currentColor"
          stroke-width="2.5"
          stroke-linecap="round"
          stroke-linejoin="round"
        />
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
            <!-- 录音中状态 (动态音量环) -->
            <svg
              v-if="isRecording"
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              class="voice-visualizer"
            >
              <!-- 背景圆环 -->
              <circle
                cx="12"
                cy="12"
                r="9"
                stroke="currentColor"
                stroke-width="2"
                opacity="0.18"
              />
              <!-- 动态音量环 -->
              <circle
                cx="12"
                cy="12"
                r="9"
                :stroke="'currentColor'"
                stroke-width="3.5"
                fill="none"
                :stroke-dasharray="2 * Math.PI * 9"
                :stroke-dashoffset="
                  2 * Math.PI * 9 * (1 - Math.min(audioLevel, 1))
                "
                stroke-linecap="round"
                style="
                  transition: stroke-dashoffset 0.15s
                    cubic-bezier(0.4, 0, 0.2, 1);
                "
                opacity="0.95"
              />
              <!-- 中心小圆点 -->
              <circle
                cx="12"
                cy="12"
                r="3.2"
                :fill="'currentColor'"
                opacity="0.85"
              />
            </svg>
            <!-- 默认麦克风图标 -->
            <svg
              v-else
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
              active: isVoiceMode && effectiveButtonMode === 'voice-mode',
              'send-mode': effectiveButtonMode === 'send',
              'stop-mode': effectiveButtonMode === 'stop',
            }"
            @click="handleMainButton"
            :disabled="
              isMobile && effectiveButtonMode === 'send' && !hasInputContent
            "
            :title="
              effectiveButtonMode === 'send'
                ? '发送消息'
                : effectiveButtonMode === 'stop'
                ? '停止生成'
                : '语音模式'
            "
          >
            <!-- 发送图标 (向上箭头) -->
            <svg
              v-if="effectiveButtonMode === 'send'"
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
              v-else-if="effectiveButtonMode === 'stop'"
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

    <!-- 回到底部按钮 -->
    <button
      v-show="showScrollToBottom"
      class="scroll-to-bottom"
      @click="scrollToBottomSmooth"
      aria-label="回到底部"
    >
      <!-- 向下箭头：竖线+V形 -->
      <svg
        width="28"
        height="28"
        viewBox="0 0 24 24"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          d="M12 5L12 17"
          stroke="currentColor"
          stroke-width="2.5"
          stroke-linecap="round"
        />
        <path
          d="M7 13L12 18L17 13"
          stroke="currentColor"
          stroke-width="2.5"
          stroke-linecap="round"
          stroke-linejoin="round"
        />
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
            <!-- 录音中状态 (动态音量环) -->
            <svg
              v-if="isRecording"
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              class="voice-visualizer"
            >
              <!-- 背景圆环 -->
              <circle
                cx="12"
                cy="12"
                r="9"
                stroke="currentColor"
                stroke-width="2"
                opacity="0.18"
              />
              <!-- 动态音量环 -->
              <circle
                cx="12"
                cy="12"
                r="9"
                :stroke="'currentColor'"
                stroke-width="3.5"
                fill="none"
                :stroke-dasharray="2 * Math.PI * 9"
                :stroke-dashoffset="
                  2 * Math.PI * 9 * (1 - Math.min(audioLevel, 1))
                "
                stroke-linecap="round"
                style="
                  transition: stroke-dashoffset 0.15s
                    cubic-bezier(0.4, 0, 0.2, 1);
                "
                opacity="0.95"
              />
              <!-- 中心小圆点 -->
              <circle
                cx="12"
                cy="12"
                r="3.2"
                :fill="'currentColor'"
                opacity="0.85"
              />
            </svg>
            <!-- 默认麦克风图标 -->
            <svg
              v-else
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
              active: isVoiceMode && effectiveButtonMode === 'voice-mode',
              'send-mode': effectiveButtonMode === 'send',
              'stop-mode': effectiveButtonMode === 'stop',
            }"
            @click="handleMainButton"
            :disabled="
              isMobile && effectiveButtonMode === 'send' && !hasInputContent
            "
            :title="
              effectiveButtonMode === 'send'
                ? '发送消息'
                : effectiveButtonMode === 'stop'
                ? '停止生成'
                : '语音模式'
            "
          >
            <!-- 发送图标 (向上箭头) -->
            <svg
              v-if="effectiveButtonMode === 'send'"
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
              v-else-if="effectiveButtonMode === 'stop'"
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

    <!-- 回到底部按钮 -->
    <button
      v-show="showScrollToBottom"
      class="scroll-to-bottom"
      @click="scrollToBottomSmooth"
      aria-label="回到底部"
    >
      <!-- 向下箭头：竖线+V形 -->
      <svg
        width="28"
        height="28"
        viewBox="0 0 24 24"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          d="M12 5L12 17"
          stroke="currentColor"
          stroke-width="2.5"
          stroke-linecap="round"
        />
        <path
          d="M7 13L12 18L17 13"
          stroke="currentColor"
          stroke-width="2.5"
          stroke-linecap="round"
          stroke-linejoin="round"
        />
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
            <!-- 录音中状态 (动态音量环) -->
            <svg
              v-if="isRecording"
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              class="voice-visualizer"
            >
              <!-- 背景圆环 -->
              <circle
                cx="12"
                cy="12"
                r="9"
                stroke="currentColor"
                stroke-width="2"
                opacity="0.18"
              />
              <!-- 动态音量环 -->
              <circle
                cx="12"
                cy="12"
                r="9"
                :stroke="'currentColor'"
                stroke-width="3.5"
                fill="none"
                :stroke-dasharray="2 * Math.PI * 9"
                :stroke-dashoffset="
                  2 * Math.PI * 9 * (1 - Math.min(audioLevel, 1))
                "
                stroke-linecap="round"
                style="
                  transition: stroke-dashoffset 0.15s
                    cubic-bezier(0.4, 0, 0.2, 1);
                "
                opacity="0.95"
              />
              <!-- 中心小圆点 -->
              <circle
                cx="12"
                cy="12"
                r="3.2"
                :fill="'currentColor'"
                opacity="0.85"
              />
            </svg>
            <!-- 默认麦克风图标 -->
            <svg
              v-else
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
              active: isVoiceMode && effectiveButtonMode === 'voice-mode',
              'send-mode': effectiveButtonMode === 'send',
              'stop-mode': effectiveButtonMode === 'stop',
            }"
            @click="handleMainButton"
            :disabled="
              isMobile && effectiveButtonMode === 'send' && !hasInputContent
            "
            :title="
              effectiveButtonMode === 'send'
                ? '发送消息'
                : effectiveButtonMode === 'stop'
                ? '停止生成'
                : '语音模式'
            "
          >
            <!-- 发送图标 (向上箭头) -->
            <svg
              v-if="effectiveButtonMode === 'send'"
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
              v-else-if="effectiveButtonMode === 'stop'"
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

    <!-- 回到底部按钮 -->
    <button
      v-show="showScrollToBottom"
      class="scroll-to-bottom"
      @click="scrollToBottomSmooth"
      aria-label="回到底部"
    >
      <!-- 向下箭头：竖线+V形 -->
      <svg
        width="28"
        height="28"
        viewBox="0 0 24 24"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          d="M12 5L12 17"
          stroke="currentColor"
          stroke-width="2.5"
          stroke-linecap="round"
        />
        <path
          d="M7 13L12 18L17 13"
          stroke="currentColor"
          stroke-width="2.5"
          stroke-linecap="round"
          stroke-linejoin="round"
        />
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
            <!-- 录音中状态 (动态音量环) -->
            <svg
              v-if="isRecording"
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              class="voice-visualizer"
            >
              <!-- 背景圆环 -->
              <circle
                cx="12"
                cy="12"
                r="9"
                stroke="currentColor"
                stroke-width="2"
                opacity="0.18"
              />
              <!-- 动态音量环 -->
              <circle
                cx="12"
                cy="12"
                r="9"
                :stroke="'currentColor'"
                stroke-width="3.5"
                fill="none"
                :stroke-dasharray="2 * Math.PI * 9"
                :stroke-dashoffset="
                  2 * Math.PI * 9 * (1 - Math.min(audioLevel, 1))
                "
                stroke-linecap="round"
                style="
                  transition: stroke-dashoffset 0.15s
                    cubic-bezier(0.4, 0, 0.2, 1);
                "
                opacity="0.95"
              />
              <!-- 中心小圆点 -->
              <circle
                cx="12"
                cy="12"
                r="3.2"
                :fill="'currentColor'"
                opacity="0.85"
              />
            </svg>
            <!-- 默认麦克风图标 -->
            <svg
              v-else
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
              active: isVoiceMode && effectiveButtonMode === 'voice-mode',
              'send-mode': effectiveButtonMode === 'send',
              'stop-mode': effectiveButtonMode === 'stop',
            }"
            @click="handleMainButton"
            :disabled="
              isMobile && effectiveButtonMode === 'send' && !hasInputContent
            "
            :title="
              effectiveButtonMode === 'send'
                ? '发送消息'
                : effectiveButtonMode === 'stop'
                ? '停止生成'
                : '语音模式'
            "
          >
            <!-- 发送图标 (向上箭头) -->
            <svg
              v-if="effectiveButtonMode === 'send'"
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
              v-else-if="effectiveButtonMode === 'stop'"
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

    <!-- 回到底部按钮 -->
    <button
      v-show="showScrollToBottom"
      class="scroll-to-bottom"
      @click="scrollToBottomSmooth"
      aria-label="回到底部"
    >
      <!-- 向下箭头：竖线+V形 -->
      <svg
        width="28"
        height="28"
        viewBox="0 0 24 24"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          d="M12 5L12 17"
          stroke="currentColor"
          stroke-width="2.5"
          stroke-linecap="round"
        />
        <path
          d="M7 13L12 18L17 13"
          stroke="currentColor"
          stroke-width="2.5"
          stroke-linecap="round"
          stroke-linejoin="round"
        />
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
            <!-- 录音中状态 (动态音量环) -->
            <svg
              v-if="isRecording"
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              class="voice-visualizer"
            >
              <!-- 背景圆环 -->
              <circle
                cx="12"
                cy="12"
                r="9"
                stroke="currentColor"
                stroke-width="2"
                opacity="0.18"
              />
              <!-- 动态音量环 -->
              <circle
                cx="12"
                cy="12"
                r="9"
                :stroke="'currentColor'"
                stroke-width="3.5"
                fill="none"
                :stroke-dasharray="2 * Math.PI * 9"
                :stroke-dashoffset="
                  2 * Math.PI * 9 * (1 - Math.min(audioLevel, 1))
                "
                stroke-linecap="round"
                style="
                  transition: stroke-dashoffset 0.15s
                    cubic-bezier(0.4, 0, 0.2, 1);
                "
                opacity="0.95"
              />
              <!-- 中心小圆点 -->
              <circle
                cx="12"
                cy="12"
                r="3.2"
                :fill="'currentColor'"
                opacity="0.85"
              />
            </svg>
            <!-- 默认麦克风图标 -->
            <svg
              v-else
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
              active: isVoiceMode && effectiveButtonMode === 'voice-mode',
              'send-mode': effectiveButtonMode === 'send',
              'stop-mode': effectiveButtonMode === 'stop',
            }"
            @click="handleMainButton"
            :disabled="
              isMobile && effectiveButtonMode === 'send' && !hasInputContent
            "
            :title="
              effectiveButtonMode === 'send'
                ? '发送消息'
                : effectiveButtonMode === 'stop'
                ? '停止生成'
                : '语音模式'
            "
          >
            <!-- 发送图标 (向上箭头) -->
            <svg
              v-if="effectiveButtonMode === 'send'"
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
              v-else-if="effectiveButtonMode === 'stop'"
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

    <!-- 回到底部按钮 -->
    <button
      v-show="showScrollToBottom"
      class="scroll-to-bottom"
      @click="scrollToBottomSmooth"
      aria-label="回到底部"
    >
      <!-- 向下箭头：竖线+V形 -->
      <svg
        width="28"
        height="28"
        viewBox="0 0 24 24"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          d="M12 5L12 17"
          stroke="currentColor"
          stroke-width="2.5"
          stroke-linecap="round"
        />
        <path
          d="M7 13L12 18L17 13"
          stroke="currentColor"
          stroke-width="2.5"
          stroke-linecap="round"
          stroke-linejoin="round"
        />
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
            <!-- 录音中状态 (动态音量环) -->
            <svg
              v-if="isRecording"
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              class="voice-visualizer"
            >
              <!-- 背景圆环 -->
              <circle
                cx="12"
                cy="12"
                r="9"
                stroke="currentColor"
                stroke-width="2"
                opacity="0.18"
              />
              <!-- 动态音量环 -->
              <circle
                cx="12"
                cy="12"
                r="9"
                :stroke="'currentColor'"
                stroke-width="3.5"
                fill="none"
                :stroke-dasharray="2 * Math.PI * 9"
                :stroke-dashoffset="
                  2 * Math.PI * 9 * (1 - Math.min(audioLevel, 1))
                "
                stroke-linecap="round"
                style="
                  transition: stroke-dashoffset 0.15s
                    cubic-bezier(0.4, 0, 0.2, 1);
                "
                opacity="0.95"
              />
              <!-- 中心小圆点 -->
              <circle
                cx="12"
                cy="12"
                r="3.2"
                :fill="'currentColor'"
                opacity="0.85"
              />
            </svg>
            <!-- 默认麦克风图标 -->
            <svg
              v-else
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
              active: isVoiceMode && effectiveButtonMode === 'voice-mode',
              'send-mode': effectiveButtonMode === 'send',
              'stop-mode': effectiveButtonMode === 'stop',
            }"
            @click="handleMainButton"
            :disabled="
              isMobile && effectiveButtonMode === 'send' && !hasInputContent
            "
            :title="
              effectiveButtonMode === 'send'
                ? '发送消息'
                : effectiveButtonMode === 'stop'
                ? '停止生成'
                : '语音模式'
            "
          >
            <!-- 发送图标 (向上箭头) -->
            <svg
              v-if="effectiveButtonMode === 'send'"
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
              v-else-if="effectiveButtonMode === 'stop'"
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

    <!-- 回到底部按钮 -->
    <button
      v-show="showScrollToBottom"
      class="scroll-to-bottom"
      @click="scrollToBottomSmooth"
      aria-label="回到底部"
    >
      <!-- 向下箭头：竖线+V形 -->
      <svg
        width="28"
        height="28"
        viewBox="0 0 24 24"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          d="M12 5L12 17"
          stroke="currentColor"
          stroke-width="2.5"
          stroke-linecap="round"
        />
        <path
          d="M7 13L12 18L17 13"
          stroke="currentColor"
          stroke-width="2.5"
          stroke-linecap="round"
          stroke-linejoin="round"
        />
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
            <!-- 录音中状态 (动态音量环) -->
            <svg
              v-if="isRecording"
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              class="voice-visualizer"
            >
              <!-- 背景圆环 -->
              <circle
                cx="12"
                cy="12"
                r="9"
                stroke="currentColor"
                stroke-width="2"
                opacity="0.18"
              />
              <!-- 动态音量环 -->
              <circle
                cx="12"
                cy="12"
                r="9"
                :stroke="'currentColor'"
                stroke-width="3.5"
                fill="none"
                :stroke-dasharray="2 * Math.PI * 9"
                :stroke-dashoffset="
                  2 * Math.PI * 9 * (1 - Math.min(audioLevel, 1))
                "
                stroke-linecap="round"
                style="
                  transition: stroke-dashoffset 0.15s
                    cubic-bezier(0.4, 0, 0.2, 1);
                "
                opacity="0.95"
              />
              <!-- 中心小圆点 -->
              <circle
                cx="12"
                cy="12"
                r="3.2"
                :fill="'currentColor'"
                opacity="0.85"
              />
            </svg>
            <!-- 默认麦克风图标 -->
            <svg
              v-else
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
              <line
  color: var(--text-secondary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1.5;
}

/* 思考动画 - 全局定义 */
@keyframes thinkingBounce {
  0%, 60%, 100% {
    transform: translateY(0);
  }
  30% {
    transform: translateY(-10px);
  }
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
