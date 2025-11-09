# 小乐AI - NAS PostgreSQL 配置指南

## 📋 准备工作

### 1. 确认NAS信息
- **NAS IP地址**: ___________________（填写你的NAS局域网IP）
- **SSH端口**: 22（默认）
- **管理员账号**: admin

### 2. 确认Docker已安装
- 打开群晖DSM → 套件中心
- 搜索"Docker"并安装（如果没装）

---

## 🚀 安装步骤

### 方法A：自动安装（推荐）

**1. SSH连接到NAS**
```bash
# 在Mac终端执行（替换IP地址）
ssh admin@你的NAS_IP
# 输入管理员密码
```

**2. 下载并执行安装脚本**
```bash
# 创建脚本
cat > install_postgresql.sh << 'EOF'
#!/bin/bash

echo "🚀 开始安装PostgreSQL..."

# 拉取镜像
sudo docker pull postgres:13-alpine

# 创建数据目录
sudo mkdir -p /volume1/docker/postgresql/data
sudo chmod 777 /volume1/docker/postgresql/data

# 启动容器
sudo docker run -d \
  --name xiaole-postgresql \
  --restart always \
  -e POSTGRES_PASSWORD=Xiaole2025Admin \
  -e POSTGRES_DB=xiaole_ai \
  -e POSTGRES_USER=xiaole_user \
  -e POSTGRES_INITDB_ARGS="--encoding=UTF8 --locale=C" \
  -p 5432:5432 \
  -v /volume1/docker/postgresql/data:/var/lib/postgresql/data \
  postgres:13-alpine

echo "⏳ 等待PostgreSQL启动..."
sleep 10

echo "✅ PostgreSQL安装完成！"
sudo docker ps | grep xiaole-postgresql

echo ""
echo "数据库信息："
echo "  主机: $(hostname -I | awk '{print $1}')"
echo "  端口: 5432"
echo "  数据库: xiaole_ai"
echo "  用户: xiaole_user"
echo "  密码: Xiaole2025User"
EOF

# 执行脚本
chmod +x install_postgresql.sh
./install_postgresql.sh
```

---

### 方法B：通过群晖Docker界面（图形化）

**1. 打开Docker套件**

**2. 下载镜像**
- 注册表 → 搜索"postgres"
- 选择"postgres:13-alpine"
- 点击下载

**3. 创建容器**
- 映像 → 选择postgres:13-alpine → 启动
- 容器名称: `xiaole-postgresql`
- 勾选"启用自动重新启动"

**4. 高级设置**

**存储空间**：
- 添加文件夹
- 文件夹: docker/postgresql/data
- 装载路径: /var/lib/postgresql/data

**端口设置**：
- 本地端口: 5432
- 容器端口: 5432
- 类型: TCP

**环境变量**：
```
POSTGRES_PASSWORD=Xiaole2025Admin
POSTGRES_DB=xiaole_ai
POSTGRES_USER=xiaole_user
POSTGRES_INITDB_ARGS=--encoding=UTF8 --locale=C
```

**5. 启动容器**

---

## ✅ 安装后验证

**1. 检查容器状态**
```bash
sudo docker ps | grep xiaole-postgresql
# 应该显示容器正在运行
```

**2. 测试数据库连接**
```bash
sudo docker exec xiaole-postgresql psql -U xiaole_user -d xiaole_ai -c "SELECT version();"
# 应该显示PostgreSQL版本信息
```

**3. 查看日志**
```bash
sudo docker logs xiaole-postgresql
# 检查是否有错误
```

---

## 📝 配置信息（记录下来）

安装完成后，把这些信息填写到小乐的配置中：

```
NAS_IP=你的NAS_IP
DB_PORT=5432
DB_NAME=xiaole_ai
DB_USER=xiaole_user
DB_PASSWORD=Xiaole2025User
```

---

## 🔧 常用管理命令

