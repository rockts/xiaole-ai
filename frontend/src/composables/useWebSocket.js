import { ref, onUnmounted } from 'vue'

let ws = null
const connected = ref(false)
const listeners = new Map()
let heartbeatTimer = null

export function useWebSocket() {
    const startHeartbeat = () => {
        if (heartbeatTimer) clearInterval(heartbeatTimer)
        heartbeatTimer = setInterval(() => {
            if (ws && ws.readyState === WebSocket.OPEN) {
                ws.send("ping")
            }
        }, 30000)
    }

    const connect = () => {
        if (ws && ws.readyState === WebSocket.OPEN) {
            return
        }

        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
        const wsUrl = `${protocol}//${window.location.host}/ws`

        ws = new WebSocket(wsUrl)

        ws.onopen = () => {
            console.log('WebSocket connected')
            connected.value = true
            startHeartbeat()
        }

        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data)
                if (data.type === 'pong') return // Ignore pong

                console.log('WebSocket message:', data)

                // 触发所有监听器
                listeners.forEach((callback) => {
                    callback(data)
                })
            } catch (error) {
                console.error('Failed to parse WebSocket message:', error)
            }
        }

        ws.onerror = (error) => {
            console.error('WebSocket error:', error)
        }

        ws.onclose = () => {
            console.log('WebSocket disconnected')
            connected.value = false
            if (heartbeatTimer) clearInterval(heartbeatTimer)

            // 5秒后重连
            setTimeout(() => {
                connect()
            }, 5000)
        }
    }

    const disconnect = () => {
        if (ws) {
            ws.close()
            ws = null
        }
    }

    const send = (data) => {
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify(data))
        }
    }

    const on = (callback) => {
        const id = Symbol()
        listeners.set(id, callback)
        return () => listeners.delete(id)
    }

    onUnmounted(() => {
        // 不要在组件卸载时断开连接，保持全局连接
    })

    return {
        connected,
        connect,
        disconnect,
        send,
        on
    }
}
