/**
 * chat-controls.js
 * 聊天控制模块：新对话、图片查看器等功能
 */

export function initChatControls() {
    // 新对话按钮绑定
    document.querySelectorAll('[data-action="new-chat"]').forEach((btn) => {
        btn.addEventListener('click', newChat);
    });

    // 图片查看器关闭绑定
    const imageViewerModal = document.getElementById('imageViewerModal');
    if (imageViewerModal) {
        imageViewerModal.addEventListener('click', (event) => {
            if (event.target.id === 'imageViewerModal' || event.target.classList.contains('image-viewer-close')) {
                closeImageViewer();
            }
        });
    }

    // ESC键关闭图片查看器
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            const modal = document.getElementById('imageViewerModal');
            if (modal && modal.classList.contains('active')) {
                closeImageViewer();
            }
        }
    });

    // 为动态添加的图片绑定点击事件（事件委托）
    document.addEventListener('click', (e) => {
        if (e.target.tagName === 'IMG' && e.target.closest('.message')) {
            const imgSrc = e.target.src;
            if (imgSrc) {
                openImageViewer(imgSrc);
            }
        }
    });

    // 空对话状态监听：无消息时让输入框在容器内居中
    setupChatEmptyObserver();
}

export function newChat() {
    window.currentSessionId = null;
    const chatContainer = document.getElementById('chatContainer');
    if (chatContainer) {
        chatContainer.innerHTML = '';
    }

    const sessionInfo = document.getElementById('sessionInfo');
    if (sessionInfo) {
        sessionInfo.style.display = 'none';
    }

    const messageInput = document.getElementById('messageInput');
    if (messageInput) {
        messageInput.focus();
    }

    // 清除编辑状态
    if (window.clearEditingState) {
        window.clearEditingState();
    }
}

export function openImageViewer(imageSrc) {
    const modal = document.getElementById('imageViewerModal');
    const img = document.getElementById('imageViewerImg');
    if (!modal || !img) return;

    img.src = imageSrc;
    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
}

export function closeImageViewer() {
    const modal = document.getElementById('imageViewerModal');
    if (!modal) return;

    modal.classList.remove('active');
    document.body.style.overflow = '';
}

// ===== 空对话检测与状态切换 =====
function setupChatEmptyObserver() {
    const chatEl = document.getElementById('chat');
    const container = document.getElementById('chatContainer');
    const editor = document.getElementById('messageInput');

    if (!chatEl || !container) {
        console.warn('⚠️ chat or chatContainer not found');
        return;
    }

    // 强制确保chat-empty类存在
    if (!chatEl.classList.contains('chat-empty')) {
        chatEl.classList.add('chat-empty');
    }

    const ensureWelcome = () => {
        let welcome = document.getElementById('chatWelcome');
        if (!welcome) {
            welcome = document.createElement('div');
            welcome.id = 'chatWelcome';
            welcome.className = 'chat-welcome';
            chatEl.appendChild(welcome);
        }
        welcome.innerHTML = getWelcomeHTML();
        welcome.style.display = 'block';
        return welcome;
    };

    const update = () => {
        const hasMessage = container.querySelector('.message') !== null;

        if (!hasMessage) {
            chatEl.classList.add('chat-empty');
        } else {
            chatEl.classList.remove('chat-empty');
        }

        // 动态占位文案：空态更友好
        if (editor) {
            editor.setAttribute(
                'data-placeholder',
                !hasMessage ? '我们先从哪里开始呢？' : '发送消息或输入 / 选择技能'
            );
        }

        // 空态欢迎语
        const welcome = document.getElementById('chatWelcome');
        if (!hasMessage) {
            ensureWelcome();
        } else if (welcome) {
            welcome.style.display = 'none';
        }
    };

    // 立即执行一次
    setTimeout(() => {
        update();
        ensureWelcome();
    }, 100);

    // 监听子树变化（消息添加/清空）
    const observer = new MutationObserver(() => update());
    observer.observe(container, { childList: true, subtree: true });

    // 视口尺寸变化时也刷新一次（避免布局切换时错位）
    window.addEventListener('resize', update);
}

function getWelcomeHTML() {
    const now = new Date();
    const hour = now.getHours();
    let greet = '你好';
    if (hour >= 5 && hour < 11) greet = '早上好';
    else if (hour >= 11 && hour < 14) greet = '中午好';
    else if (hour >= 14 && hour < 18) greet = '下午好';
    else greet = '晚上好';

    const nickname = localStorage.getItem('userNickname')
        || localStorage.getItem('nickname')
        || localStorage.getItem('displayName')
        || '';

    const nameText = nickname ? `，${sanitize(nickname)}` : '';

    return `
        <div class="welcome-title">${greet}${nameText}</div>
        <div class="welcome-subtitle">准备好开始了吗？</div>
    `;
}

function sanitize(str) {
    return String(str).replace(/[&<>"']/g, (c) => ({
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#39;'
    })[c]);
}
