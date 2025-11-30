# GitHub Webhook 自动部署

## 功能
Push 到 `main` 分支后,NAS 自动拉取代码并重新部署。

## 部署步骤

### 1. 在 NAS 上安装 Flask
```bash
# 群晖 DSM 6.2.3 使用 pip 而不是 pip3
sudo pip install flask
```

### 2. 生成并设置 Webhook 密钥
```bash
cd /volume2/docker/xiaole-ai

# 生成随机密钥
python -c "import os; print(os.urandom(32).hex())"
# 记下生成的密钥,稍后在 GitHub 和启动脚本中使用
```

### 3. 创建启动脚本
群晖 DSM 6.2.3 不支持 systemd,需要手动创建启动脚本:

```bash
# 创建启动脚本
sudo nano /volume2/docker/xiaole-ai/start_webhook.sh
```

填入以下内容:
```bash
#!/bin/bash
cd /volume2/docker/xiaole-ai

export WEBHOOK_SECRET="your-generated-secret-here"
export DB_USER="your_db_user"
export DB_PASS="your_db_password"
export DEEPSEEK_API_KEY="your_deepseek_api_key"
export QWEN_API_KEY="your_qwen_api_key"
export BAIDU_APP_ID="your_baidu_app_id"
export BAIDU_API_KEY="your_baidu_api_key"
export BAIDU_SECRET_KEY="your_baidu_secret_key"

nohup python webhook_deploy.py > /var/log/webhook_deploy.log 2>&1 &
echo $! > /var/run/webhook_deploy.pid
echo "Webhook 服务已启动,PID: $(cat /var/run/webhook_deploy.pid)"
```

```bash
# 添加执行权限
sudo chmod +x /volume2/docker/xiaole-ai/start_webhook.sh

# 启动服务
sudo bash /volume2/docker/xiaole-ai/start_webhook.sh

# 查看日志
tail -f /var/log/webhook_deploy.log
```

### 4. 配置 Cloudflare Tunnel
在群晖 DSM 控制面板中:
1. 打开 **控制面板** → **任务计划**
2. 新增 → **触发的任务** → **用户定义的脚本**
3. 常规设置:
   - 任务名称: `Webhook Auto Deploy`
   - 用户: `root`
   - 事件: `开机`
4. 任务设置 → 运行命令:
   ```bash
   bash /volume2/docker/xiaole-ai/start_webhook.sh
   ```
5. 点击确定

### 5. 管理 Webhook 服务
```bash
# 查看进程
ps aux | grep webhook_deploy

# 停止服务
sudo kill $(cat /var/run/webhook_deploy.pid)

# 重启服务
sudo kill $(cat /var/run/webhook_deploy.pid)
sudo bash /volume2/docker/xiaole-ai/start_webhook.sh

# 查看日志
tail -f /var/log/webhook_deploy.log
```

### 4. 配置 Cloudflare Tunnel
在 Cloudflare 配置中添加:
```yaml
ingress:
  - hostname: ai.leke.xyz
    service: http://192.168.88.188:8000
  - hostname: webhook.leke.xyz  # 新增
    service: http://192.168.88.188:9000
```

### 6. 在 GitHub 仓库设置 Webhook
1. 进入仓库 Settings → Webhooks → Add webhook
2. Payload URL: `https://webhook.leke.xyz/webhook`
3. Content type: `application/json`
4. Secret: 填入第2步生成的密钥
5. 选择 `Just the push event`
6. 勾选 `Active`
7. 点击 `Add webhook`

## 测试
```bash
# 本地 push 到 main
git push origin main

# 在 NAS 上查看日志
sudo journalctl -u webhook_deploy -f
```

## 安全建议
- ✅ 使用强随机密钥
- ✅ 只监听 main 分支
- ✅ 验证 GitHub 签名
- ✅ Webhook 服务只监听内网
- ✅ 通过 Cloudflare Tunnel 暴露(自动 HTTPS)
