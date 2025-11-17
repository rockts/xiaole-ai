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
            const data = await api.getSession(sessionId)
            sessionInfo.value = {
                id: sessionId,
                title: data.title
            }
            messages.value = data.messages || data.history || []
            currentSessionId.value = sessionId
        } catch (error) {
            console.error('Failed to load session:', error)
        }
    }

    const sendMessage = async (content, imagePath = null, router = null) => {
        try {
            // 添加用户消息
            messages.value.push({
                id: Date.now(),
                role: 'user',
                content,
                image_path: imagePath
            })

            isTyping.value = true

            const response = await api.sendMessage({
                user_id: 'default_user',
                session_id: currentSessionId.value || '',
                prompt: content,
                image_path: imagePath
            })

            // 更新 session_id（无论是新会话还是已存在的会话）
            if (response.session_id) {
                const isNewSession = !currentSessionId.value
                currentSessionId.value = response.session_id

                if (isNewSession) {
                    // 新会话：设置标题并更新路由
                    sessionInfo.value = {
                        id: response.session_id,
                        title: content.substring(0, 30) + (content.length > 30 ? '...' : '')
                    }
                    // 使用 router 更新路由
                    if (router) {
                        router.push(`/chat/${response.session_id}`)
                    }
                }
            }

            // 添加 AI 回复（后端返回字段是 reply 不是 response）
            messages.value.push({
                id: Date.now() + 1,
                role: 'assistant',
                content: response.reply || response.response || ''
            })

            // 刷新会话列表
            await loadSessions()
        } catch (error) {
            console.error('Failed to send message:', error)
        } finally {
            isTyping.value = false
        }
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
        uploadImage,
        clearCurrentSession
    }
})
