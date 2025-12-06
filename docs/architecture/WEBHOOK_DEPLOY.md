# GitHub Webhook 自动部署

## 功能
Push 到 `main` 分支后,Docker 容器自动拉取代码并重新加载。

## 架构
- Webhook 服务运行在 Docker 容器内(端口 9000)
- 收到 GitHub push 通知后,在容器内执行 `git pull`
- 通过 `kill 1` 触发容器重启,Docker 自动重启加载新代码
- 无需在 NAS 系统安装 Python/Flask

## 部署步骤

### 1. 生成 Webhook 密钥
```bash
# 在本地或 NAS 上生成
python -c "import os; print(os.urandom(32).hex())"
# 记下生成的密钥,用于 GitHub 和 .env 配置
```

### 2. 配置环境变量
编辑 NAS 上的 `.env` 文件:
```bash
ssh admin@192.168.88.188
cd /volume2/docker/xiaole-ai
nano .env
```

添加 webhook 密钥:
```bash
WEBHOOK_SECRET=your-generated-secret-here
```

### 3. 配置 Cloudflare Tunnel
在 Cloudflare Zero Trust 控制台添加:
```yaml
ingress:
  - hostname: ai.leke.xyz
    service: http://192.168.88.188:8000
  - hostname: webhook.leke.xyz  # 新增
    service: http://192.168.88.188:9000
```

### 4. 在 GitHub 仓库设置 Webhook
1. 进入仓库 Settings → Webhooks → Add webhook
2. Payload URL: `https://webhook.leke.xyz/webhook`
3. Content type: `application/json`
4. Secret: 填入第1步生成的密钥
5. 选择 `Just the push event`
6. 勾选 `Active`
7. 点击 `Add webhook`

### 5. 首次部署
在 NAS 上执行:
```bash
cd /volume2/docker/xiaole-ai
sudo bash deploy_prod.sh
```

完成后,webhook 服务会自动在容器内启动。

## 测试
```bash
# 本地 push 到 main
git push origin main

# 在 NAS 查看容器日志
sudo docker logs -f xiaole-ai
```

## 查看 Webhook 日志
```bash
# 查看实时日志
sudo docker logs -f xiaole-ai | grep webhook

# 测试 webhook 健康状态
curl http://192.168.88.188:9000/health
```

## 工作原理
1. GitHub push 到 main → 发送 webhook 到 `webhook.leke.xyz`
2. Cloudflare Tunnel → Docker 容器 9000 端口
3. Flask 服务验证签名 → 执行 `git pull origin main`
4. 如有更新 → `kill 1` 触发容器退出
5. Docker `--restart=always` → 自动重启容器
6. 容器启动 → 加载新代码

## 安全建议
- ✅ 使用强随机密钥(32字节)
- ✅ 只监听 main 分支
- ✅ 验证 GitHub HMAC-SHA256 签名
- ✅ Webhook 服务在容器内,不暴露到公网
- ✅ 通过 Cloudflare Tunnel 暴露(自动 HTTPS + DDoS 防护)
