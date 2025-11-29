import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/services/api'

export const useMemoryStore = defineStore('memory', () => {
    const stats = ref({})
    const memories = ref([])
    const loading = ref(false)
    const memoriesLoading = ref(false)

    const loadStats = async () => {
        try {
            loading.value = true
            stats.value = await api.getMemoryStats()
        } catch (error) {
            console.error('Failed to load memory stats:', error)
        } finally {
            loading.value = false
        }
    }

    // ...existing code...
    const loadRecentMemories = async (hours = 720, limit = 100, tag = null) => {
        try {
            memoriesLoading.value = true
            const data = await api.getRecentMemories(hours, limit, tag)
            console.log('[Memory Store] loadRecentMemories response:', data)

            // Handle different response formats
            if (Array.isArray(data)) {
                memories.value = data
            } else if (data && Array.isArray(data.memory)) {
                memories.value = data.memory
            } else if (data && Array.isArray(data.memories)) {
                memories.value = data.memories
            } else {
                console.warn('[Memory Store] Unexpected response format:', data)
                memories.value = []
            }

            console.log('[Memory Store] memories count:', memories.value.length)
        } catch (error) {
            console.error('Failed to load memories:', error)
            memories.value = []
        } finally {
            memoriesLoading.value = false
        }
    }

    const searchMemories = async (query) => {
        try {
            memoriesLoading.value = true
            const data = await api.searchMemories(query)
            // 后端返回 memories 字段
            memories.value = data.memories || []
        } catch (error) {
            console.error('Failed to search memories:', error)
        } finally {
            memoriesLoading.value = false
        }
    }

    const semanticSearch = async (query) => {
        try {
            memoriesLoading.value = true
            const data = await api.semanticSearch(query)
            // 后端返回 memories 字段
            memories.value = data.memories || []
        } catch (error) {
            console.error('Failed to semantic search:', error)
        } finally {
            memoriesLoading.value = false
        }
    }

    const deleteMemory = async (memoryId) => {
        try {
            await api.deleteMemory(memoryId)
            memories.value = memories.value.filter(m => m.id !== memoryId)
            await loadStats()
        } catch (error) {
            console.error('Failed to delete memory:', error)
        }
    }

    const updateMemory = async (memoryId, content, tag) => {
        try {
            await api.updateMemory(memoryId, { content, tag })
            const memory = memories.value.find(m => m.id === memoryId)
            if (memory) {
                memory.content = content
                memory.tag = tag
            }
            await loadStats()
            return true
        } catch (error) {
            console.error('Failed to update memory:', error)
            return false
        }
    }

    return {
        stats,
        memories,
        loading,
        memoriesLoading,
        loadStats,
        loadRecentMemories,
        searchMemories,
        semanticSearch,
        deleteMemory,
        updateMemory
    }
})
