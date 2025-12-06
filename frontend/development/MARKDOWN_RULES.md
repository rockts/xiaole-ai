# 开发中创建 Markdown 文档的规则

> 本文档说明在开发过程中如何创建和管理 Markdown 文档

## ⚠️ AI 重要规则

**AI 在创建文档时：**
- ✅ **默认创建到 xiaole-ai 文档库**（`../xiaole-ai/`）
- ✅ **使用 `./scripts/create-doc.sh` 脚本创建**
- ❌ **不要手动创建到当前仓库**（除非是项目特定文档）

详见 [AI 创建文档规则](#-ai-创建文档规则) 章节。

## 📋 文档分类

### 1. 项目文档（当前仓库）
- **位置**: 项目根目录或 `docs/` 目录
- **用途**: 项目特定的文档，如 README、部署说明、开发指南等
- **示例**: `README.md`, `CLOUDFLARE_PAGES.md`
- **提交**: 提交到当前仓库

### 2. 共享文档（xiaole-ai 文档库）
- **位置**: `../xiaole-ai/` 文档库
- **用途**: 跨仓库共享的文档，如组件文档、API 文档、开发规范等
- **目录结构**:
  - `frontend/setup/` - 前端设置相关
  - `frontend/development/` - 前端开发相关
  - `frontend/components/` - 组件文档
  - `frontend/api/` - API 文档
  - `backend/setup/` - 后端设置相关
  - `backend/development/` - 后端开发相关
- **提交**: 提交到 xiaole-ai 文档库

## 🚀 快速创建文档

### 使用 create-doc.sh 脚本

```bash
# 创建开发相关文档
./scripts/create-doc.sh development <文档名称>

# 创建设置相关文档
./scripts/create-doc.sh setup <文档名称>

# 创建组件文档（仅前端）
./scripts/create-doc.sh components <文档名称>

# 创建 API 文档（仅前端）
./scripts/create-doc.sh api <文档名称>
```

### 示例

```bash
# 创建前端优化方案文档
./scripts/create-doc.sh development optimization-plan

# 创建组件使用文档
./scripts/create-doc.sh components button-usage

# 创建 API 接口文档
./scripts/create-doc.sh api user-api
```

## 📝 文档命名规范

1. **使用小写字母和连字符**
   - ✅ 正确: `user-guide.md`, `api-reference.md`
   - ❌ 错误: `UserGuide.md`, `API_Reference.md`

2. **使用描述性名称**
   - ✅ 正确: `component-button-usage.md`
   - ❌ 错误: `button.md`, `doc1.md`

3. **避免特殊字符**
   - 不使用空格、中文、特殊符号

## 📄 文档结构模板

### 基础模板

```markdown
# 文档标题

> 创建时间: YYYY-MM-DD HH:MM
> 仓库: xiaole-web (frontend)
> 类型: development

## 概述

[文档概述，说明文档的目的和范围]

## 详细内容

[详细内容，可以包含多个章节]

### 子章节

[子章节内容]

## 相关链接

- [相关链接1]
- [相关链接2]

## 更新记录

- YYYY-MM-DD: 创建文档
```

### 组件文档模板

```markdown
# ComponentName 组件

> 创建时间: YYYY-MM-DD HH:MM
> 仓库: xiaole-web (frontend)
> 类型: components

## 概述

[组件功能描述]

## Props

| 属性名 | 类型   | 默认值 | 说明     |
| ------ | ------ | ------ | -------- |
| prop1  | String | -      | 属性说明 |

## 使用示例

\`\`\`vue
<ComponentName prop1="value" />
\`\`\`

## 相关链接

- [组件源码路径]
- [相关文档]

## 更新记录

- YYYY-MM-DD: 创建文档
```

## ✅ 创建文档检查清单

- [ ] 确定文档类型（项目文档 vs 共享文档）
- [ ] 选择合适的文档位置
- [ ] 使用 `create-doc.sh` 脚本创建（如适用）
- [ ] 遵循命名规范
- [ ] 填写完整的文档内容
- [ ] 添加相关链接
- [ ] 更新更新记录
- [ ] 提交到正确的仓库

## 🔍 文档位置判断

### 应该放在项目文档（当前仓库）的情况：
- 项目特定的配置说明
- 部署流程文档
- 项目开发规则
- 项目 README 和说明

### 应该放在共享文档（xiaole-ai）的情况：
- 组件使用文档
- API 接口文档
- 开发规范和最佳实践
- 跨仓库共享的技术文档

## 🤖 AI 创建文档规则

**重要：AI 在创建文档时必须遵循以下规则**

### 默认行为
- **默认创建到 xiaole-ai 文档库**：除非明确是项目特定文档，否则所有文档都应创建到 `../xiaole-ai/` 文档库
- **使用 create-doc.sh 脚本**：AI 应该使用 `./scripts/create-doc.sh` 脚本创建文档，而不是手动创建
- **自动判断文档类型**：根据文档内容自动判断文档类型（setup、development、components、api）

### 创建流程
1. **判断文档类型**
   - 组件文档 → `components` 类型
   - API 文档 → `api` 类型
   - 开发相关 → `development` 类型
   - 设置相关 → `setup` 类型

2. **使用脚本创建**
   ```bash
   ./scripts/create-doc.sh <类型> <文档名称>
   ```

3. **编辑文档内容**
   - 打开创建的文件
   - 填写完整的文档内容
   - 遵循文档结构模板

4. **提交到文档库**
   ```bash
   cd ../xiaole-ai
   git add <文档路径>
   git commit -m "docs(frontend/backend): 添加 <文档名称>"
   git push
   ```

### 例外情况（项目文档）
只有在以下情况下才创建到当前仓库：
- 项目特定的配置文件说明（如 `.cursorrules` 说明）
- 项目部署流程文档（如 `CLOUDFLARE_PAGES.md`）
- 项目开发规则文档（如项目特定的开发指南）
- 项目 README 文件

### AI 行为检查清单
- [ ] 判断文档是否为项目特定文档
- [ ] 如果不是项目文档，使用 `create-doc.sh` 创建到 xiaole-ai
- [ ] 如果是项目文档，创建到当前仓库的 `docs/` 目录
- [ ] 遵循命名规范
- [ ] 使用正确的文档模板
- [ ] 提交到正确的仓库

## 📌 注意事项

1. **不要创建重复文档**
   - 创建前先检查是否已有相关文档
   - 优先更新现有文档而非创建新文档

2. **保持文档更新**
   - 代码变更时同步更新相关文档
   - 在更新记录中记录变更内容

3. **文档质量**
   - 确保文档内容准确、完整
   - 使用清晰的标题和结构
   - 添加必要的代码示例

4. **提交规范**
   - 项目文档：提交到当前仓库
   - 共享文档：提交到 xiaole-ai 文档库
   - 提交信息格式：`docs(type): 添加/更新 文档名称`

## 🔗 相关资源

- [create-doc.sh 脚本](../../xiaole-web/scripts/create-doc.sh)
- [xiaole-ai 文档库](../..)
- [Markdown 语法指南](https://www.markdownguide.org/)

