import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

export const useAuthStore = defineStore('auth', () => {
    const token = ref(localStorage.getItem('token') || null)
    const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))
    const loading = ref(false)
    const error = ref(null)

    const isAuthenticated = computed(() => !!token.value)

    const login = async (username, password) => {
        loading.value = true
        error.value = null
        try {
            const formData = new FormData()
            formData.append('username', username)
            formData.append('password', password)

            // 使用 axios 直接请求，避免循环依赖 api.js
            const API_BASE_URL = import.meta.env.VITE_API_BASE || ''
            const response = await axios.post(`${API_BASE_URL}/api/token`, formData)

            const { access_token } = response.data
            token.value = access_token
            localStorage.setItem('token', access_token)

            // 简单设置用户信息并持久化
            user.value = { username }
            localStorage.setItem('user', JSON.stringify(user.value))

            return true
        } catch (err) {
            console.error('Login failed:', err)
            error.value = err.response?.data?.detail || '登录失败，请检查用户名和密码'
            return false
        } finally {
            loading.value = false
        }
    }

    const logout = () => {
        token.value = null
        user.value = null
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        // 可以选择重定向到登录页，通常在组件或路由守卫中处理
    }

    return {
        token,
        user,
        loading,
        error,
        isAuthenticated,
        login,
        logout
    }
})
