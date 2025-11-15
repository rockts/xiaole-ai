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