```bash
# 查看容器状态
sudo docker ps | grep xiaole

# 查看日志
sudo docker logs xiaole-postgresql

# 重启容器
sudo docker restart xiaole-postgresql

# 停止容器
sudo docker stop xiaole-postgresql

# 启动容器
sudo docker start xiaole-postgresql

# 进入数据库
sudo docker exec -it xiaole-postgresql psql -U xiaole_user -d xiaole_ai

# 备份数据库
sudo docker exec xiaole-postgresql pg_dump -U xiaole_user xiaole_ai > backup.sql

# 恢复数据库
cat backup.sql | sudo docker exec -i xiaole-postgresql psql -U xiaole_user -d xiaole_ai
```

---

## ❓ 常见问题

**Q: 容器无法启动？**
A: 检查端口5432是否被占用：`sudo netstat -tulpn | grep 5432`

**Q: 连接被拒绝？**
A: 检查防火墙设置，确保5432端口开放

**Q: 数据丢失？**
A: 数据存储在 /volume1/docker/postgresql/data，不会丢失

**Q: 如何修改密码？**
```bash
sudo docker exec -it xiaole-postgresql psql -U postgres
ALTER USER xiaole_user WITH PASSWORD '新密码';
```

---

## 🎯 下一步

安装完成后，告诉我你的**NAS IP地址**，我会帮你：
1. 更新小乐的配置文件
2. 安装PostgreSQL驱动
3. 测试连接
4. 迁移数据到NAS

---

## ✅ 配置完成记录 (2025-11-09)

### 最终配置状态

**使用方案**: NAS 现有 PostgreSQL (非 Docker)

#### 数据库连接信息
- 主机: 192.168.88.188:5432
- 数据库: xiaole_ai
- 用户: xiaole_user
- 密码: Xiaole2025User

#### 关键配置

**1. PostgreSQL 网络配置**
```bash
# /var/services/pgsql/postgresql.conf
listen_addresses = '*'  # 允许网络访问
```

**2. 客户端认证配置**
```bash
# /var/services/pgsql/pg_hba.conf
host    xiaole_ai    xiaole_user    192.168.88.0/24    md5
```

**3. 数据表结构**
```sql
CREATE TABLE memories (
    id SERIAL PRIMARY KEY,
    content TEXT,
    tag VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**4. xiaole-ai 配置 (.env)**
```env
DB_USER=xiaole_user
DB_PASS=Xiaole2025User
DB_HOST=192.168.88.188
DB_PORT=5432
DB_NAME=xiaole_ai
# DATABASE_URL=sqlite:///./xiaole_ai.db  # SQLite已停用
```

### 测试验证

#### NAS 端测试
```bash
# 查看数据
sudo -u postgres psql -d xiaole_ai -c "SELECT * FROM memories;"

# 查看监听状态
sudo netstat -tuln | grep 5432
# 输出: tcp 0 0 0.0.0.0:5432 0.0.0.0:* LISTEN ✅
```

#### Mac 端测试
```bash
# 连接测试
python3 test_final_setup.py

# API 测试
curl -X POST "http://localhost:8000/memory" \
  -H "Content-Type: application/json" \
  -d '{"content":"NAS测试","tag":"test"}'
```

### 配置优势

✅ **数据持久化**: NAS RAID 保护  
✅ **多设备访问**: 局域网设备共享数据库  
✅ **性能提升**: PostgreSQL 并发支持  
✅ **扩展性**: 可添加 pgvector 向量搜索  

### 故障排查命令

```bash
# NAS 端
sudo synoservicectl --status pgsql     # 检查服务状态
sudo synoservicectl --restart pgsql    # 重启服务
sudo tail -f /var/services/pgsql/pg_log/postgresql-*.log  # 查看日志

# Mac 端
python3 test_nas_connection.py         # 测试连接
python3 verify_nas_db.py              # 验证数据库
```

**配置完成！xiaole-ai 现在使用 NAS PostgreSQL。** 🎉
