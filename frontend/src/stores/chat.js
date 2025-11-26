import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/services/api'

export const useChatStore = defineStore('chat', () => {
    const sessions = ref([])
    const messages = ref([])
    const sessionInfo = ref(null)
    const currentSessionId = ref(null)
    const isTyping = ref(false)
    const loading = ref(false)

    const loadSessions = async (forceRefresh = false) => {
        try {
            loading.value = true
            const data = await api.getSessions(forceRefresh)
            // 将 session_id 映射为 id，保持字段一致性
            sessions.value = (data.sessions || []).map(s => ({
                ...s,
                id: s.session_id || s.id
            }))
            console.log('✅ Sessions loaded:', sessions.value.length)
        } catch (error) {
            console.error('Failed to load sessions:', error)
        } finally {
            loading.value = false
        }
    }

    const loadSession = async (sessionId) => {
        try {
            console.log('🔄 Loading session:', sessionId)
            // 请求更多历史记录，防止长对话被截断
            const data = await api.getSession(sessionId, 500)
            console.log('📦 Session data received:', data)
            console.log('💬 Messages:', data.messages || data.history || [])
            sessionInfo.value = {
                id: sessionId,
                title: data.title
            }
            const loadedMessages = data.messages || data.history || []
            messages.value = loadedMessages.map(msg => ({
                ...msg,
                status: 'done'
            }))
            currentSessionId.value = sessionId
            console.log('✅ Session loaded, messages count:', messages.value.length)
        } catch (error) {
            console.error('❌ Failed to load session:', error)
        }
    }

    const typingTimer = ref(null)
    const activeTypingMessageId = ref(null)
    const activeStreamAbort = ref(null)

    const sendMessage = async (content, imagePath = null, router = null, options = {}) => {
        try {
            const instant = !!options.instant // 语音模式：立即展示，不走打字动画
            const responseStyle = options.responseStyle || 'balanced'

            // ChatView.vue 已立即插入用户消息，这里不再重复插入
            isTyping.value = !instant

            // 插入思考占位消息（保持对话顺序，添加到末尾）
            const placeholderId = Date.now() + 1
            activeTypingMessageId.value = placeholderId
            messages.value.push({
                id: placeholderId,
                role: 'assistant',
                content: instant ? '…' : '', // 语音模式先占位省时反馈
                status: instant ? 'typing' : 'thinking'
            })

            const response = await api.sendMessage({
                user_id: 'default_user',
                session_id: currentSessionId.value || '',
                prompt: content,
                image_path: imagePath,
                response_style: responseStyle
            })

            // 更新 session 信息
            if (response.session_id) {
                const isNewSession = !currentSessionId.value
                currentSessionId.value = response.session_id
                if (isNewSession) {
                    sessionInfo.value = {
                        id: response.session_id,
                        title: content.substring(0, 30) + (content.length > 30 ? '...' : '')
                    }
                    if (router) router.push(`/chat/${response.session_id}`)
                }
            }

            // 获取最终文本
            const full = response.reply || response.response || ''
            const msgIndex = messages.value.findIndex(m => m.id === placeholderId)

            // 同步最新的消息ID
            if (msgIndex !== -1) {
                // 1. 更新 AI 回复的消息 ID
                if (response.assistant_message_id) {
                    messages.value[msgIndex].id = response.assistant_message_id
                }

                // 2. 更新用户消息的 ID
                if (response.user_message_id) {
                    // 向前查找最近的一条临时ID的用户消息
                    for (let i = msgIndex - 1; i >= 0; i--) {
                        const msg = messages.value[i]
                        if (msg.role === 'user' && String(msg.id).startsWith('temp-')) {
                            console.log('✅ Syncing user message ID:', msg.id, '->', response.user_message_id)
                            messages.value[i].id = response.user_message_id
                            break
                        }
                    }
                }
            }

            if (msgIndex !== -1) {
                messages.value[msgIndex].fullContent = full
                if (instant) {
                    messages.value[msgIndex].content = full
                    messages.value[msgIndex].status = 'done'
                    isTyping.value = false
                    // 语音模式：派发事件供 ChatView 触发TTS朗读
                    if (typeof window !== 'undefined') {
                        window.dispatchEvent(new CustomEvent('voiceAssistantReply', {
                            detail: { text: full }
                        }))
                    }
                } else {
                    messages.value[msgIndex].status = 'typing'
                    messages.value[msgIndex].content = ''
                }

                // 保存搜索结果
                if (response.search_results) {
                    messages.value[msgIndex].search_results = response.search_results
                }

                if (!instant) {
                    let i = 0
                    const step = Math.max(1, Math.round(full.length / 60)) // 约1秒60步
                    typingTimer.value = setInterval(() => {
                        if (i >= full.length) {
                            clearInterval(typingTimer.value)
                            typingTimer.value = null
                            messages.value[msgIndex].content = full
                            messages.value[msgIndex].status = 'done'
                            isTyping.value = false
                            return
                        }
                        messages.value[msgIndex].content = full.slice(0, i)
                        i += step
                    }, 16) // ~60fps
                }
            }

            await loadSessions(true) // 强制刷新会话列表
            console.log('✅ Sessions refreshed after message sent')
        } catch (error) {
            console.error('Failed to send message:', error)
            // 错误时撤销占位或显示错误
            if (activeTypingMessageId.value) {
                const msgIndex = messages.value.findIndex(m => m.id === activeTypingMessageId.value)
                if (msgIndex !== -1) {
                    messages.value[msgIndex].status = 'done'
                    const errorMsg = error.response?.data?.detail || '出错了，请稍后重试。'
                    messages.value[msgIndex].content = `⚠️ ${errorMsg}`
                }
            }
        } finally {
            // 如果仍在打字由定时器结束时处理 isTyping
            if (!typingTimer.value) {
                isTyping.value = false
            }
        }
    }

    // 流式发送消息（SSE 切片流）
    const sendMessageStreamed = async (content, imagePath = null, router = null, options = {}) => {
        const responseStyle = options.responseStyle || 'balanced'
        try {
            // 插入思考占位消息
            isTyping.value = true
            const placeholderId = Date.now() + 1
            activeTypingMessageId.value = placeholderId
            const thinkingMsg = {
                id: placeholderId,
                role: 'assistant',
                content: '',
                status: 'thinking'
            }
            messages.value.push(thinkingMsg)
            console.log('💭 Thinking message added:', thinkingMsg)

            // 构建中止控制器
            const controller = new AbortController()
            activeStreamAbort.value = controller

            // 首次 start 时切换为 typing
            let msgIndex = -1
            let accumulated = ''

            const onStart = () => {
                if (msgIndex === -1) {
                    msgIndex = messages.value.findIndex(m => m.id === placeholderId)
                }
                if (msgIndex !== -1) {
                    messages.value[msgIndex].status = 'typing'
                }
            }

            const onDelta = (chunk) => {
                if (msgIndex === -1) {
                    msgIndex = messages.value.findIndex(m => m.id === placeholderId)
                }
                accumulated += chunk || ''
                if (msgIndex !== -1) {
                    messages.value[msgIndex].content = accumulated
                }
            }

            const onEnd = async (payload) => {
                if (msgIndex === -1) {
                    msgIndex = messages.value.findIndex(m => m.id === placeholderId)
                }
                if (msgIndex !== -1) {
                    // 同步 ID
                    if (payload?.assistant_message_id) {
                        messages.value[msgIndex].id = payload.assistant_message_id
                    }
                    // 同步前一条用户消息 ID
                    if (payload?.user_message_id) {
                        for (let i = msgIndex - 1; i >= 0; i--) {
                            const msg = messages.value[i]
                            if (msg.role === 'user' && String(msg.id).startsWith('temp-')) {
                                messages.value[i].id = payload.user_message_id
                                break
                            }
                        }
                    }
                    messages.value[msgIndex].status = 'done'
                }

                // 更新会话并路由
                if (payload?.session_id) {
                    const isNew = !currentSessionId.value
                    currentSessionId.value = payload.session_id
                    if (isNew) {
                        sessionInfo.value = {
                            id: payload.session_id,
                            title: content.substring(0, 30) + (content.length > 30 ? '...' : '')
                        }
                        if (router) router.push(`/chat/${payload.session_id}`)
                    }
                }

                isTyping.value = false
                activeStreamAbort.value = null
                await loadSessions(true) // 强制刷新会话列表
                console.log('✅ Sessions refreshed after streamed message')
            }

            await api.streamChat({
                user_id: 'default_user',
                session_id: currentSessionId.value || '',
                prompt: content,
                image_path: imagePath,
                response_style: responseStyle
            }, { onStart, onDelta, onEnd, signal: controller.signal })
        } catch (error) {
            console.error('Failed to send message (stream):', error)
            if (activeTypingMessageId.value) {
                const msgIndex = messages.value.findIndex(m => m.id === activeTypingMessageId.value)
                if (msgIndex !== -1) {
                    messages.value[msgIndex].status = 'done'
                    const errText = error?.message || '出错了，请稍后重试。'
                    messages.value[msgIndex].content = `⚠️ ${errText}`
                }
            }
        } finally {
            isTyping.value = false
            activeStreamAbort.value = null
        }
    }

    const stopGeneration = () => {
        if (typingTimer.value && activeTypingMessageId.value) {
            clearInterval(typingTimer.value)
            typingTimer.value = null
            const msgIndex = messages.value.findIndex(m => m.id === activeTypingMessageId.value)
            if (msgIndex !== -1) {
                const full = messages.value[msgIndex].fullContent || ''
                messages.value[msgIndex].content = full
                messages.value[msgIndex].status = 'done'
            }
        }
        // 取消流式
        if (activeStreamAbort.value) {
            try { activeStreamAbort.value.abort() } catch (_) { }
            activeStreamAbort.value = null
        }
        isTyping.value = false
    }

    const uploadImage = async (file) => {
        try {
            const formData = new FormData()
            formData.append('file', file)

            const response = await api.uploadImage(formData)
            return response.file_path
        } catch (error) {
            console.error('Failed to upload image:', error)
            return null
        }
    }

    const uploadDocument = async (file) => {
        try {
            const formData = new FormData()
            formData.append('file', file)
            formData.append('user_id', 'default_user')
            if (currentSessionId.value) {
                formData.append('session_id', currentSessionId.value)
            }

            const response = await api.uploadDocument(formData)
            return response
        } catch (error) {
            console.error('Failed to upload document:', error)
            throw error
        }
    }

    const clearCurrentSession = () => {
        messages.value = []
        sessionInfo.value = null
        currentSessionId.value = null
    }

    const deleteMessage = (messageId) => {
        const index = messages.value.findIndex(m => m.id === messageId)
        if (index !== -1) {
            messages.value.splice(index, 1)
        }
    }

    const deleteMessageApi = async (messageId) => {
        try {
            await api.deleteMessage(messageId)
        } catch (error) {
            console.error('Failed to delete message from backend:', error)
        }
    }

    const submitFeedback = async (data) => {
        try {
            return await api.submitFeedback(data)
        } catch (error) {
            console.error('Failed to submit feedback:', error)
            return { success: false, error }
        }
    }

    return {
        sessions,
        messages,
        sessionInfo,
        currentSessionId,
        isTyping,
        loading,
        loadSessions,
        loadSession,
        sendMessage,
        sendMessageStreamed,
        stopGeneration,
        uploadImage,
        uploadDocument,
        clearCurrentSession,
        deleteMessage,
        deleteMessageApi, // Export this
        submitFeedback
    }
})
