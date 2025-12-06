# docs 目录说明

> ⚠️ **重要**：此目录仅保留必要的文件，详细文档已移至 [xiaole-ai](https://github.com/rockts/xiaole-ai) 仓库

## 当前保留的文件

- `DEV_CONTEXT.md` - 开发上下文（符号链接，指向 iCloud，不提交到代码库）
- `DEV_CONTEXT.md.example` - 模板文件（可选）

## 文档管理规则

### 保留在当前仓库

- ✅ `README.md`（项目根目录）- 项目说明
- ✅ `xiaole-agent-context/*` - Agent 规则（必须保留）
- ✅ `docs/DEV_CONTEXT.md` - 开发上下文（iCloud 同步）

### 移到 docs 库（xiaole-ai）

- 📚 详细使用指南
- 📚 设置教程
- 📚 开发文档
- 📚 测试文档
- 📚 架构设计

## 查看详细文档

详细文档请访问：[xiaole-ai 仓库](https://github.com/rockts/xiaole-ai)

## 迁移文档

如需迁移文档到 docs 库，使用脚本：

```bash
export DOCS_REPO_PATH=/path/to/xiaole-ai
./scripts/move-docs-to-repo.sh
```
