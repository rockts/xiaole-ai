import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
    plugins: [vue()],
    resolve: {
        alias: {
            '@': path.resolve(__dirname, './src')
        }
    },
    server: {
        host: '0.0.0.0', // 允许外部访问
        port: 3000,
        proxy: {
            '/api': {
                target: 'http://localhost:8000',
                changeOrigin: true
            },
            '/ws': {
                target: 'ws://localhost:8000',
                ws: true
            },
            '/sessions': {
                target: 'http://localhost:8000',
                changeOrigin: true
            },
            '/session': {
                target: 'http://localhost:8000',
                changeOrigin: true
            },
            // 只代理 POST 请求到后端 /chat API
            '/chat': {
                target: 'http://localhost:8000',
                changeOrigin: true,
                bypass: function (req, res, options) {
                    // 如果是 GET 请求，返回给前端路由处理
                    if (req.method === 'GET') {
                        return req.url;
                    }
                    // POST 请求继续代理到后端
                }
            },
            '/uploads': {
                target: 'http://localhost:8000',
                changeOrigin: true
            },
            // 仅代理具体的 memory API 路径，避免拦截前端路由 /memory
            '/memory/stats': {
                target: 'http://localhost:8000',
                changeOrigin: true
            },
            '/memory/recent': {
                target: 'http://localhost:8000',
                changeOrigin: true
            },
            '/memory/search': {
                target: 'http://localhost:8000',
                changeOrigin: true
            },
            '/memory/semantic': {
                target: 'http://localhost:8000',
                changeOrigin: true
            },
            // 删除/更新等 /memory/{id} 走后端；带斜杠不影响前端 /memory 路由
            '/memory/': {
                target: 'http://localhost:8000',
                changeOrigin: true
            },
            '/tools': {
                target: 'http://localhost:8000',
                changeOrigin: true
            }
        }
    },
    build: {
        outDir: '../static/dist',
        emptyOutDir: true
    }
})
