# 小乐开发者文档站

这个仓库是小乐的开发者/文档站，所有文档最终会发布到 `docs.leke.xyz`。前后端项目的文档也集中放在这里统一维护。

## 仓库内容
- `architecture/` 系统架构与部署设计
- `backend/` 后端相关文档
- `frontend/` 前端相关文档
- `product/` 产品/测试/用户向文档
- `dev/` 开发运维与已知问题（含 `issues/`）
- `roadmap/` 规划与历史存档（含 `archived/`）
- `INDEX.md`, `QUICK_REFERENCE.md` 导航与速查
- `DOCS_README.md` 旧版项目说明（归档）
- `architecture.png` 架构图

## 托管方案（Cloudflare Pages）
1) Pages 项目指向本仓库，框架选择 None。构建命令留空（或 `echo skip`），输出目录使用仓库根目录 `/`。
2) 生产分支使用当前默认分支（现为 `develop`）。如需预览，可在 Pages 启用其它分支预览。
3) 绑定自定义域 `docs.leke.xyz`，在 Cloudflare 添加 CNAME 指向 Pages 默认域，并开启自动 HTTPS。

## 本地预览
```bash
cd /Users/rockts/Dev/xiaole-ai
python3 -m http.server 8000
# 浏览器访问 http://localhost:8000
```

## 文档维护
- 按类别放入对应目录；前端/后端项目的 docs 也放这里。
- 更新导航文件：`INDEX.md`、`QUICK_REFERENCE.md`。
- 大篇幅说明可放子目录的 README，或归档到 `DOCS_README.md`。

## 历史说明
原有功能/更新/部署等长篇说明已归档至 `DOCS_README.md`，此处仅保留站点用途与导航。
