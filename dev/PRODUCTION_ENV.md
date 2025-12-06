# 生产环境配置指南

## NAS 环境变量配置

在 NAS 的 `/volume2/docker/xiaole-ai/.env` 文件中配置生产环境变量。

### 1. 数据库配置
```bash
DB_HOST=192.168.88.188
DB_PORT=5432
DB_NAME=xiaole_ai
DB_USER=xiaole_user
DB_PASS=your_production_db_password
```

### 2. AI API 配置
```bash
# DeepSeek API
DEEPSEEK_API_KEY=your_deepseek_api_key

# Qwen API (视觉功能)
QWEN_API_KEY=your_qwen_api_key

# 百度语音 API
BAIDU_APP_ID=your_baidu_app_id
BAIDU_API_KEY=your_baidu_api_key
BAIDU_SECRET_KEY=your_baidu_secret_key
```

### 3. 管理员密码（重要）⚠️

**生成密码哈希**:
```bash
# 在本地或 NAS 上执行
python -c "import bcrypt; password = input('输入密码: ').encode('utf-8'); print(bcrypt.hashpw(password, bcrypt.gensalt()).decode('utf-8'))"
```

**配置到 .env**:
```bash
ADMIN_USERNAME=admin
ADMIN_PASSWORD_HASH=$2b$12$XdpfzbBMZvpVXgBUVgA63ug5xubhhrkNV80ChIhE/Bs9toHJEkMVa
```

### 4. Webhook 配置

```bash
# 生成随机密钥
WEBHOOK_SECRET=$(python -c "import os; print(os.urandom(32).hex())")
```

配置到 `.env`:
```bash
WEBHOOK_SECRET=your_generated_webhook_secret
```

### 5. JWT 密钥

```bash
# 生成随机密钥
SECRET_KEY=$(python -c "import os; print(os.urandom(32).hex())")
```

配置到 `.env`:
```bash
SECRET_KEY=your_generated_jwt_secret
```

## 完整 .env 模板

```bash
# 数据库配置
DB_HOST=192.168.88.188
DB_PORT=5432
DB_NAME=xiaole_ai
DB_USER=xiaole_user
DB_PASS=CHANGE_THIS_DB_PASSWORD

# AI API 配置
DEEPSEEK_API_KEY=CHANGE_THIS_DEEPSEEK_KEY
QWEN_API_KEY=CHANGE_THIS_QWEN_KEY

# 百度语音 API
BAIDU_APP_ID=CHANGE_THIS_BAIDU_APP_ID
BAIDU_API_KEY=CHANGE_THIS_BAIDU_API_KEY
BAIDU_SECRET_KEY=CHANGE_THIS_BAIDU_SECRET_KEY

# 管理员账号（使用 bcrypt 生成的哈希）
ADMIN_USERNAME=admin
ADMIN_PASSWORD_HASH=CHANGE_THIS_TO_BCRYPT_HASH

# Webhook 密钥（32字节随机）
WEBHOOK_SECRET=CHANGE_THIS_WEBHOOK_SECRET

# JWT 密钥（32字节随机）
SECRET_KEY=CHANGE_THIS_JWT_SECRET
```

## 安全检查清单

- [ ] 修改所有 `CHANGE_THIS_*` 占位符
- [ ] 使用强密码（至少12位，包含大小写字母、数字、特殊字符）
- [ ] 密码哈希使用 bcrypt 生成
- [ ] Webhook 密钥至少 32 字节随机
- [ ] JWT 密钥至少 32 字节随机
- [ ] `.env` 文件权限设置为 600 (`chmod 600 .env`)
- [ ] 不要将 `.env` 提交到 Git 仓库

## 首次部署

```bash
# 1. SSH 登录 NAS
ssh admin@192.168.88.188

# 2. 进入项目目录
cd /volume2/docker/xiaole-ai

# 3. 创建并编辑 .env 文件
nano .env
# 粘贴上面的模板,修改所有 CHANGE_THIS_* 值

# 4. 设置文件权限
chmod 600 .env

# 5. 执行部署
sudo bash deploy_prod.sh

# 6. 验证服务
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:9000/health
```

## 更新密码

如需更新管理员密码:

```bash
# 1. 生成新密码哈希
python -c "import bcrypt; password = 'your_new_password'.encode('utf-8'); print(bcrypt.hashpw(password, bcrypt.gensalt()).decode('utf-8'))"

# 2. 更新 .env 中的 ADMIN_PASSWORD_HASH

# 3. 重启容器
sudo docker restart xiaole-ai
```

## 密钥轮换建议

- **数据库密码**: 每年更换一次
- **API Keys**: 发现泄露时立即更换
- **管理员密码**: 每季度更换一次
- **Webhook 密钥**: 每半年更换一次
- **JWT 密钥**: 更换后所有用户需重新登录
