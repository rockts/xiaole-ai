# Webhook 403 问题调试记录

**日期**: 2024年12月1日  
**问题**: GitHub Webhook 一直返回 403 Forbidden,自动部署无法工作

## 问题现象

1. GitHub Webhook 配置正确,指向 `https://webhook.leke.xyz/webhook`
2. Cloudflare Tunnel 正常工作,请求能到达容器
3. Webhook 服务运行在容器内 9000 端口
4. 每次 GitHub 发送 webhook 请求都返回 403
5. 容器日志显示:
   ```
   172.17.0.1 - - [30/Nov/2025 20:51:52] "POST /webhook HTTP/1.1" 403 -
   ```

## 已尝试的解决方案

### 1. 同步 WEBHOOK_SECRET
- 确认 NAS `.env` 文件中的密钥: `deb84ca1ba574384c866d90eba3bf809bc6891dcf8ababc41a4724efa90f3fe4`
- 在 GitHub Webhook 设置中更新了 Secret
- 多次 Redeliver 仍然 403

### 2. 添加调试日志
**修改记录**:
- Commit `2f6c60b`: 添加 print 调试日志
- Commit `7e00520`: 改用 sys.stderr 输出
- Commit `50d243b`: 格式化调整

**调试代码**:
```python
import sys

@app.route("/webhook", methods=["POST"])
def webhook():
    signature = request.headers.get("X-Hub-Signature-256")
    
    # 调试日志
    sys.stderr.write(f"[DEBUG] Webhook received\n")
    sys.stderr.write(f"[DEBUG] Signature from GitHub: {signature}\n")
    sys.stderr.write(f"[DEBUG] WEBHOOK_SECRET (first 8): {WEBHOOK_SECRET[:8]}...\n")
    sys.stderr.write(f"[DEBUG] WEBHOOK_SECRET (last 8): ...{WEBHOOK_SECRET[-8:]}\n")
    sys.stderr.write(f"[DEBUG] Payload size: {len(request.data)} bytes\n")
    sys.stderr.flush()
    
    if not verify_signature(request.data, signature):
        sys.stderr.write("[DEBUG] ❌ Signature verification FAILED!\n")
        sys.stderr.flush()
        return jsonify({"error": "Invalid signature"}), 403
```

**问题**: 调试日志从未在容器日志中出现!

### 3. 更新容器内文件
尝试的方法:
```bash
# 方法1: Git pull + restart
sudo git pull origin main
sudo docker restart xiaole-ai

# 方法2: Docker cp
sudo docker cp webhook_deploy.py xiaole-ai:/app/webhook_deploy.py
sudo docker restart xiaole-ai

# 方法3: 重新部署
sudo bash deploy_prod.sh
```

**问题**: 容器重启后,webhook 仍然运行旧代码,调试日志不出现

## 技术细节

### 架构
```
GitHub Push → GitHub Webhook → Cloudflare Tunnel (webhook.leke.xyz) 
→ NAS (192.168.88.188:9000) → Docker Container (xiaole-ai) 
→ Flask (webhook_deploy.py)
```

### 关键文件
- **NAS 路径**: `/volume2/docker/xiaole-ai/webhook_deploy.py`
- **容器路径**: `/app/webhook_deploy.py`
- **启动脚本**: `start_services.sh` (启动 webhook + FastAPI)
- **环境变量**: `/volume2/docker/xiaole-ai/.env`

### GitHub Webhook 信息
**最近一次请求** (2025年12月1日 04:33:31):
```json
{
  "X-Hub-Signature-256": "sha256=7dc43b1cc6c416f66307f080f5f1cbdaa099a9b4e78540ddf376afddb47b6fe6",
  "Content-Length": 7311,
  "Content-Type": "application/json",
  "X-Github-Event": "push"
}
```

### 签名验证逻辑
```python
def verify_signature(payload_body, signature_header):
    """验证 GitHub Webhook 签名"""
    if not signature_header:
        return False
    
    hash_object = hmac.new(
        WEBHOOK_SECRET.encode('utf-8'),
        msg=payload_body,
        digestmod=hashlib.sha256
    )
    expected_signature = "sha256=" + hash_object.hexdigest()
    return hmac.compare_digest(expected_signature, signature_header)
```

