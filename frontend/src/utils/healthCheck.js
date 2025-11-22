/**
 * 后端健康检查和自动重连
 */

let checkInterval = null
let isChecking = false
const CHECK_INTERVAL = 30000 // 30秒检查一次
const listeners = new Set()

export const healthCheck = {
  /**
   * 开始健康检查
   */
  start() {
    if (checkInterval) return

    console.log('🔍 启动后端健康检查...')

    // 立即检查一次
    this.check()

    // 定期检查
    checkInterval = setInterval(() => {
      this.check()
    }, CHECK_INTERVAL)
  },

  /**
   * 停止健康检查
   */
  stop() {
    if (checkInterval) {
      clearInterval(checkInterval)
      checkInterval = null
      console.log('⏹️ 停止后端健康检查')
    }
  },

  /**
   * 执行一次健康检查
   */
  async check() {
    if (isChecking) return
    isChecking = true

    try {
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), 5000)

      // 使用后端API路径而不是前端根路径
      const apiBase = import.meta.env.VITE_API_BASE || ''
      // 使用 /api/scheduler/status 作为健康检查端点，因为它被代理且返回JSON
      const response = await fetch(`${apiBase}/api/scheduler/status`, {
        method: 'GET',
        signal: controller.signal
      })

      clearTimeout(timeoutId)

      if (response.ok) {
        this.notifyListeners('online')
      } else {
        this.notifyListeners('offline')
      }
    } catch (error) {
      console.warn('后端连接失败:', error.message)
      this.notifyListeners('offline')
    } finally {
      isChecking = false
    }
  },

  /**
   * 添加状态监听器
   * @param {Function} callback - 回调函数，参数为状态 'online' | 'offline'
   */
  addListener(callback) {
    listeners.add(callback)
  },

  /**
   * 移除状态监听器
   */
  removeListener(callback) {
    listeners.delete(callback)
  },

  /**
   * 通知所有监听器
   */
  notifyListeners(status) {
    listeners.forEach(callback => {
      try {
        callback(status)
      } catch (error) {
        console.error('健康检查监听器错误:', error)
      }
    })
  }
}

// 页面可见时自动恢复检查
document.addEventListener('visibilitychange', () => {
  if (!document.hidden && checkInterval) {
    healthCheck.check()
  }
})
