/**
 * Cloudflare Worker: 路由分发
 * - /api/* /uploads/* /ws/* /static/* /files/* → NAS 后端 (via Tunnel)
 * - 其他路径 → Cloudflare Pages 前端
 */

// 配置
const BACKEND_ORIGIN = 'https://backend.leke.xyz'  // Tunnel 域名，需要修改
const PAGES_ORIGIN = 'https://xiaole-ai.pages.dev' // Pages 域名

// 需要转发到后端的路径前缀
const BACKEND_PATHS = ['/api', '/uploads', '/ws', '/static', '/files']

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url)
    const pathname = url.pathname

    // 检查是否需要转发到后端
    const isBackendPath = BACKEND_PATHS.some(prefix => 
      pathname === prefix || pathname.startsWith(prefix + '/')
    )

    if (isBackendPath) {
      // 转发到后端
      const backendUrl = new URL(pathname + url.search, BACKEND_ORIGIN)
      
      // WebSocket 特殊处理
      if (pathname === '/ws' && request.headers.get('Upgrade') === 'websocket') {
        return fetch(backendUrl.toString(), {
          headers: request.headers,
          method: request.method,
        })
      }

      // 普通 HTTP 请求
      const newRequest = new Request(backendUrl.toString(), {
        method: request.method,
        headers: request.headers,
        body: request.body,
        redirect: 'follow',
      })

      const response = await fetch(newRequest)
      
      // 添加 CORS 头
      const newResponse = new Response(response.body, response)
      newResponse.headers.set('Access-Control-Allow-Origin', '*')
      
      return newResponse
    }

    // 转发到 Pages 前端
    const pagesUrl = new URL(pathname + url.search, PAGES_ORIGIN)
    const pagesRequest = new Request(pagesUrl.toString(), {
      method: request.method,
      headers: request.headers,
      body: request.body,
    })

    return fetch(pagesRequest)
  }
}
