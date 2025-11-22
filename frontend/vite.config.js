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
        host: '0.0.0.0',
        port: 3000,
        proxy: {
            '/api': {
                target: 'http://127.0.0.1:8000',
                changeOrigin: true
            },
            '/ws': {
                target: 'ws://127.0.0.1:8000',
                ws: true
            },
            '/sessions': {
                target: 'http://127.0.0.1:8000',
                changeOrigin: true
            },
            '/session': {
                target: 'http://127.0.0.1:8000',
                changeOrigin: true
            },
            '/chat': {
                target: 'http://127.0.0.1:8000',
                changeOrigin: true,
                bypass: function (req) {
                    if (req.method === 'GET') {
                        return req.url;
                    }
                }
            },
            '/uploads': {
                target: 'http://127.0.0.1:8000',
                changeOrigin: true
            },
            '/static': {
                target: 'http://127.0.0.1:8000',
                changeOrigin: true
            },
            '/memory/stats': {
                target: 'http://127.0.0.1:8000',
                changeOrigin: true
            },
            '/memory/recent': {
                target: 'http://127.0.0.1:8000',
                changeOrigin: true
            },
            '/memory/search': {
                target: 'http://127.0.0.1:8000',
                changeOrigin: true
            },
            '/memory/semantic': {
                target: 'http://127.0.0.1:8000',
                changeOrigin: true
            },
            '/memory/': {
                target: 'http://127.0.0.1:8000',
                changeOrigin: true
            },
            '/tools': {
                target: 'http://127.0.0.1:8000',
                changeOrigin: true
            }
        }
    },
    build: {
        outDir: '../static/dist',
        emptyOutDir: true
    }
})
