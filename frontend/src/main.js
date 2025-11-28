import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'
import './assets/styles/main.css'
import 'highlight.js/styles/github-dark.css'
import { healthCheck } from './utils/healthCheck'

// 控制台调试提示
console.log(
  '%c小乐 AI 管家 %cv0.9.0',
  'color: #667eea; font-size: 20px; font-weight: bold;',
  'color: #999; font-size: 14px;'
);
console.log(
  '%c💡 调试快捷键: Ctrl+Shift+D 清除认证信息',
  'color: #10b981; font-size: 12px;'
);

const app = createApp(App)
const pinia = createPinia()

// 全局错误处理
app.config.errorHandler = (err, instance, info) => {
  console.error('❌ Vue Error:', err);
  console.error('📍 Error Info:', info);
  console.error('🔍 Component:', instance);

  // 如果是路由加载错误,尝试重新加载
  if (err.message && err.message.includes('Failed to fetch dynamically imported module')) {
    console.warn('⚠️ 动态导入失败,3秒后重新加载页面...');
    setTimeout(() => {
      window.location.reload();
    }, 3000);
  }
};

app.use(pinia)
app.use(router)
app.mount('#app')

// 启动后端健康检查
healthCheck.start()

// 应用卸载时停止检查
window.addEventListener('beforeunload', () => {
  healthCheck.stop()
})

