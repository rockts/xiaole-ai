# 前端性能优化指南 (v0.6.0)

## 概述

本文档描述了v0.6.0版本前端性能优化的实现方案和使用方法。

## 优化内容

### 1. 数据缓存系统

**问题**: 每次切换标签页都重新请求数据，造成大量冗余请求

**解决方案**: 实现客户端缓存机制

```javascript
// 使用缓存
const cached = DataCache.get('sessions');
if (cached) {
    // 使用缓存数据
    renderSessions(cached);
    PerformanceMonitor.recordCacheHit();
} else {
    // 请求新数据
    const data = await APIController.fetch('/api/sessions');
    DataCache.set('sessions', data);
    PerformanceMonitor.recordCacheMiss();
}
```

**特性**:
- TTL: 60秒（可配置）
- 支持5种数据类型: sessions, memory, analytics, tools, reminders
- 自动过期检查
- 手动清除缓存

**API**:
```javascript
// 检查缓存是否有效
DataCache.isValid('sessions') // => true/false

// 获取缓存（自动检查有效性）
const data = DataCache.get('sessions') // => data or null

// 更新缓存
DataCache.set('sessions', data)

// 清除缓存
DataCache.clear('sessions') // 清除指定缓存
DataCache.clear() // 清除所有缓存

// 查看缓存状态
console.log(DataCache.getStats())
```

### 2. API并发控制

**问题**: 多个API同时请求，可能造成服务器压力和浏览器卡顿

**解决方案**: 限制同时请求数量

```javascript
// 使用并发控制的fetch
const response = await APIController.fetch(url, options);
```

**特性**:
- 最大并发数: 3（可配置）
- 自动队列管理
- 等待机制

**API**:
```javascript
// 获取当前状态
const status = APIController.getStatus()
// {
//   active: 2,      // 当前活跃请求数
//   max: 3,         // 最大并发数
//   available: 1    // 可用插槽
// }
```

### 3. 超时优化

**问题**: 60秒超时过长，用户等待时间太久

**解决方案**: 缩短超时至30秒

```javascript
// 旧代码（60秒）
const timeoutId = setTimeout(() => controller.abort(), 60000);

// 新代码（30秒）
const timeoutId = setTimeout(() => controller.abort(), 30000);
```

**改进点**:
- 超时时间: 60秒 → 30秒
- 超时提示更友好
- 建议用户简化问题

### 4. 懒加载机制

**问题**: 所有标签页数据一次性加载，初始加载慢

**解决方案**: 按需加载数据

```javascript
function switchTab(tabName) {
    // 只在缓存无效时加载
    if (!DataCache.isValid(tabName)) {
        loadTabData(tabName);
        LazyLoader.markLoaded(tabName);
    }
}
```

**特性**:
- 首次访问才加载
- 缓存后不重复加载
- 标签页切换更快

**API**:
```javascript
// 检查是否已加载
LazyLoader.isLoaded('sessions') // => true/false

// 标记已加载
LazyLoader.markLoaded('sessions')

// 重置加载状态
LazyLoader.reset('sessions') // 重置指定标签页
LazyLoader.reset() // 重置所有标签页
```

### 5. 防抖和节流

**问题**: 频繁操作触发大量事件

**解决方案**: 使用防抖和节流函数

```javascript
// 防抖：延迟执行，只执行最后一次
const debouncedSearch = debounce((query) => {
    search(query);
}, 300);

// 节流：限制执行频率
const throttledScroll = throttle(() => {
    handleScroll();
}, 1000);
```

**使用场景**:
- 防抖: 搜索输入、窗口resize
- 节流: 滚动事件、鼠标移动

### 6. 性能监控

**问题**: 无法量化优化效果

**解决方案**: 内置性能监控

```javascript
// 查看性能统计
console.log(PerformanceMonitor.getStats())
// {
//   apiCalls: 45,
//   cacheHits: 32,
//   cacheMisses: 13,
//   errors: 0,
//   cacheHitRate: '71.1%'
// }
```

**监控指标**:
- API调用次数
- 缓存命中率
- 错误次数

## 集成方式

### 1. 引入性能模块

在HTML中添加：

```html
<!-- 在其他脚本之前引入 -->
<script src="/static/performance.js"></script>
```

### 2. 修改现有代码

#### 原代码：
```javascript
async function loadSessions() {
    const response = await fetch('/api/sessions');
    const data = await response.json();
    renderSessions(data);
}

function switchTab(tabName) {
    if (tabName === 'sessions') loadSessions();
}
```

#### 优化后：
```javascript
async function loadSessions() {
    // 检查缓存
    const cached = DataCache.get('sessions');
    if (cached) {
        renderSessions(cached);
        PerformanceMonitor.recordCacheHit();
        return;
    }
    
    // 使用并发控制
    PerformanceMonitor.recordAPICall();
    const response = await APIController.fetch('/api/sessions');
    const data = await response.json();
    
    // 更新缓存
    DataCache.set('sessions', data);
    PerformanceMonitor.recordCacheMiss();
    renderSessions(data);
}

function switchTab(tabName) {
    // 懒加载+缓存检查
    if (tabName === 'sessions') {
        if (!DataCache.isValid('sessions')) {
            loadSessions();
        }
    }
}
```

## 性能提升预期

| 指标           | 优化前     | 优化后        | 提升   |
| -------------- | ---------- | ------------- | ------ |
| 标签页切换速度 | 500-2000ms | <100ms        | 80-95% |
| 首屏加载时间   | 3-5秒      | 1-2秒         | 40-60% |
| API请求数      | 高频重复   | 缓存后减少70% | 70%    |
| 超时等待       | 60秒       | 30秒          | 50%    |
| 内存占用       | 无控制     | <100MB        | 稳定   |

## 调试工具

在浏览器控制台：

```javascript
// 查看完整性能报告
debugPerformance()

// 清除所有缓存（测试用）
DataCache.clear()

// 重置性能统计
PerformanceMonitor.reset()

// 查看缓存详情
console.table(DataCache.getStats())
```

## 注意事项

1. **缓存时效性**: TTL设为60秒，数据可能有延迟
2. **手动刷新**: 重要操作后应清除缓存
3. **并发限制**: 最多3个并发请求，大量请求会排队
4. **浏览器兼容**: 需要现代浏览器（支持Promise、async/await）

## 未来改进

- [ ] 实现虚拟滚动（长列表优化）
- [ ] 添加Service Worker（离线支持）
- [ ] 实现WebSocket推送（减少轮询）
- [ ] 添加图片懒加载
- [ ] 实现代码分割（按需加载）

## 相关文档

- [v0.6.0开发计划](v0.6.0_PLAN.md)
- [主动问答优化](PROACTIVE_QA_FIX.md)
- [数据库优化](../db_migrations/002_add_indexes_v0.6.0.sql)
