import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

// API基础URL配置
// 优先使用环境变量，否则使用空字符串（通过vite代理访问）
const API_BASE_URL = import.meta.env.VITE_API_BASE || ''

const api = axios.create({
    baseURL: API_BASE_URL,
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
        // 注入 Token
        const authStore = useAuthStore()
        if (authStore.token) {
            config.headers.Authorization = `Bearer ${authStore.token}`
        }

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

        // 处理 401 未授权
        if (error.response && error.response.status === 401) {
            const authStore = useAuthStore()
            authStore.logout()
            // 可以在这里触发重定向，或者由路由守卫处理
            if (window.location.pathname !== '/login') {
                window.location.href = '/login'
            }
            return Promise.reject(error)
        }

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
        return api.get('/api/sessions', { params: { all_sessions: allSessions } })
    },

    getSession(sessionId, limit = 200) {
        return api.get(`/api/session/${sessionId}`, { params: { limit } })
    },

    deleteSession(sessionId) {
        return api.delete(`/api/chat/sessions/${sessionId}`)
    },

    updateSession(sessionId, data) {
        return api.patch(`/api/chat/sessions/${sessionId}`, data)
    },

    deleteMessage(messageId) {
        return api.delete(`/api/messages/${messageId}`)
    },

    sendMessage(data) {
        // 后端使用查询参数而不是 POST body
        const params = new URLSearchParams()
        // 即使是空字符串也要发送 prompt 参数
        params.append('prompt', data.prompt || '')

        if (data.session_id) params.append('session_id', data.session_id)
        if (data.user_id) params.append('user_id', data.user_id)
        if (data.response_style) params.append('response_style', data.response_style)
        if (data.image_path) params.append('image_path', data.image_path)

        // 增加超时时间到 120 秒，并禁用自动重试
        return api.post(`/api/chat?${params.toString()}`, null, {
            timeout: 120000,
            retryCount: MAX_RETRIES // 设置为最大重试次数，防止拦截器重试
        })
    },

    // 流式聊天（SSE 兼容，切片流）
    async streamChat(data, { onStart, onDelta, onEnd, signal } = {}) {
        // 使用 fetch 以支持 ReadableStream
        const params = new URLSearchParams()
        params.append('prompt', data.prompt || '')
        if (data.session_id) params.append('session_id', data.session_id)
        if (data.user_id) params.append('user_id', data.user_id)
        if (data.response_style) params.append('response_style', data.response_style)
        if (data.image_path) params.append('image_path', data.image_path)

        const authStore = useAuthStore()
        const headers = { 'Accept': 'text/event-stream' }
        if (authStore.token) headers['Authorization'] = `Bearer ${authStore.token}`

        const url = `${API_BASE_URL}/api/chat/stream?${params.toString()}`
        const res = await fetch(url, { method: 'POST', headers, signal })
        if (!res.ok || !res.body) {
            const text = await res.text().catch(() => '')
            throw new Error(text || `HTTP ${res.status}`)
        }

        const reader = res.body.getReader()
        const decoder = new TextDecoder('utf-8')
        let buffer = ''

        // 先通知开始
        if (typeof onStart === 'function') onStart()

        try {
            while (true) {
                const { value, done } = await reader.read()
                if (done) break
                buffer += decoder.decode(value, { stream: true })

                // SSE 按空行分隔事件
                let idx
                while ((idx = buffer.indexOf('\n\n')) !== -1) {
                    const raw = buffer.slice(0, idx).trim()
                    buffer = buffer.slice(idx + 2)
                    if (!raw) continue
                    // 仅处理以 data: 开头的行
                    const lines = raw.split('\n')
                    for (const line of lines) {
                        const prefix = 'data: '
                        if (line.startsWith(prefix)) {
                            try {
                                const payload = JSON.parse(line.slice(prefix.length))
                                if (payload.type === 'delta' && typeof onDelta === 'function') {
                                    onDelta(payload.data || '')
                                } else if (payload.type === 'start') {
                                    if (typeof onStart === 'function') onStart(payload)
                                } else if (payload.type === 'end') {
                                    if (typeof onEnd === 'function') onEnd(payload)
                                }
                            } catch (_) {
                                // 忽略解析错误
                            }
                        }
                    }
                }
            }
            // 处理残留缓冲
            const rest = buffer.trim()
            if (rest) {
                const lines = rest.split('\n')
                for (const line of lines) {
                    const prefix = 'data: '
                    if (line.startsWith(prefix)) {
                        try {
                            const payload = JSON.parse(line.slice(prefix.length))
                            if (payload.type === 'delta' && typeof onDelta === 'function') {
                                onDelta(payload.data || '')
                            } else if (payload.type === 'end') {
                                if (typeof onEnd === 'function') onEnd(payload)
                            }
                        } catch (_) { }
                    }
                }
            }
        } finally {
            try { reader.releaseLock() } catch (_) { }
        }
    },

    uploadImage(formData) {
        return api.post('/api/vision/upload', formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
        })
    },

    // 记忆相关
    getMemoryStats() {
        return api.get('/api/memory/stats')
    },

    getRecentMemories(hours = 24, limit = 20, tag = null) {
        const params = { hours, limit }
        if (tag) params.tag = tag
        return api.get('/api/memory/recent', { params })
    },

    searchMemories(keywords) {
        // ...existing code...
        return api.get('/api/memory/search', { params: { keywords } })
    },

    semanticSearch(query) {
        return api.get('/api/memory/semantic', { params: { query } })
    },

    deleteMemory(memoryId) {
        return api.delete(`/api/memory/${memoryId}`)
    },

    updateMemory(memoryId, data) {
        return api.put(`/api/memory/${memoryId}`, data)
    },

    // 任务相关
    getTasks(status = '', limit = 50) {
        const params = { limit };
        if (status) params.status = status;
        return api.get('/api/tasks', { params });
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
    getReminders(enabledOnly = false) {
        return api.get('/api/reminders', { params: { enabled_only: enabledOnly } })
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

    // 行为分析相关
    getBehaviorAnalytics(days = 30) {
        return api.get('/api/analytics/behavior', { params: { days } })
    },

    // 文档相关
    getDocuments(limit = 50) {
        // 从auth store获取登录用户名,如果没有使用admin
        const authStore = useAuthStore();
        console.log('🔍 authStore.user:', authStore.user);
        console.log('🔍 authStore.token:', authStore.token ? '有token' : '无token');
        const username = authStore.user?.username || 'admin';
        console.log('🔍 getDocuments - 使用登录用户名:', username);
        const url = `/api/documents/users/${username}`;
        console.log('🔍 请求URL:', url);
        return api.get(url, { params: { limit } })
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

    // 工具相关
    getTools(enabledOnly = true) {
        return api.get('/api/tools/list', { params: { enabled_only: enabledOnly } })
    },

    getToolHistory(userId = 'default_user', limit = 20) {
        return api.get('/api/tools/history', { params: { user_id: userId, limit } })
    },

    // 反馈相关
    submitFeedback(data) {
        return api.post('/api/feedback', data)
    },

    getFeedbackStats() {
        return api.get('/api/feedback/stats')
    },

    // 语音合成
    synthesizeVoice(text, options = {}) {
        return api.post('/api/voice/synthesize', {
            text,
            person: options.person !== undefined ? options.person : 0,
            speed: options.speed !== undefined ? options.speed : 5,
            pitch: options.pitch !== undefined ? options.pitch : 5,
            volume: options.volume !== undefined ? options.volume : 5,
            audio_format: options.audio_format || 'mp3'
        })
    },

    // 语音识别（上传音频文件：wav/pcm/m4a/amr）
    recognizeVoice(fileOrBlob, filename = 'voice.wav') {
        const formData = new FormData()
        const file = fileOrBlob instanceof File ? fileOrBlob : new File([fileOrBlob], filename, { type: 'audio/wav' })
        formData.append('file', file)
        return api.post('/api/voice/recognize', formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
            timeout: 60000
        })
    }
}
