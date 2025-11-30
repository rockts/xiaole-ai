# Cloudflare Tunnel 配置

## 概述
通过 Cloudflare Tunnel 将 NAS 上的服务安全暴露到公网,无需开放防火墙端口。

## 域名和服务映射

### 主服务
- **域名**: `ai.leke.xyz`
- **目标**: `http://192.168.88.188:8000`
- **说明**: 小乐 AI 主应用(FastAPI + 前端静态文件)

### Webhook 服务
- **域名**: `webhook.leke.xyz`
- **目标**: `http://192.168.88.188:9000`
- **说明**: GitHub Webhook 自动部署服务

## Cloudflare Tunnel 配置文件

在 Cloudflare Zero Trust 控制台中配置,或使用配置文件 `config.yml`:

```yaml
tunnel: <your-tunnel-id>
credentials-file: /root/.cloudflared/<your-tunnel-id>.json

ingress:
  # 主应用
  - hostname: ai.leke.xyz
    service: http://192.168.88.188:8000
    originRequest:
      noTLSVerify: true
  
  # Webhook 服务
  - hostname: webhook.leke.xyz
    service: http://192.168.88.188:9000
    originRequest:
      noTLSVerify: true
  
  # 兜底规则(必需)
  - service: http_status:404
```

## 在 Cloudflare Zero Trust 控制台配置

### 1. 创建 Tunnel
1. 登录 [Cloudflare Zero Trust](https://one.dash.cloudflare.com/)
2. 进入 **Access** → **Tunnels**
3. 点击 **Create a tunnel**
4. 选择 **Cloudflared**
5. 输入名称(如 `xiaole-ai-nas`)
6. 按照指引在 NAS 上安装 cloudflared

### 2. 配置公共主机名

#### 主应用配置
- **Subdomain**: `ai`
- **Domain**: `leke.xyz`
- **Service**: `HTTP`
- **URL**: `192.168.88.188:8000`

#### Webhook 配置
- **Subdomain**: `webhook`
- **Domain**: `leke.xyz`
- **Service**: `HTTP`
- **URL**: `192.168.88.188:9000`

### 3. 高级设置(可选)
- **HTTP 设置**:
  - `No TLS Verify`: 启用(内网不需要 TLS 验证)
  - `HTTP Host Header`: 留空或设置为 `ai.leke.xyz`

## NAS 上安装 Cloudflared

### Synology DSM 安装方式

#### 方法 1: Docker 容器(推荐)
```bash
# 创建配置目录
sudo mkdir -p /volume2/docker/cloudflared

# 运行 cloudflared 容器
sudo docker run -d \
  --name cloudflared \
  --restart always \
  -v /volume2/docker/cloudflared:/home/nonroot/.cloudflared \
  cloudflare/cloudflared:latest \
  tunnel --no-autoupdate run --token <your-tunnel-token>
```

#### 方法 2: 直接安装二进制文件
```bash
# 下载 cloudflared
sudo wget -O /usr/local/bin/cloudflared https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
sudo chmod +x /usr/local/bin/cloudflared

# 使用 tunnel token 运行
cloudflared tunnel --no-autoupdate run --token <your-tunnel-token>
```

### 开机自启动

在 DSM 控制面板设置:
1. **控制面板** → **任务计划**
2. **新增** → **触发的任务** → **用户定义的脚本**
3. **常规设置**:
   - 任务名称: `Cloudflare Tunnel`
   - 用户: `root`
   - 事件: `开机`
4. **任务设置** → **运行命令**:
```bash
# Docker 方式
sudo docker start cloudflared

# 或直接运行(如果使用二进制文件)
nohup /usr/local/bin/cloudflared tunnel --no-autoupdate run --token <your-token> > /var/log/cloudflared.log 2>&1 &
```

## 验证配置

### 测试连接
```bash
# 测试主应用
curl -I https://ai.leke.xyz/health

# 测试 Webhook
curl https://webhook.leke.xyz/health
```

### 查看日志
```bash
# Docker 方式
sudo docker logs -f cloudflared

# 二进制文件方式
tail -f /var/log/cloudflared.log
```

## DNS 记录

Cloudflare Tunnel 会自动创建以下 DNS 记录:
- `ai.leke.xyz` → CNAME → `<tunnel-id>.cfargotunnel.com`
- `webhook.leke.xyz` → CNAME → `<tunnel-id>.cfargotunnel.com`

**无需手动配置 A 记录或开放路由器端口。**

## 安全建议

- ✅ Tunnel 只允许出站连接(从 NAS 到 Cloudflare)
- ✅ 不需要开放防火墙端口
- ✅ 自动 HTTPS(Let's Encrypt)
- ✅ DDoS 防护(Cloudflare 网络)
- ✅ 可配置 Access 策略限制访问

### 可选: 添加访问控制

在 Cloudflare Zero Trust 中为 `ai.leke.xyz` 添加 Access 策略:
1. **Access** → **Applications** → **Add an application**
2. 选择 **Self-hosted**
3. 配置登录方式(Email OTP、GitHub OAuth 等)
4. 设置允许访问的用户

## 故障排查

### Tunnel 无法连接
```bash
# 检查 cloudflared 状态
sudo docker ps | grep cloudflared

# 重启 tunnel
sudo docker restart cloudflared
```

### 502 Bad Gateway
- 检查 NAS 上的服务是否运行: `sudo docker ps | grep xiaole-ai`
- 检查端口映射: `curl http://192.168.88.188:8000/health`
- 查看 cloudflared 日志: `sudo docker logs cloudflared`

### DNS 不生效
- 等待 DNS 传播(最多 5 分钟)
- 清除本地 DNS 缓存: `sudo dscacheutil -flushcache` (macOS)
- 使用 `dig ai.leke.xyz` 检查 DNS 记录

## 相关文档
- [Cloudflare Tunnel 官方文档](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/)
- [Webhook 自动部署](./WEBHOOK_DEPLOY.md)
- [生产环境配置](./PRODUCTION_ENV.md)
