import axios from 'axios'

const api = axios.create({
    baseURL: import.meta.env.VITE_API_BASE || '',
    timeout: 30000,
    headers: {
        'Content-Type': 'application/json'
    }
})

// 自动重试配置
const MAX_RETRIES = 3
const RETRY_DELAY = 1000 // 毫秒

// 请求拦截器
api.interceptors.request.use(
    config => {
        // 初始化重试计数
        config.retryCount = config.retryCount || 0
        return config
    },
    error => {
        return Promise.reject(error)
    }
)

// 响应拦截器 - 添加自动重试逻辑
api.interceptors.response.use(
    response => response.data,
    async error => {
        const config = error.config

        // 如果没有配置或已达到最大重试次数，直接拒绝
        if (!config || config.retryCount >= MAX_RETRIES) {
            console.error('API Error (final):', error.message)
            return Promise.reject(error)
        }

        // 只对网络错误或 5xx 错误重试
        const shouldRetry =
            !error.response || // 网络错误（后端未响应）
            (error.response.status >= 500 && error.response.status < 600) // 服务器错误

        if (!shouldRetry) {
            console.error('API Error:', error.message)
            return Promise.reject(error)
        }

        // 增加重试计数
        config.retryCount += 1
        const delay = RETRY_DELAY * config.retryCount

        console.warn(`API 请求失败，${delay}ms 后进行第 ${config.retryCount} 次重试...`)

        // 等待后重试
        await new Promise(resolve => setTimeout(resolve, delay))
        return api(config)
    }
)

export default {
    // 会话相关
    getSessions(allSessions = true) {
        return api.get('/sessions', { params: { all_sessions: allSessions } })
    },

    getSession(sessionId, limit = 200) {
        return api.get(`/session/${sessionId}`, { params: { limit } })
    },

    deleteSession(sessionId) {
        return api.delete(`/api/chat/sessions/${sessionId}`)
    },

    deleteMessage(messageId) {
        return api.delete(`/api/messages/${messageId}`)
    },

    sendMessage(data) {
        // 后端使用查询参数而不是 POST body
        const params = new URLSearchParams()
        if (data.prompt) params.append('prompt', data.prompt)
        if (data.session_id) params.append('session_id', data.session_id)
        if (data.user_id) params.append('user_id', data.user_id)
        if (data.response_style) params.append('response_style', data.response_style)
        if (data.image_path) params.append('image_path', data.image_path)

        // 增加超时时间到 120 秒，并禁用自动重试
        return api.post(`/chat?${params.toString()}`, null, {
            timeout: 120000,
            retryCount: MAX_RETRIES // 设置为最大重试次数，防止拦截器重试
        })
    },

    uploadImage(formData) {
        return api.post('/api/vision/upload', formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
        })
    },

    // 记忆相关
    getMemoryStats() {
        return api.get('/memory/stats')
    },

    getRecentMemories(hours = 24, limit = 20, tag = null) {
        return api.get('/memory/recent', { params: { hours, limit, tag } })
    },

    searchMemories(keywords) {
        // ...existing code...
        return api.get('/memory/search', { params: { keywords } })
    },

    semanticSearch(query) {
        return api.get('/memory/semantic', { params: { query } })
    },

    deleteMemory(memoryId) {
        return api.delete(`/api/memory/${memoryId}`)
    },

    updateMemory(memoryId, data) {
        return api.put(`/api/memory/${memoryId}`, data)
    },

    // 任务相关
    getTasks(userId = 'default_user', status = '', limit = 50) {
        return api.get(`/api/users/${userId}/tasks`, { params: { status, limit } })
    },

    getTask(taskId) {
        return api.get(`/api/tasks/${taskId}`)
    },

    createTask(data) {
        return api.post('/api/tasks', data)
    },

    updateTask(taskId, data) {
        return api.put(`/api/tasks/${taskId}`, data)
    },

    deleteTask(taskId) {
        return api.delete(`/api/tasks/${taskId}`)
    },

    // 提醒相关
    getReminders(userId = 'default_user', enabledOnly = false) {
        return api.get('/api/reminders', { params: { user_id: userId, enabled_only: enabledOnly } })
    },

    createReminder(data) {
        return api.post('/api/reminders', data)
    },

    updateReminder(reminderId, data) {
        return api.put(`/api/reminders/${reminderId}`, data)
    },

    deleteReminder(reminderId) {
        return api.delete(`/api/reminders/${reminderId}`)
    },

    confirmReminder(reminderId) {
        return api.post(`/api/reminders/${reminderId}/confirm`)
    },

    snoozeReminder(reminderId, minutes = 5) {
        return api.post(`/api/reminders/${reminderId}/snooze`, null, { params: { minutes } })
    },

    // 文档相关
    getDocuments(userId = 'default_user', limit = 50) {
        return api.get(`/api/users/${userId}/documents`, { params: { limit } })
    },

    getDocument(docId) {
        return api.get(`/api/documents/${docId}`)
    },

    uploadDocument(formData) {
        return api.post('/api/documents/upload', formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
        })
    },

    deleteDocument(docId) {
        return api.delete(`/api/documents/${docId}`)
    },

    // 课程表相关
    getSchedule(userId = 'default_user') {
        return api.get('/api/schedule', { params: { user_id: userId } })
    },

    updateSchedule(data) {
        return api.post('/api/schedule', data)
    },

    // 工具相关
    getTools(enabledOnly = true) {
        return api.get('/tools/list', { params: { enabled_only: enabledOnly } })
    },

    getToolHistory(userId = 'default_user', limit = 20) {
        return api.get('/tools/history', { params: { user_id: userId, limit } })
    },

    // 反馈相关
    submitFeedback(data) {
        return api.post('/api/feedback', data)
    },

    getFeedbackStats() {
        return api.get('/api/feedback/stats')
    },

    // 语音合成
    synthesizeVoice(text) {
        return api.post('/api/voice/synthesize', {
            text,
            person: 0, // 默认度小美
            speed: 5,
            pitch: 5,
            volume: 5,
            audio_format: 'mp3'
        })
    }
}
