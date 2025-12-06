# 多仓库开发上下文设置指南

## 问题 1：前端项目（另一个仓库）如何设置？

### 方案：为每个仓库单独设置

每个仓库（前端、后端）都有自己独立的开发上下文文件。

### 设置步骤

#### 1. 前端仓库设置

```bash
# 进入前端仓库
cd /path/to/xiaole-web

# 创建 .cursorrules（如果不存在）
cat > .cursorrules << 'EOF'
Include context from ./xiaole-agent-context/*

# 开发上下文（iCloud 同步，不提交到代码库）
Include context from ./docs/DEV_CONTEXT.md if it exists
EOF

# 创建 docs 目录
mkdir -p docs

# 创建符号链接指向 iCloud（使用不同的文件名区分前后端）
ln -s ~/Library/Mobile\ Documents/com~apple~CloudDocs/XiaoleDev/xiaole-web-context.md \
      docs/DEV_CONTEXT.md

# 如果 iCloud 文件不存在，先创建
if [ ! -f ~/Library/Mobile\ Documents/com~apple~CloudDocs/XiaoleDev/xiaole-web-context.md ]; then
  cp docs/DEV_CONTEXT.md.example \
     ~/Library/Mobile\ Documents/com~apple~CloudDocs/XiaoleDev/xiaole-web-context.md 2>/dev/null || \
  echo "# 前端开发上下文\n\n## 当前任务\n\n## 对话记录\n" > \
     ~/Library/Mobile\ Documents/com~apple~CloudDocs/XiaoleDev/xiaole-web-context.md
fi
```

#### 2. 文件命名建议

在 iCloud 中使用不同的文件名区分前后端：

- **后端**：`xiaole-backend-context.md`
- **前端**：`xiaole-web-context.md`
- **文档**：`xiaole-ai-context.md`（如果有）

#### 3. 共享的 Agent 规则（可选）

如果前后端共享一些规则，可以：

1. **方案 A**：每个仓库维护自己的 `xiaole-agent-context/`
2. **方案 B**：在 iCloud 中创建共享规则目录
   ```bash
   # 创建共享规则目录
   mkdir -p ~/Library/Mobile\ Documents/com~apple~CloudDocs/XiaoleDev/shared-rules
   
   # 在 .cursorrules 中引用
   Include context from ~/Library/Mobile\ Documents/com~apple~CloudDocs/XiaoleDev/shared-rules/*
   ```

---

## 问题 2：在其他电脑上继续开发

### 快速设置步骤

#### 1. 克隆/拉取代码

```bash
# 克隆仓库（如果还没有）
git clone https://github.com/rockts/xiaole-backend.git
cd xiaole-backend

# 或拉取最新代码
git pull origin develop
```

#### 2. 创建符号链接

```bash
# 确保 iCloud 目录存在
mkdir -p ~/Library/Mobile\ Documents/com~apple~CloudDocs/XiaoleDev

# 创建符号链接（指向 iCloud 文件）
ln -s ~/Library/Mobile\ Documents/com~apple~CloudDocs/XiaoleDev/xiaole-backend-context.md \
      docs/DEV_CONTEXT.md

# 验证
ls -la docs/DEV_CONTEXT.md
# 应该显示：symbolic link
```

#### 3. 等待 iCloud 同步

- 打开 Finder，导航到 `~/Library/Mobile Documents/com~apple~CloudDocs/XiaoleDev/`
- 查看文件图标：
  - 云朵图标 ☁️ = 正在同步/未下载
  - 实心图标 = 已下载到本地
- 如果显示云朵，右键文件 → "下载" 手动触发同步

#### 4. 验证设置

```bash
# 检查文件是否存在
ls -la docs/DEV_CONTEXT.md

# 检查内容
cat docs/DEV_CONTEXT.md | head -10

# 检查 .cursorrules
cat .cursorrules
```

---

## 完整设置脚本

### 后端仓库设置脚本

