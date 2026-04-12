# 会员管理系统 - 快速部署指南

本指南将帮助您快速部署会员管理系统到生产环境。

## 部署方式概览

我们提供三种部署方式：

1. **传统部署** - 使用systemd + Nginx（推荐用于小型项目）
2. **Docker部署** - 使用Docker Compose（推荐用于快速部署）
3. **云平台部署** - 部署到云服务（如阿里云、腾讯云）

---

## 方式一：传统部署（推荐）

### 前置要求

- Ubuntu 20.04+ / CentOS 7+
- Python 3.10+
- Node.js 18+
- PostgreSQL 13+
- Nginx

### 一键初始化

```bash
# 1. 下载项目
cd /var/www
git clone <your-repo-url> member-management
cd member-management

# 2. 运行初始化脚本
sudo bash scripts/init.sh

# 3. 按提示输入配置信息
#    - 域名
#    - 数据库信息
#    - 管理员账户

# 4. 启动服务
sudo systemctl start member-management
```

### 手动部署步骤

如果需要更多控制，可以手动执行以下步骤：

#### 1. 安装系统依赖

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装Python
sudo apt install -y python3.10 python3-pip python3-venv

# 安装Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# 安装PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# 安装Nginx
sudo apt install -y nginx
```

#### 2. 配置数据库

```bash
# 创建数据库和用户
sudo -u postgres psql
```

```sql
CREATE DATABASE memberdb;
CREATE USER memberuser WITH ENCRYPTED PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE memberdb TO memberuser;
\q
```

#### 3. 配置后端

```bash
cd /var/www/member-management/backend

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
pip install gunicorn psycopg2-binary

# 配置环境变量
cp ../.env.example .env
vim .env  # 修改配置

# 运行迁移
python manage.py migrate

# 创建超级用户
python manage.py createsuperuser

# 收集静态文件
python manage.py collectstatic --noinput
```

#### 4. 配置前端

```bash
cd /var/www/member-management/frontend

# 安装依赖
npm install

# 构建生产版本
npm run build
```

#### 5. 配置Nginx

```bash
# 复制配置文件
sudo cp configs/nginx-member-management.conf /etc/nginx/sites-available/member-management

# 创建符号链接
sudo ln -s /etc/nginx/sites-available/member-management /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重新加载Nginx
sudo systemctl reload nginx
```

#### 6. 配置系统服务

```bash
# 复制服务文件
sudo cp configs/member-management.service /etc/systemd/system/

# 重新加载systemd
sudo systemctl daemon-reload

# 启用服务
sudo systemctl enable member-management

# 启动服务
sudo systemctl start member-management
```

#### 7. 配置SSL证书

```bash
# 安装Certbot
sudo apt install -y certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

---

## 方式二：Docker部署

### 前置要求

- Docker 20.10+
- Docker Compose 2.0+

### 快速开始

```bash
# 1. 克隆项目
git clone <your-repo-url> member-management
cd member-management

# 2. 配置环境变量
cp .env.example .env
vim .env  # 修改配置

# 3. 启动所有服务
docker-compose up -d

# 4. 查看日志
docker-compose logs -f

# 5. 初始化数据库
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser
```

### Docker管理命令

```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 查看日志
docker-compose logs -f [service_name]

# 进入容器
docker-compose exec backend bash

# 更新服务
docker-compose pull
docker-compose up -d --build

# 查看状态
docker-compose ps
```

---

## 方式三：云平台部署

### 阿里云部署

#### 使用ECS + RDS

1. **购买ECS实例**
   - 选择Ubuntu 20.04
   - 配置：2核4GB起步
   - 带宽：按需选择

2. **购买RDS PostgreSQL**
   - 选择主备实例
   - 存储空间：20GB起步

3. **配置负载均衡（可选）**
   - 购买SLB实例
   - 配置健康检查

4. **部署应用**
   - 按照传统部署步骤操作
   - 使用RDS连接地址替换localhost

#### 使用容器服务

1. **购买ACK集群**
   - 选择托管版
   - 节点配置按需选择

2. **配置镜像仓库**
   - 使用阿里云容器镜像服务

3. **部署应用**
   ```bash
   # 构建镜像
   docker build -t registry.cn-hangzhou.aliyuncs.com/your-namespace/member-backend:latest .

   # 推送镜像
   docker push registry.cn-hangzhou.aliyuncs.com/your-namespace/member-backend:latest

   # 使用kubectl部署
   kubectl apply -f k8s/
   ```

### 腾讯云部署

#### 使用CVM + TencentDB

1. **购买CVM实例**
   - 选择Ubuntu 20.04
   - 配置：2核4GB起步

2. **购买TencentDB for PostgreSQL**
   - 选择主备实例
   - 存储空间：20GB起步

