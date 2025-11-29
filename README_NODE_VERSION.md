# Node 版本管理说明

## 📦 版本要求

本项目要求:
- **Node.js**: >= 18.0.0 (推荐 20.x LTS)
- **npm**: >= 9.0.0

当前锁定版本: **20.19.5** (见 `.nvmrc` 文件)

## 🔧 自动版本切换

### 方法 1: 使用 nvm 自动切换 (推荐)

在 `~/.zshrc` 中添加:

```bash
# 小乐 AI 项目环境
source ~/Dev/xiaole-ai/.zshrc_xiaole
```

然后重新加载:
```bash
source ~/.zshrc
```

进入项目目录时会自动切换到正确的 Node 版本。

### 方法 2: 手动切换

```bash
cd ~/Dev/xiaole-ai
nvm use
```

### 方法 3: 全局安装指定版本

```bash
nvm install 20.19.5
nvm alias default 20.19.5
```

## 🚀 启动项目

### 使用统一启动脚本 (推荐)
```bash
./start.sh
```

脚本会自动:
1. 加载 nvm
2. 读取 `.nvmrc` 并切换到正确版本
3. 显示当前 Node 和 npm 版本
4. 启动后端和前端服务

### 单独启动前端
```bash
cd frontend
./start.sh
```

### 快捷命令 (需要加载 .zshrc_xiaole)
```bash
xiaole-start          # 启动完整服务
xiaole-stop           # 停止服务
xiaole-restart        # 重启服务
xiaole-frontend       # 仅启动前端
xiaole-backend        # 仅启动后端
xiaole-logs           # 查看所有日志
```

## 🐛 故障排查

### 问题: npm WARN npm does not support Node.js vXX

**原因**: 当前 Node 版本太旧

**解决**:
```bash
# 检查当前版本
node --version

# 如果版本不对,手动切换
cd ~/Dev/xiaole-ai
nvm use

# 或安装正确版本
nvm install 20.19.5
nvm use 20.19.5
```

### 问题: SyntaxError: Unexpected reserved word

**原因**: Node 版本太旧,不支持 ES6+ 语法

**解决**: 确保使用 Node >= 18

### 问题: nvm: command not found

**原因**: nvm 未安装或未正确配置

**解决**:
```bash
# 安装 nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash

# 或使用 Homebrew
brew install nvm

# 然后在 ~/.zshrc 添加:
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
```

## 📝 文件说明

- `.nvmrc`: 项目 Node 版本锁定文件
- `frontend/.nvmrc`: 前端目录的版本锁定文件  
- `frontend/package.json`: 包含 `engines` 字段限制版本
- `.zshrc_xiaole`: 自动环境配置脚本
- `start.sh`: 统一启动脚本,自动切换版本
- `frontend/start.sh`: 前端独立启动脚本

## ✅ 验证配置

```bash
# 1. 进入项目目录
cd ~/Dev/xiaole-ai

# 2. 检查版本
node --version    # 应该显示 v20.19.5
npm --version     # 应该显示 >= 9.0.0

# 3. 测试启动
./start.sh
```

---

**更新日期**: 2025-11-29  
**维护者**: @rockts
