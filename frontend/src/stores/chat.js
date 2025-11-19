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

    const loadSessions = async () => {
        try {
            loading.value = true
            const data = await api.getSessions(true)
            // 将 session_id 映射为 id，保持字段一致性
            sessions.value = (data.sessions || []).map(s => ({
                ...s,
                id: s.session_id || s.id
            }))
        } catch (error) {
            console.error('Failed to load sessions:', error)
        } finally {
            loading.value = false
        }
    }

    const loadSession = async (sessionId) => {
        try {
            console.log('🔄 Loading session:', sessionId)
            const data = await api.getSession(sessionId)
            console.log('📦 Session data received:', data)
            console.log('💬 Messages:', data.messages || data.history || [])
            sessionInfo.value = {
                id: sessionId,
                title: data.title
            }
            messages.value = data.messages || data.history || []
            currentSessionId.value = sessionId
            console.log('✅ Session loaded, messages count:', messages.value.length)
        } catch (error) {
            console.error('❌ Failed to load session:', error)
        }
    }

    const typingTimer = ref(null)
    const activeTypingMessageId = ref(null)

    const sendMessage = async (content, imagePath = null, router = null) => {
        try {
            // ChatView.vue 已立即插入用户消息，这里不再重复插入
            isTyping.value = true

            // 插入思考占位消息
            const placeholderId = Date.now() + 1
            activeTypingMessageId.value = placeholderId
            messages.value.push({
                id: placeholderId,
                role: 'assistant',
                content: '',
                status: 'thinking'
            })

            const response = await api.sendMessage({
                user_id: 'default_user',
                session_id: currentSessionId.value || '',
                prompt: content,
                image_path: imagePath
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
            if (msgIndex !== -1) {
                messages.value[msgIndex].status = 'typing'
                messages.value[msgIndex].fullContent = full
                messages.value[msgIndex].content = ''

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

            await loadSessions()
        } catch (error) {
            console.error('Failed to send message:', error)
            // 错误时撤销占位或显示错误
            if (activeTypingMessageId.value) {
                const msgIndex = messages.value.findIndex(m => m.id === activeTypingMessageId.value)
                if (msgIndex !== -1) {
                    messages.value[msgIndex].status = 'done'
                    messages.value[msgIndex].content = '⚠️ 出错了，请稍后重试。'
                }
            }
        } finally {
            // 如果仍在打字由定时器结束时处理 isTyping
            if (!typingTimer.value) {
                isTyping.value = false
            }
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
        isTyping.value = false
    }

    const uploadImage = async (file) => {
        try {
            const formData = new FormData()
            formData.append('image', file)

            const response = await api.uploadImage(formData)
            return response.image_path
        } catch (error) {
            console.error('Failed to upload image:', error)
            return null
        }
    }

    const clearCurrentSession = () => {
        messages.value = []
        sessionInfo.value = null
        currentSessionId.value = null
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
        stopGeneration,
        uploadImage,
        clearCurrentSession
    }
})
