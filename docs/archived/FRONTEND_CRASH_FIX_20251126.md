# 前端崩溃修复报告 (2025-11-26)

## 问题诊断
用户报告“前端频繁崩溃”。经代码分析，在 `frontend/src/components/common/ReminderNotification.vue` 中发现了一个严重的资源泄漏问题。

### 根本原因：AudioContext 泄漏
`ReminderNotification` 组件负责在提醒触发时播放声音。它使用了一个备用机制 (`playFallbackSound`)，通过 Web Audio API 生成“叮咚”声。

`playFallbackSound` 的实现存在以下问题：
1. 每次调用时都会创建一个 **新的** `AudioContext`。
2. 这些上下文 **从未被关闭**。
3. `playSound` 函数在提醒激活期间会循环调用 `playFallbackSound`（每 5 秒一次）。

浏览器通常限制活动的 `AudioContext` 实例数量（通常为 6 个）。一旦达到此限制，浏览器标签页可能会崩溃、卡死或完全停止播放音频。

## 修复实施
我对 `frontend/src/components/common/ReminderNotification.vue` 进行了重构：
1.  **使用共享 AudioContext**：组件现在维护一个单例 `sharedAudioCtx`?### 根本原因：AudioContext 泄漏
`ReminderNotification\生命周期管理**：上下文按需创建，并仅在组件卸载时关闭。
3.  **资源清理**：添加了显式断开振荡器（Oscillator）和增益（Gain）节点的代码，防止上下文内部的内存泄漏。

## 验证
- `new AudioContext()` 的无限创建循环已停止。
- 音频节点在使用后被正确断开。
- 组件销毁时（例如注销时）上下文会被关闭。

## 建议
- 继续监控应用程序是否有进一步的崩溃。
- 如果崩溃仍然存在，建议优化 `ChatView.vue` 的图片处理（大 Base64 图片）或 `ReminderNotification` 的语音合成（同样使用 Base64 音频）。
