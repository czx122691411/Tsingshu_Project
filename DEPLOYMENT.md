# 会员管理系统生产环境部署指南

## 目录
- [服务器要求](#服务器要求)
- [一、服务器环境准备](#一服务器环境准备)
- [二、后端部署](#二后端部署)
- [三、前端部署](#三前端部署)
- [四、Nginx配置](#四nginx配置)
- [五、HTTPS证书配置](#五https证书配置)
- [六、进程管理配置](#六进程管理配置)
- [七、监控和日志](#七监控和日志)
- [八、备份策略](#八备份策略)
- [九、自动化部署脚本](#九自动化部署脚本)

---

## 服务器要求

### 最低配置
- **CPU**: 2核
- **内存**: 4GB
- **硬盘**: 40GB SSD
- **操作系统**: Ubuntu 20.04 LTS / 22.04 LTS 或 CentOS 7/8

### 推荐配置
- **CPU**: 4核
- **内存**: 8GB
- **硬盘**: 80GB SSD
- **带宽**: 10Mbps及以上

---

## 一、服务器环境准备

### 1.1 更新系统
```bash
# Ubuntu/Debian
sudo apt update && sudo apt upgrade -y

# CentOS
sudo yum update -y
```

### 1.2 安装基础工具
```bash
# Ubuntu/Debian
sudo apt install -y curl wget git vim ufw fail2ban

# CentOS
sudo yum install -y curl wget git vim firewalld fail2ban
```

### 1.3 安装Python 3.10+
```bash
# Ubuntu/Debian
sudo apt install -y python3.10 python3.10-venv python3-pip

# 验证安装
python3 --version
```

### 1.4 安装Node.js 18+
```bash
# 使用NodeSource仓库
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# 验证安装
node --version
npm --version
```

### 1.5 安装PostgreSQL
```bash
# Ubuntu/Debian
sudo apt install -y postgresql postgresql-contrib

# 启动服务
sudo systemctl start postgresql
sudo systemctl enable postgresql

# 创建数据库和用户
sudo -u postgres psql
```

在PostgreSQL命令行中执行：
```sql
-- 创建数据库
CREATE DATABASE memberdb;

-- 创建用户
CREATE USER memberuser WITH ENCRYPTED PASSWORD 'your_strong_password_here';

-- 授权
GRANT ALL PRIVILEGES ON DATABASE memberdb TO memberuser;

-- 退出
\q
```

### 1.6 安装Nginx
```bash
sudo apt install -y nginx
sudo systemctl start nginx
sudo systemctl enable nginx
```

---

## 二、后端部署

### 2.1 创建部署目录
```bash
sudo mkdir -p /var/www/member-management
sudo chown $USER:$USER /var/www/member-management
cd /var/www/member-management
```

### 2.2 上传代码
```bash
# 方式1: 使用git
git clone <your-repo-url> .

# 方式2: 使用scp上传
# scp -r ./member-management/* user@server:/var/www/member-management/
```

### 2.3 配置Python虚拟环境
```bash
cd /var/www/member-management/backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn psycopg2-binary
```

### 2.4 创建环境配置文件
```bash
cd /var/www/member-management/backend
cat > .env << 'EOF'
# Django配置
SECRET_KEY=your-secret-key-here-change-this-in-production
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# 数据库配置
DB_ENGINE=django.db.backends.postgresql
DB_NAME=memberdb
DB_USER=memberuser
DB_PASSWORD=your_strong_password_here
DB_HOST=localhost
DB_PORT=5432

# CORS配置
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# JWT配置
JWT_ACCESS_TOKEN_LIFETIME=60
JWT_REFRESH_TOKEN_LIFETIME=1440
EOF
```

生成安全的SECRET_KEY：
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 2.5 修改Django settings
```bash
cd /var/www/member-management/backend
vim member_management/settings.py
```

添加或修改以下内容：
```python
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 安全配置
SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = os.getenv('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')

# 数据库配置
DATABASES = {
    'default': {
        'ENGINE': os.getenv('DB_ENGINE'),
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
    }
}

# CORS配置
CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS', '').split(',')
CORS_ALLOW_CREDENTIALS = True

# 静态文件和媒体文件
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# 安全中间件（生产环境必须）
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
```

### 2.6 数据库迁移和初始化
```bash
cd /var/www/member-management/backend
source venv/bin/activate

# 收集静态文件
python manage.py collectstatic --noinput

# 运行迁移
python manage.py migrate

# 创建超级管理员
python manage.py createsuperuser

# （可选）加载初始数据
python manage.py loaddata initial_data.json
```

### 2.7 配置防火墙
```bash
# Ubuntu/Debian
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# CentOS
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

---

## 三、前端部署

### 3.1 安装依赖
```bash
cd /var/www/member-management/frontend
npm install
```

### 3.2 配置生产环境变量
```bash
cd /var/www/member-management/frontend
cat > .env.production << 'EOF'
VITE_API_BASE_URL=https://yourdomain.com/api
VITE_APP_TITLE=会员管理系统
EOF
```

### 3.3 修改vite.config.js
```bash
vim vite.config.js
```

确保配置包含：
```javascript
export default defineConfig({
  plugins: [vue()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: false,
    minify: 'terser',
    rollupOptions: {
      output: {
        manualChunks: {
          'element-plus': ['element-plus'],
          'vue-vendor': ['vue', 'vue-router', 'pinia'],
        }
      }
    }
  }
})
```

### 3.4 构建生产版本
```bash
cd /var/www/member-management/frontend
npm run build
```

构建完成后，静态文件将在 `dist` 目录中。

---

## 四、Nginx配置

### 4.1 创建后端Nginx配置
```bash
sudo vim /etc/nginx/sites-available/member-management-api
```

添加以下内容：
```nginx
# 后端API配置
upstream member_backend {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name api.yourdomain.com;

    # 重定向到HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    # SSL证书配置（将在下一步配置）
    ssl_certificate /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # 日志
    access_log /var/log/nginx/member-api-access.log;
    error_log /var/log/nginx/member-api-error.log;

    # Django静态文件
    location /static/ {
        alias /var/www/member-management/backend/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Django媒体文件
    location /media/ {
        alias /var/www/member-management/backend/media/;
        expires 7d;
    }

    # API代理
    location /api/ {
        proxy_pass http://member_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }

    # Django admin
    location /admin/ {
        proxy_pass http://member_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 4.2 创建前端Nginx配置
```bash
sudo vim /etc/nginx/sites-available/member-management-frontend
```

添加以下内容：
```nginx
# 前端配置
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    # 重定向到HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL证书配置
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # 网站根目录
    root /var/www/member-management/frontend/dist;
    index index.html;

    # 日志
    access_log /var/log/nginx/member-frontend-access.log;
    error_log /var/log/nginx/member-frontend-error.log;

    # Gzip压缩
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/json;

    # 静态资源缓存
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Vue Router history模式
    location / {
        try_files $uri $uri/ /index.html;
    }

    # 安全头
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
}
```

### 4.3 启用配置
```bash
# 创建符号链接
sudo ln -s /etc/nginx/sites-available/member-management-api /etc/nginx/sites-enabled/
sudo ln -s /etc/nginx/sites-available/member-management-frontend /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重新加载Nginx
sudo systemctl reload nginx
```

---

## 五、HTTPS证书配置

### 5.1 安装Certbot
```bash
sudo apt install -y certbot python3-certbot-nginx
```

### 5.2 获取SSL证书
```bash
# 前端证书
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# 后端证书
sudo certbot --nginx -d api.yourdomain.com
```

### 5.3 设置自动续期
```bash
# 测试续期
sudo certbot renew --dry-run

# Certbot会自动创建cron任务，证书会自动续期
# 查看定时任务
sudo systemctl list-timers | grep certbot
```

---

## 六、进程管理配置

### 6.1 创建Gunicorn systemd服务
```bash
sudo vim /etc/systemd/system/member-management.service
```

添加以下内容：
```ini
[Unit]
Description=Member Management Django Application
After=network.target postgresql.service

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/var/www/member-management/backend
Environment="PATH=/var/www/member-management/backend/venv/bin"
ExecStart=/var/www/member-management/backend/venv/bin/gunicorn \
          --workers 3 \
          --bind 127.0.0.1:8000 \
          --timeout 120 \
          --access-logfile /var/log/member-management/gunicorn-access.log \
          --error-logfile /var/log/member-management/gunicorn-error.log \
          --log-level info \
          member_management.wsgi:application

ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=30
PrivateTmp=true
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### 6.2 创建日志目录
```bash
sudo mkdir -p /var/log/member-management
sudo chown www-data:www-data /var/log/member-management
```

### 6.3 启动服务
```bash
# 重新加载systemd配置
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start member-management

# 设置开机自启
sudo systemctl enable member-management

# 查看状态
sudo systemctl status member-management

# 查看日志
sudo journalctl -u member-management -f
```

---

## 七、监控和日志

### 7.1 配置日志轮转
```bash
sudo vim /etc/logrotate.d/member-management
```

添加以下内容：
```
/var/log/member-management/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        systemctl reload member-management > /dev/null 2>&1 || true
    endscript
}
```

### 7.2 配置Nginx日志轮转
```bash
sudo vim /etc/logrotate.d/nginx-member
```

添加以下内容：
```
/var/log/nginx/member-*-*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data adm
    sharedscripts
    prerotate
        if [ -d /etc/logrotate.d/httpd-prerotate ]; then \
            run-parts /etc/logrotate.d/httpd-prerotate; \
        fi
    endscript
    postrotate
        invoke-rc.d nginx rotate >/dev/null 2>&1 || true
    endscript
}
```

### 7.3 安装监控工具（可选）
```bash
# 安装htop
sudo apt install -y htop

# 安装netdata（实时监控）
bash <(curl -Ss https://my-netdata.io/kickstart.sh)

# 访问监控面板
# http://your-server-ip:19999
```

---

## 八、备份策略

### 8.1 创建数据库备份脚本
```bash
sudo vim /usr/local/bin/backup-memberdb.sh
```

添加以下内容：
```bash
#!/bin/bash

# 配置
BACKUP_DIR="/var/backups/member-management"
DB_NAME="memberdb"
DB_USER="memberuser"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/db_backup_$TIMESTAMP.sql.gz"

# 创建备份目录
mkdir -p "$BACKUP_DIR"

# 备份数据库
PGPASSWORD="your_db_password" pg_dump -h localhost -U "$DB_USER" "$DB_NAME" | gzip > "$BACKUP_FILE"

# 保留最近7天的备份
find "$BACKUP_DIR" -name "db_backup_*.sql.gz" -mtime +7 -delete

# 记录日志
echo "$(date): Database backup completed: $BACKUP_FILE" >> /var/log/member-management/backup.log
```

设置权限：
```bash
sudo chmod +x /usr/local/bin/backup-memberdb.sh
```

### 8.2 配置定时备份
```bash
# 编辑crontab
sudo crontab -e
```

添加以下内容：
```
# 每天凌晨2点备份数据库
0 2 * * * /usr/local/bin/backup-memberdb.sh

# 每周日凌晨3点备份媒体文件
0 3 * * 0 tar -czf /var/backups/member-management/media_$(date +\%Y\%m\%d).tar.gz /var/www/member-management/backend/media/
```

### 8.3 创建媒体文件备份脚本
```bash
sudo vim /usr/local/bin/backup-media.sh
```

添加以下内容：
```bash
#!/bin/bash

BACKUP_DIR="/var/backups/member-management"
MEDIA_DIR="/var/www/member-management/backend/media"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/media_backup_$TIMESTAMP.tar.gz"

# 创建备份
tar -czf "$BACKUP_FILE" -C "$MEDIA_DIR" .

# 保留最近4周的备份
find "$BACKUP_DIR" -name "media_backup_*.tar.gz" -mtime +28 -delete

echo "$(date): Media backup completed: $BACKUP_FILE" >> /var/log/member-management/backup.log
```

---

## 九、自动化部署脚本

### 9.1 创建一键部署脚本
```bash
vim /var/www/member-management/deploy.sh
```

添加以下内容：
```bash
#!/bin/bash

set -e

echo "========================================="
echo "会员管理系统一键部署脚本"
echo "========================================="

# 配置变量
PROJECT_DIR="/var/www/member-management"
BACKUP_DIR="/var/backups/member-management"
VENV_DIR="$PROJECT_DIR/backend/venv"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 函数：打印成功信息
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

# 函数：打印错误信息
print_error() {
    echo -e "${RED}✗${NC} $1"
}

# 函数：打印警告信息
print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# 1. 备份数据库
echo "正在备份数据库..."
mkdir -p "$BACKUP_DIR"
PGPASSWORD="your_db_password" pg_dump -h localhost -U memberuser memberdb | gzip > "$BACKUP_DIR/pre_deploy_$(date +%Y%m%d_%H%M%S).sql.gz"
print_success "数据库备份完成"

# 2. 拉取最新代码
echo "正在拉取最新代码..."
cd "$PROJECT_DIR"
git pull origin main
print_success "代码更新完成"

# 3. 更新后端依赖
echo "正在更新后端依赖..."
cd "$PROJECT_DIR/backend"
source "$VENV_DIR/bin/activate"
pip install --upgrade pip
pip install -r requirements.txt
print_success "后端依赖更新完成"

# 4. 运行数据库迁移
echo "正在运行数据库迁移..."
python manage.py migrate --noinput
print_success "数据库迁移完成"

# 5. 收集静态文件
echo "正在收集静态文件..."
python manage.py collectstatic --noinput
print_success "静态文件收集完成"

# 6. 更新前端依赖
echo "正在更新前端依赖..."
cd "$PROJECT_DIR/frontend"
npm install
print_success "前端依赖更新完成"

# 7. 构建前端
echo "正在构建前端..."
npm run build
print_success "前端构建完成"

# 8. 重启服务
echo "正在重启服务..."
sudo systemctl reload nginx
sudo systemctl restart member-management
print_success "服务重启完成"

echo ""
echo "========================================="
print_success "部署完成！"
echo "========================================="
```

设置执行权限：
```bash
chmod +x /var/www/member-management/deploy.sh
```

### 9.2 创建回滚脚本
```bash
vim /var/www/member-management/rollback.sh
```

添加以下内容：
```bash
#!/bin/bash

set -e

BACKUP_DIR="/var/backups/member-management"
LATEST_BACKUP=$(ls -t "$BACKUP_DIR"/pre_deploy_*.sql.gz 2>/dev/null | head -1)

if [ -z "$LATEST_BACKUP" ]; then
    echo "错误：未找到备份文件"
    exit 1
fi

echo "正在回滚到备份: $LATEST_BACKUP"

# 恢复数据库
gunzip -c "$LATEST_BACKUP" | psql -h localhost -U memberuser memberdb

# 回滚代码
cd /var/www/member-management
git reset --hard HEAD~1

# 重启服务
sudo systemctl restart member-management

echo "回滚完成"
```

---

## 十、部署后检查清单

部署完成后，请检查以下项目：

- [ ] 后端API可以正常访问（https://api.yourdomain.com/api/）
- [ ] 前端页面可以正常访问（https://yourdomain.com）
- [ ] SSL证书有效且自动续期已配置
- [ ] 数据库连接正常
- [ ] 静态文件和媒体文件可以正常访问
- [ ] 日志文件正常写入
- [ ] 备份脚本正常工作
- [ ] 服务开机自启已设置
- [ ] 防火墙规则已配置
- [ ] Django管理员账户可以登录后台

---

## 十一、性能优化建议

### 11.1 数据库优化
```sql
-- 在PostgreSQL中创建索引
CREATE INDEX idx_activity_start_time ON activities_activity(start_time);
CREATE INDEX idx_participation_registered_at ON activities_activityparticipation(registered_at);
CREATE INDEX idx_member_code ON members_member(code);
```

### 11.2 启用缓存（可选）
```bash
# 安装Redis
sudo apt install -y redis-server

# 在Django中配置缓存
pip install django-redis
```

在settings.py中添加：
```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

### 11.3 Gunicorn优化
根据服务器配置调整worker数量：
```bash
# 计算： (2 x CPU核心数) + 1
# 例如4核CPU：9个worker

# 修改服务配置
ExecStart=/var/www/member-management/backend/venv/bin/gunicorn \
          --workers 9 \
          --worker-class sync \
          --worker-connections 1000 \
          --max-requests 1000 \
          --max-requests-jitter 50 \
          --timeout 120 \
          --bind 127.0.0.1:8000 \
          member_management.wsgi:application
```

---

## 十二、安全加固

### 12.1 配置fail2ban
```bash
sudo vim /etc/fail2ban/jail.local
```

添加以下内容：
```ini
[nginx-http-auth]
enabled = true
port = http,https
logpath = /var/log/nginx/error.log

[nginx-limit-req]
enabled = true
port = http,https
logpath = /var/log/nginx/error.log
maxretry = 10
```

启动fail2ban：
```bash
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### 12.2 设置文件权限
```bash
# 后端
sudo chown -R www-data:www-data /var/www/member-management/backend
sudo chmod -R 755 /var/www/member-management/backend
sudo chmod 600 /var/www/member-management/backend/.env

# 前端
sudo chown -R www-data:www-data /var/www/member-management/frontend/dist
sudo chmod -R 755 /var/www/member-management/frontend/dist
```

---

## 常见问题

### Q1: 端口被占用怎么办？
```bash
# 查看占用端口的进程
sudo lsof -i :8000

# 杀死进程
sudo kill -9 <PID>
```

### Q2: 数据库连接失败？
```bash
# 检查PostgreSQL状态
sudo systemctl status postgresql

# 检查连接
psql -h localhost -U memberuser -d memberdb
```

### Q3: 静态文件404错误？
```bash
# 重新收集静态文件
cd /var/www/member-management/backend
source venv/bin/activate
python manage.py collectstatic --noinput --clear

# 检查Nginx配置
sudo nginx -t
```

---

## 技术支持

如遇到部署问题，请检查以下日志文件：

- **Django日志**: `/var/log/member-management/gunicorn-error.log`
- **Nginx日志**: `/var/log/nginx/member-*-error.log`
- **系统日志**: `sudo journalctl -u member-management -n 50`

---

**部署完成后，建议进行压力测试和安全性扫描，确保系统稳定运行。**