```bash
#!/bin/bash
# setup-backend-context.sh

REPO_DIR="/path/to/xiaole-backend"
ICLOUD_DIR="$HOME/Library/Mobile Documents/com~apple~CloudDocs/XiaoleDev"
CONTEXT_FILE="xiaole-backend-context.md"

cd "$REPO_DIR" || exit 1

# 创建 iCloud 目录
mkdir -p "$ICLOUD_DIR"

# 创建 .cursorrules（如果不存在）
if [ ! -f .cursorrules ]; then
  cat > .cursorrules << 'EOF'
Include context from ./xiaole-agent-context/*

# 开发上下文（iCloud 同步，不提交到代码库）
Include context from ./docs/DEV_CONTEXT.md if it exists
EOF
fi

# 创建 docs 目录
mkdir -p docs

# 创建 iCloud 文件（如果不存在）
if [ ! -f "$ICLOUD_DIR/$CONTEXT_FILE" ]; then
  echo "# 后端开发上下文

## 当前任务

## 对话记录

## 待办事项
" > "$ICLOUD_DIR/$CONTEXT_FILE"
fi

# 创建符号链接
if [ -L docs/DEV_CONTEXT.md ]; then
  echo "符号链接已存在"
elif [ -f docs/DEV_CONTEXT.md ]; then
  mv docs/DEV_CONTEXT.md docs/DEV_CONTEXT.md.backup
  ln -s "$ICLOUD_DIR/$CONTEXT_FILE" docs/DEV_CONTEXT.md
else
  ln -s "$ICLOUD_DIR/$CONTEXT_FILE" docs/DEV_CONTEXT.md
fi

echo "✅ 设置完成！"
echo "文件位置: docs/DEV_CONTEXT.md -> $ICLOUD_DIR/$CONTEXT_FILE"
```

### 前端仓库设置脚本

```bash
#!/bin/bash
# setup-frontend-context.sh

REPO_DIR="/path/to/xiaole-web"
ICLOUD_DIR="$HOME/Library/Mobile Documents/com~apple~CloudDocs/XiaoleDev"
CONTEXT_FILE="xiaole-web-context.md"

# ... 类似上面的脚本，但使用 xiaole-web-context.md
```

---

## 文件结构总结

### iCloud 目录结构

```
~/Library/Mobile Documents/com~apple~CloudDocs/XiaoleDev/
├── xiaole-backend-context.md    # 后端开发上下文
├── xiaole-web-context.md        # 前端开发上下文
└── shared-rules/                # 共享规则（可选）
    ├── common-persona.md
    └── common-rules.md
```

### 后端仓库结构

```
xiaole-backend/
├── .cursorrules                 # 自动读取配置
├── xiaole-agent-context/        # 后端规则
│   ├── persona.md
│   ├── dev-rules.md
│   └── ...
└── docs/
    └── DEV_CONTEXT.md           # 符号链接 → iCloud
```

### 前端仓库结构

```
xiaole-web/
├── .cursorrules                 # 自动读取配置
├── xiaole-agent-context/        # 前端规则（如果有）
│   └── ...
└── docs/
    └── DEV_CONTEXT.md           # 符号链接 → iCloud
```

---

## 常见问题

### Q: 新电脑上 iCloud 文件显示为云朵图标？

A: 这是正常的，iCloud 默认只下载元数据。右键文件 → "下载" 即可。

### Q: 如何确保文件已同步？

A: 
1. 在 Finder 中查看文件图标（实心 = 已下载）
2. 检查文件修改时间
3. 在两个设备上编辑文件，看是否同步

### Q: 前后端可以共享开发上下文吗？

A: 可以，但建议分开：
- **分开**：更清晰，避免混淆
- **共享**：如果前后端任务关联性强，可以创建一个共享文件

### Q: 如果 iCloud 不可用怎么办？

A: 备选方案：
1. 使用 Git LFS + 私有仓库
2. 使用加密的云存储（如 Dropbox、OneDrive）
3. 使用密码管理器（如 1Password）的笔记功能

---

## 快速检查清单

在新电脑上设置时：

- [ ] 克隆/拉取代码
- [ ] 创建 iCloud 目录
- [ ] 创建符号链接
- [ ] 等待 iCloud 同步
- [ ] 验证 `.cursorrules` 存在
- [ ] 测试 AI 能否读取上下文

