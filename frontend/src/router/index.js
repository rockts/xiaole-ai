import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
    history: createWebHistory(),
    routes: [
        {
            path: '/',
            redirect: '/chat'
        },
        {
            path: '/chat/:sessionId?',
            name: 'Chat',
            component: () => import('@/views/ChatView.vue'),
            meta: { title: '对话' }
        },
        {
            path: '/share/:id',
            name: 'Share',
            component: () => import('@/views/ShareView.vue'),
            meta: { title: '分享' }
        },
        {
            path: '/memory',
            name: 'Memory',
            component: () => import('@/views/MemoryView.vue'),
            meta: { title: '记忆' }
        },
        {
            path: '/behavior',
            name: 'Behavior',
            component: () => import('@/views/BehaviorView.vue'),
            meta: { title: '行为分析' }
        },
        {
            path: '/reminders',
            name: 'Reminders',
            component: () => import('@/views/RemindersView.vue'),
            meta: { title: '提醒' }
        },
        {
            path: '/tasks',
            name: 'Tasks',
            component: () => import('@/views/TasksView.vue'),
            meta: { title: '任务' }
        },
        {
            path: '/task/:id',
            name: 'TaskDetail',
            component: () => import('@/views/TaskDetailView.vue'),
            meta: { title: '任务详情' }
        },
        {
            path: '/documents',
            name: 'Documents',
            component: () => import('@/views/DocumentsView.vue'),
            meta: { title: '文档' }
        },
        {
            path: '/documents/:id',
            name: 'DocumentDetail',
            component: () => import('@/views/DocumentDetailView.vue'),
            meta: { title: '文档详情' }
        },
        {
            path: '/tools',
            name: 'Tools',
            component: () => import('@/views/ToolsView.vue'),
            meta: { title: '工具' }
        },
        {
            path: '/faces',
            name: 'Faces',
            component: () => import('@/views/FacesView.vue'),
            meta: { title: '人脸管理' }
        },
        {
            path: '/settings',
            name: 'Settings',
            component: () => import('@/views/SettingsView.vue'),
            meta: { title: '设置' }
        }
    ]
})

router.beforeEach((to, from, next) => {
    document.title = to.meta.title ? `${to.meta.title} - 小乐 AI 管家` : '小乐 AI 管家'
    next()
})

export default router
