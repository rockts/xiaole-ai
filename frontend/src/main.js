import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'
import './assets/styles/main.css'
import { healthCheck } from './utils/healthCheck'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)
app.mount('#app')

// 启动后端健康检查
healthCheck.start()

// 应用卸载时停止检查
window.addEventListener('beforeunload', () => {
  healthCheck.stop()
})
