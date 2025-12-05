# Cloudflare Pages 部署配置

## 基本设置

在 Cloudflare Dashboard 中配置:

1. **项目名称**: `xiaole-web` (或你喜欢的名称)
2. **Git 仓库**: `rockts/xiaole-ai`
3. **生产分支**: `main`
4. **构建设置**:
   - **Framework preset**: None (手动配置)
   - **Build command**: `cd frontend && npm install && npm run build`
   - **Build output directory**: `frontend/dist`
   - **Root directory**: `/` (项目根目录)

## 环境变量

在 Cloudflare Pages 设置中添加:

| 变量名 | 值 |
|--------|-----|
| `VITE_API_BASE` | `https://ai.leke.xyz` |
| `NODE_VERSION` | `20` |

## 部署后

- 前端访问: `https://xiaole-web.pages.dev` (或自定义域名)
- API 调用: `https://ai.leke.xyz/api/*`

## 自定义域名 (可选)

1. 在 Cloudflare Pages → Custom domains
2. 添加如 `app.leke.xyz` 或其他域名
3. 配置 DNS CNAME 记录

## 注意事项

- 确保 NAS 上的 Cloudflare Tunnel 正常运行
- 后端 CORS 已配置为允许所有来源
- SPA 路由通过 `_redirects` 文件处理
