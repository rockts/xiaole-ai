import {
    initTheme,
    applyInitialSettings,
    toggleTheme,
    updateThemePreference,
    toggleKeyboardShortcuts,
    toggleShortcutHints,
    updateResponseStyle,
    toggleProactiveQA,
    toggleReminderNotifications,
    resetSettings
} from './modules/theme.js';
import {
    initNavigation,
    toggleSidebar,
    toggleSidebarCollapse,
    switchTab
} from './modules/navigation.js';
import {
    initComposer,
    sendMessageFromDiv,
    sendHomeMessage,
    triggerImageUpload,
    handleImageUpload,
    editMessage,
    clearEditingState,
    showImagePreviewInInput,
    removeImagePreview
} from './modules/composer.js';
import {
    initChatControls,
    newChat,
    openImageViewer,
    closeImageViewer
} from './modules/chat-controls.js';

// expose functions globally for existing inline handlers until HTML is refactored
window.toggleTheme = toggleTheme;
window.updateThemePreference = updateThemePreference;
window.toggleKeyboardShortcuts = toggleKeyboardShortcuts;
window.toggleShortcutHints = toggleShortcutHints;
window.updateResponseStyle = updateResponseStyle;
window.toggleProactiveQA = toggleProactiveQA;
window.toggleReminderNotifications = toggleReminderNotifications;
window.resetSettings = resetSettings;
window.toggleSidebar = toggleSidebar;
window.toggleSidebarCollapse = toggleSidebarCollapse;
window.switchTab = switchTab;
window.sendMessageFromDiv = sendMessageFromDiv;
window.sendHomeMessage = sendHomeMessage;
window.triggerImageUpload = triggerImageUpload;
window.handleImageUpload = handleImageUpload;
window.editMessage = editMessage;
window.clearEditingState = clearEditingState;
window.showImagePreviewInInput = showImagePreviewInInput;
window.removeImagePreview = removeImagePreview;
window.newChat = newChat;
window.openImageViewer = openImageViewer;
window.closeImageViewer = closeImageViewer;

document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    applyInitialSettings();
    initNavigation();
    initComposer();
    initChatControls();
});

// Future modules can register their own event delegates here as they are extracted.
