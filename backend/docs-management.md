# 文档管理规则

## 文档分类

### 保留在当前仓库的文档

以下文档**必须保留**在当前仓库（xiaole-backend）：

1. **README.md**（项目根目录）
   - 项目快速开始指南
   - API 端点说明
   - 部署信息

2. **xiaole-agent-context/**（Agent 规则目录）
   - `persona.md` - Agent 角色定义
   - `dev-rules.md` - 开发规则
   - `project-overview.md` - 项目概览
   - `tools.md` - 工具说明
   - `task-basic-rules.md` - 任务规则
   - 这些文件是 Agent 自动读取的上下文，必须保留

3. **docs/DEV_CONTEXT.md**（符号链接）
   - 开发上下文文件（iCloud 同步）
   - 符号链接，指向 iCloud 文件

4. **docs/DEV_CONTEXT.md.example**（可选）
   - 模板文件，可以保留或移到 docs 库

### 移到 docs 库的文档

根据 [xiaole-ai 仓库](https://github.com/rockts/xiaole-ai) 的结构：

**后端文档** → `xiaole-ai/backend/`（已存在的目录）

1. **详细使用指南**
   - `docs/USAGE.md` → `backend/setup/usage.md`
   - `docs/MULTI-REPO-SETUP.md` → `backend/setup/multi-repo-setup.md`
   - `docs/iCloud-Sync-Setup.md` → `backend/setup/icloud-sync-setup.md`

2. **开发文档**
   - `docs/OPTIMIZATION-PLAN.md` → `backend/development/optimization-plan.md`
   - `docs/TEST-RESULTS.md` → `backend/development/test-results.md`

3. **其他文档**
   - `docs/conversation-context.md` → `backend/setup/conversation-context.md`
   - `docs/README.md` → `backend/README.md`（如果合适）
   - `docs/DEV_CONTEXT.md.backup` - 备份文件（可删除）

**前端文档** → `xiaole-ai/frontend/`（新建目录）

- 所有前端相关的文档都应放在 `xiaole-ai/frontend/` 目录

## 文档管理规则

### 以后的做法

1. **Agent 相关文档** → 保留在当前仓库
   - 所有 `xiaole-agent-context/` 中的文件
   - `.cursorrules` 引用的文件

2. **项目说明文档** → 保留在当前仓库
   - `README.md`（项目根目录）
   - 快速开始、API 说明等

3. **详细文档** → 移到 xiaole-ai 仓库
   - **后端文档** → `xiaole-ai/backend/`
   - **前端文档** → `xiaole-ai/frontend/`
   - 使用指南、设置教程
   - 开发文档、测试文档
   - 架构设计、最佳实践

4. **开发上下文** → 保留在当前仓库（符号链接）
   - `docs/DEV_CONTEXT.md`（iCloud 同步）

## 文档结构

### 当前仓库（xiaole-backend）

```
xiaole-backend/
├── README.md                    # 项目说明（保留）
├── .cursorrules                 # Agent 配置（保留）
├── xiaole-agent-context/        # Agent 规则（保留）
│   ├── persona.md
│   ├── dev-rules.md
│   ├── project-overview.md
│   ├── tools.md
│   └── task-basic-rules.md
└── docs/
    ├── DEV_CONTEXT.md           # 开发上下文（符号链接，保留）
    └── DEV_CONTEXT.md.example   # 模板（可选保留）
```

### Docs 库（xiaole-ai）

根据 [xiaole-ai 仓库](https://github.com/rockts/xiaole-ai) 的结构：

```
xiaole-ai/
├── backend/                     # 后端文档（已存在）
│   ├── setup/                   # 设置相关文档
│   │   ├── multi-repo-setup.md
│   │   ├── icloud-sync-setup.md
│   │   ├── usage.md
│   │   └── conversation-context.md
│   ├── development/             # 开发相关文档
│   │   ├── optimization-plan.md
│   │   └── test-results.md
│   └── README.md                # 后端文档索引（可选）
├── frontend/                    # 前端文档（新建）
│   └── ...                      # 前端相关文档
└── ...
```

## 迁移步骤

1. 在 xiaole-ai 仓库的 `backend/` 目录下创建子目录（如 `setup/`、`development/`）
2. 移动后端文档到 `xiaole-ai/backend/` 对应目录
3. 前端文档（如果有）移动到 `xiaole-ai/frontend/` 目录
4. 更新文档中的链接和引用
5. 删除当前仓库中的已迁移文档
6. 提交更改

## 目录结构说明

- **后端文档** → `xiaole-ai/backend/`（已存在的目录）
- **前端文档** → `xiaole-ai/frontend/`（新建目录）
- **共享文档** → `xiaole-ai/shared/` 或根目录

## 使用迁移脚本

**GitHub 仓库**: [https://github.com/rockts/xiaole-ai](https://github.com/rockts/xiaole-ai)

**注意**：脚本需要的是**本地文件系统路径**，不是 GitHub URL。

```bash
# 设置 docs 仓库路径（本地路径）
# 如果 xiaole-ai 仓库在 ../xiaole-ai（同级目录），可以直接运行
export DOCS_REPO_PATH=../xiaole-ai

# 或者使用绝对路径
# export DOCS_REPO_PATH=/Users/rockts/Dev/xiaole-ai

# 运行迁移脚本
./scripts/move-docs-to-repo.sh
```

脚本会自动：
- 创建 `backend/setup/` 和 `backend/development/` 目录
- 创建 `frontend/` 目录（如果不存在）
- 移动文档到对应位置
- 删除备份文件
