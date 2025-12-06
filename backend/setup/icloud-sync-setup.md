# iCloud 同步设置指南

## 方案：使用 iCloud 同步开发上下文

开发上下文文件使用 iCloud 在 Mac 设备间同步，**不提交到代码库**，确保安全。

## 快速设置

### 方法 1：直接在 iCloud Drive 中创建文件（推荐）

1. **创建 iCloud 目录**：
   ```bash
   mkdir -p ~/Library/Mobile\ Documents/com~apple~CloudDocs/XiaoleDev
   ```

2. **创建开发上下文文件**：
   ```bash
   cp docs/DEV_CONTEXT.md.example \
      ~/Library/Mobile\ Documents/com~apple~CloudDocs/XiaoleDev/xiaole-backend-context.md
   ```

3. **在所有 Mac 设备上访问**：
   - 文件会自动同步到所有登录了相同 Apple ID 的 Mac
   - 路径：`~/Library/Mobile Documents/com~apple~CloudDocs/XiaoleDev/xiaole-backend-context.md`

### 方法 2：使用符号链接（在项目目录中可见）

1. **创建 iCloud 文件**：
   ```bash
   mkdir -p ~/Library/Mobile\ Documents/com~apple~CloudDocs/XiaoleDev
   cp docs/DEV_CONTEXT.md.example \
      ~/Library/Mobile\ Documents/com~apple~CloudDocs/XiaoleDev/xiaole-backend-context.md
   ```

2. **创建符号链接**：
   ```bash
   ln -s ~/Library/Mobile\ Documents/com~apple~CloudDocs/XiaoleDev/xiaole-backend-context.md \
         docs/DEV_CONTEXT.md
   ```

3. **优势**：
   - 文件在项目目录中可见
   - 实际存储在 iCloud 中，自动同步
   - 不会提交到 Git（符号链接指向的文件已加入 .gitignore）

## 使用流程

### 日常使用

1. **编辑文件**：
   - 直接编辑 iCloud 中的文件
   - 或通过符号链接编辑 `docs/DEV_CONTEXT.md`

2. **自动同步**：
   - iCloud 会自动在后台同步
   - 通常几秒内完成同步

3. **其他设备**：
   - 打开相同路径的文件即可
   - 确保 iCloud Drive 已启用并同步

### 检查同步状态

```bash
# 查看 iCloud 文件
ls -la ~/Library/Mobile\ Documents/com~apple~CloudDocs/XiaoleDev/

# 检查文件是否在同步
# 在 Finder 中查看文件图标，如果有云朵图标表示正在同步
```

## 安全提示

✅ **安全**：
- 文件存储在 iCloud 中，端到端加密
- 不会提交到公开的代码库
- 只有你的 Apple ID 可以访问

⚠️ **注意事项**：
- 不要在文件中记录真实的密钥、密码、API Key
- 使用占位符：`[API_KEY]`、`[PASSWORD]`
- 敏感信息存储在 `.env` 文件中（已加入 .gitignore）

## 故障排除

### iCloud 未同步

1. **检查 iCloud Drive 是否启用**：
   - 系统设置 → Apple ID → iCloud → iCloud Drive

2. **检查文件是否在同步**：
   - Finder 中查看文件图标
   - 云朵图标 = 正在同步
   - 实心图标 = 已下载到本地

3. **手动触发同步**：
   - 在 Finder 中右键文件 → "下载"

### 符号链接不工作

如果使用符号链接，确保：
- 目标文件已存在于 iCloud 中
- 路径正确（注意空格需要转义）

## 文件位置总结

- **模板文件**：`docs/DEV_CONTEXT.md.example`（可提交到仓库）
- **实际文件**：`~/Library/Mobile Documents/com~apple~CloudDocs/XiaoleDev/xiaole-backend-context.md`（iCloud 同步）
- **符号链接**：`docs/DEV_CONTEXT.md`（可选，指向 iCloud 文件）

