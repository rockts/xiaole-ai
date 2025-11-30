# GitHub Webhook 自动部署

## 功能
Push 到 `main` 分支后,NAS 自动拉取代码并重新部署。

## 部署步骤

### 1. 在 NAS 上安装 Flask
```bash
pip3 install flask
```

### 2. 设置 Webhook 密钥
编辑 `webhook_deploy.service`,修改 `WEBHOOK_SECRET`:
```bash
Environment="WEBHOOK_SECRET=your-strong-random-secret"
```
生成随机密钥:
```bash
openssl rand -hex 32
```

### 3. 启动 Webhook 服务
```bash
# 复制服务文件
sudo cp webhook_deploy.service /etc/systemd/system/

# 重载配置
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start webhook_deploy

# 开机自启
sudo systemctl enable webhook_deploy

# 查看状态
sudo systemctl status webhook_deploy
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

### 5. 在 GitHub 仓库设置 Webhook
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