3. **部署应用**
   - 与阿里云ECS部署类似
   - 使用TencentDB连接地址

---

## 部署后检查清单

部署完成后，请检查以下项目：

- [ ] 后端API可以正常访问（https://api.yourdomain.com/api/）
- [ ] 前端页面可以正常访问（https://yourdomain.com）
- [ ] SSL证书有效
- [ ] 数据库连接正常
- [ ] 静态文件和媒体文件可以正常访问
- [ ] 管理员后台可以登录（https://api.yourdomain.com/admin/）
- [ ] 日志文件正常写入
- [ ] 备份脚本正常工作
- [ ] 服务开机自启已设置
- [ ] 防火墙规则已配置

---

## 常用命令

### 服务管理

```bash
# 查看服务状态
sudo systemctl status member-management

# 启动服务
sudo systemctl start member-management

# 停止服务
sudo systemctl stop member-management

# 重启服务
sudo systemctl restart member-management

# 查看日志
sudo journalctl -u member-management -f
```

### Nginx管理

```bash
# 测试配置
sudo nginx -t

# 重新加载配置
sudo systemctl reload nginx

# 重启服务
sudo systemctl restart nginx
```

### 数据库管理

```bash
# 连接数据库
psql -h localhost -U memberuser -d memberdb

# 备份数据库
pg_dump -h localhost -U memberuser memberdb > backup.sql

# 恢复数据库
psql -h localhost -U memberuser memberdb < backup.sql
```

### 部署相关

```bash
# 一键部署
sudo bash scripts/deploy.sh

# 备份数据
sudo bash scripts/backup.sh

# 回滚版本
sudo bash scripts/rollback.sh
```

---

## 性能优化建议

### 1. 数据库优化

```sql
-- 创建索引
CREATE INDEX idx_activity_start_time ON activities_activity(start_time);
CREATE INDEX idx_participation_registered_at ON activities_activityparticipation(registered_at);
CREATE INDEX idx_member_code ON members_member(code);

-- 配置连接池
-- 修改PostgreSQL配置
max_connections = 100
shared_buffers = 256MB
effective_cache_size = 1GB
```

### 2. 应用优化

```python
# 使用缓存
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}

# 使用CDN（可选）
# 静态文件上传到阿里云OSS或腾讯云COS
```

### 3. Nginx优化

```nginx
# 启用Gzip压缩
gzip on;
gzip_comp_level 6;
gzip_types text/plain text/css application/json;

# 配置缓存
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=my_cache:10m;
```

---

## 监控和维护

### 日志监控

```bash
# 实时查看应用日志
sudo tail -f /var/log/member-management/gunicorn-error.log

# 查看Nginx访问日志
sudo tail -f /var/log/nginx/member-frontend-access.log

# 查看系统日志
sudo journalctl -f
```

### 数据备份

```bash
# 手动备份
sudo bash /usr/local/bin/member-backup.sh

# 查看备份
ls -lh /var/backups/member-management/
```

### 性能监控

推荐使用以下工具：

- **Netdata** - 实时系统监控
- **Prometheus + Grafana** - 应用性能监控
- **Sentry** - 错误追踪

---

## 故障排查

### 常见问题

**问题1：服务无法启动**

```bash
# 查看详细错误
sudo journalctl -u member-management -n 50

# 检查配置
sudo nginx -t
```

**问题2：数据库连接失败**

```bash
# 检查PostgreSQL状态
sudo systemctl status postgresql

# 测试连接
psql -h localhost -U memberuser -d memberdb
```

**问题3：静态文件404**

```bash
# 重新收集静态文件
cd /var/www/member-management/backend
source venv/bin/activate
python manage.py collectstatic --noinput --clear
```

**问题4：SSL证书问题**

```bash
# 重新获取证书
sudo certbot --nginx -d yourdomain.com --force-renewal

# 检查证书状态
sudo certbot certificates
```

---

## 技术支持

如遇到问题，请查看：

1. 详细部署文档：`DEPLOYMENT.md`
2. API文档：`https://api.yourdomain.com/api/docs/`
3. Django日志：`/var/log/member-management/`
4. Nginx日志：`/var/log/nginx/`

---

## 安全建议

1. **定期更新系统**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. **配置防火墙**
   ```bash
   sudo ufw enable
   sudo ufw status
   ```

3. **定期备份数据**
   - 配置自动备份（每天凌晨2点）
   - 定期测试恢复流程

4. **监控异常**
   - 设置日志告警
   - 配置Sentry错误追踪

5. **使用HTTPS**
   - 强制HTTPS重定向
   - 配置HSTS头

---

**部署完成后，建议进行压力测试和安全扫描，确保系统稳定运行。**