## 未解决的疑问

1. **为什么调试日志不出现?**
   - 容器内文件是否真的更新了?
   - Flask 是否使用了缓存的 .pyc 文件?
   - start_services.sh 是否在后台自动重启旧版本?

2. **WEBHOOK_SECRET 是否真的匹配?**
   - 无法验证,因为调试日志看不到
   - GitHub 的 Secret 是否真的保存成功?
   - 是否有编码问题(UTF-8, 换行符等)?

3. **Docker 镜像缓存问题?**
   - webhook_deploy.py 在构建时就打包进镜像
   - docker cp 是否真的能覆盖镜像内的文件?
   - 是否需要重新构建镜像?

## 下一步计划

### 方案 A: 重新构建 Docker 镜像 (推荐)
```bash
cd /volume2/docker/xiaole-ai
sudo git reset --hard origin/main
sudo docker stop xiaole-ai
sudo docker rm xiaole-ai
sudo docker build --no-cache -t xiaole-ai:prod .
sudo docker run -d --name xiaole-ai --restart=always \
  -p 8000:8000 -p 9000:9000 \
  -v /volume2/docker/xiaole-ai/logs:/app/logs \
  --env-file /volume2/docker/xiaole-ai/.env \
  xiaole-ai:prod
```

### 方案 B: 手动启动 Webhook 服务
```bash
# 进入容器
sudo docker exec -it xiaole-ai bash

# 查看当前文件
cat /app/webhook_deploy.py | head -20

# 如果是旧文件,从挂载卷复制
cp /volume2/docker/xiaole-ai/webhook_deploy.py /app/

# 杀掉旧进程
pkill -9 -f webhook_deploy

# 手动启动
python3 /app/webhook_deploy.py &
```

### 方案 C: 简化调试 - 直接测试签名验证
创建测试脚本验证签名:
```python
import hmac
import hashlib

SECRET = "deb84ca1ba574384c866d90eba3bf809bc6891dcf8ababc41a4724efa90f3fe4"
SIGNATURE = "sha256=7dc43b1cc6c416f66307f080f5f1cbdaa099a9b4e78540ddf376afddb47b6fe6"

# 需要获取真实的 payload
payload = b'...'  # 从 GitHub webhook delivery 复制

hash_object = hmac.new(SECRET.encode('utf-8'), msg=payload, digestmod=hashlib.sha256)
expected = "sha256=" + hash_object.hexdigest()

print(f"Expected: {expected}")
print(f"Received: {SIGNATURE}")
print(f"Match: {expected == SIGNATURE}")
```

## 相关 Git 提交

- `fd5f622` - test: webhook 自动部署测试 2
- `2f6c60b` - debug: 添加 webhook 签名验证调试日志
- `7e00520` - debug: 使用 stderr 输出调试日志
- `50d243b` - style: 格式化调试代码

**注意**: 这些调试提交在 main 分支上,违反了工作流规范。问题解决后需要清理。

## 环境信息

- **NAS**: Synology DSM 6.2.3
- **Docker**: 运行在 NAS 上
- **容器**: xiaole-ai:prod
- **Python**: 3.11-slim (容器内)
- **Flask**: 开发模式运行在 0.0.0.0:9000
- **Cloudflare Tunnel**: 映射 webhook.leke.xyz → 192.168.88.188:9000

## 已知问题

1. Flask 运行在开发模式 (`app.run()`)
2. 没有使用生产级 WSGI 服务器 (如 gunicorn)
3. Webhook 服务和 FastAPI 在同一个容器内
4. 调试日志添加后无法生效

## 临时绕过方案

如果急需部署,可以暂时手动在 NAS 上执行:
```bash
cd /volume2/docker/xiaole-ai
sudo git pull origin main
sudo docker restart xiaole-ai
```

虽然 webhook 不工作,但手动部署还是可以的。

---

**更新时间**: 2024-12-01 20:51  
**状态**: 待解决  
**优先级**: 高 (阻碍自动化部署)
