# 群晖 NAS PostgreSQL 重启指南

## 方法 1: 通过 DSM 图形界面 (推荐)

1. 登录群晖 DSM 管理界面 (http://192.168.88.188:5000)
2. 打开 **套件中心**
3. 找到 **PostgreSQL** 套件
4. 点击套件,选择 **停止** 然后 **启动**

## 方法 2: 通过命令行 (SSH)

### 使用 synopkg 命令
```bash
# SSH 登录 NAS
ssh admin@192.168.88.188

# 停止 PostgreSQL
sudo synopkg stop pgsql

# 启动 PostgreSQL  
sudo synopkg start pgsql

# 重启 PostgreSQL
sudo synopkg restart pgsql

# 查看状态
sudo synopkg status pgsql
```

### 使用 systemctl 命令 (DSM 7.x)
```bash
# 重启服务
sudo systemctl restart postgresql

# 或者
sudo systemctl restart pgsql

# 查看状态
sudo systemctl status postgresql
```

## 方法 3: 修改 pg_hba.conf 后重载配置

如果只是修改了配置文件,不需要完全重启:

```bash
# 重载配置 (不中断现有连接)
sudo su - postgres -c "pg_ctl reload -D /volume1/pgsql"
```

## 修复 Docker 连接问题的完整步骤

```bash
# 1. SSH 登录 NAS
ssh admin@192.168.88.188

# 2. 编辑 pg_hba.conf
sudo vi /volume1/pgsql/pg_hba.conf

# 3. 在文件末尾添加 (允许 Docker 网络访问):
host    xiaole_ai    xiaole_user    172.17.0.0/16    md5
host    all          all            172.17.0.0/16    md5

# 4. 保存后重启 PostgreSQL
sudo synopkg restart pgsql

# 5. 验证配置
psql -U postgres -c "SELECT * FROM pg_hba_file_rules;"
```

## 常见问题排查

### 检查 PostgreSQL 是否运行
```bash
ps aux | grep postgres
netstat -tuln | grep 5432
```

### 查看 PostgreSQL 日志
```bash
# 群晖 PostgreSQL 日志位置
tail -f /volume1/pgsql/pg_log/postgresql-*.log
# 或
tail -f /var/log/postgresql.log
```

### 测试数据库连接
```bash
# 从 NAS 本地测试
psql -U xiaole_user -d xiaole_ai -h localhost

# 从 Docker 容器测试
docker exec -it xiaole-backend psql -U xiaole_user -d xiaole_ai -h 192.168.88.188
```

## 注意事项

1. **权限**: 大部分命令需要 `sudo` 或 `admin` 权限
2. **数据目录**: 群晖默认在 `/volume1/pgsql` 或 `/volume2/pgsql`
3. **端口**: 默认 5432,确保防火墙开放
4. **备份**: 修改配置前建议备份 `pg_hba.conf`

## 快速命令参考

```bash
# 一键重启
ssh admin@192.168.88.188 "sudo synopkg restart pgsql"

# 检查是否成功启动
ssh admin@192.168.88.188 "sudo synopkg status pgsql"
```
