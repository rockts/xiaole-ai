# 开发上下文使用指南

## 自动读取机制

### 当前配置

`.cursorrules` 文件已配置为**自动读取**开发上下文：

```
Include context from ./xiaole-agent-context/*
Include context from ./docs/DEV_CONTEXT.md if it exists
```

### 工作原理

1. **自动读取**：
   - 当你与 AI 对话时，Cursor 会自动读取 `docs/DEV_CONTEXT.md`
   - 如果文件存在，AI 会自动了解当前的开发上下文
   - **无需手动操作**

2. **文件位置**：
   - `docs/DEV_CONTEXT.md` 是符号链接，指向 iCloud 文件
   - 实际文件：`~/Library/Mobile Documents/com~apple~CloudDocs/XiaoleDev/xiaole-backend-context.md`
   - 所有 Mac 设备自动同步

3. **更新方式**：
   - 直接编辑 `docs/DEV_CONTEXT.md`
   - 或编辑 iCloud 中的实际文件
   - 保存后，下次对话时 AI 会自动读取最新内容

## 使用流程

### 日常开发

1. **开始对话前**（可选）：
   - 更新 `docs/DEV_CONTEXT.md` 记录当前任务状态
   - 或让 AI 自动从对话中了解上下文

2. **与 AI 对话**：
   - AI 会自动读取 `docs/DEV_CONTEXT.md`（如果存在）
   - AI 会自动读取 `xiaole-agent-context/*` 中的所有规则文件
   - **无需手动附加文件**

3. **对话后**（可选）：
   - 更新 `docs/DEV_CONTEXT.md` 记录重要信息
   - 保存后自动同步到其他设备

### 手动方式（如果需要）

如果自动读取不工作，可以：

1. **手动附加文件**：
   - 在 Cursor 中手动附加 `docs/DEV_CONTEXT.md` 到对话

2. **直接引用**：
   - 在对话中说："参考 docs/DEV_CONTEXT.md"
   - AI 会主动读取该文件

## 文件结构

```
xiaole-backend/
├── .cursorrules                    # 自动读取配置
├── xiaole-agent-context/          # Agent 规则（自动读取）
│   ├── persona.md
│   ├── project-overview.md
│   ├── dev-rules.md
│   ├── tools.md
│   └── task-basic-rules.md
└── docs/
    ├── DEV_CONTEXT.md             # 开发上下文（符号链接 → iCloud，自动读取）
    ├── DEV_CONTEXT.md.example     # 模板（可提交）
    └── README.md                   # 使用说明
```

## 验证自动读取

### 测试方法

1. **更新文件**：
   ```bash
   echo "## 测试任务\n- 状态: in_progress" >> docs/DEV_CONTEXT.md
   ```

2. **开始新对话**：
   - 问 AI："当前有什么任务？"
   - AI 应该能读取到 `docs/DEV_CONTEXT.md` 中的内容

3. **检查**：
   - 如果 AI 能回答文件中的内容，说明自动读取工作正常

## 注意事项

1. **文件必须存在**：
   - 如果 `docs/DEV_CONTEXT.md` 不存在，AI 不会报错，只是不会读取
   - 确保符号链接正确指向 iCloud 文件

2. **iCloud 同步**：
   - 文件修改后，iCloud 会自动同步
   - 其他设备上需要等待同步完成

3. **敏感信息**：
   - 不要在文件中记录真实的密钥、密码
   - 使用占位符：`[API_KEY]`、`[PASSWORD]`

## 故障排除

### AI 无法读取文件

1. **检查文件是否存在**：
   ```bash
   ls -la docs/DEV_CONTEXT.md
   ```

2. **检查符号链接**：
   ```bash
   file docs/DEV_CONTEXT.md
   # 应该显示：symbolic link
   ```

3. **检查 iCloud 文件**：
   ```bash
   ls -la ~/Library/Mobile\ Documents/com~apple~CloudDocs/XiaoleDev/
   ```

4. **重新创建符号链接**（如果需要）：
   ```bash
   rm docs/DEV_CONTEXT.md
   ln -s ~/Library/Mobile\ Documents/com~apple~CloudDocs/XiaoleDev/xiaole-backend-context.md \
         docs/DEV_CONTEXT.md
   ```

