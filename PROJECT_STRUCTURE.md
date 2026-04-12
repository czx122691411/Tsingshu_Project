# 会员管理系统 - 部署文件说明

## 项目结构

```
member-management/
├── backend/                   # Django后端
│   ├── apps/                 # 应用模块
│   ├── member_management/    # 项目配置
│   ├── manage.py            # Django管理脚本
│   ├── requirements.txt     # Python依赖
│   └── venv/                # 虚拟环境（创建后）
├── frontend/                 # Vue前端
│   ├── src/                 # 源代码
│   ├── package.json         # Node依赖
│   └── dist/                # 构建输出（创建后）
├── scripts/                  # 部署脚本
│   ├── init.sh              # 初始化脚本
│   ├── deploy.sh            # 部署脚本
│   ├── backup.sh            # 备份脚本
│   └── rollback.sh          # 回滚脚本
├── configs/                  # 配置文件
│   ├── member-management.service  # systemd服务配置
│   └── nginx-member-management.conf # Nginx配置
├── docker/                   # Docker配置
│   ├── Dockerfile.backend   # 后端Docker镜像
│   ├── Dockerfile.frontend  # 前端Docker镜像
│   └── docker-compose.yml   # Docker Compose配置
├── .env.example              # 环境变量示例
├── DEPLOYMENT.md             # 完整部署文档
├── QUICK_START.md            # 快速入门指南
└── README.md                 # 项目说明
```

## 部署脚本说明

### 1. 初始化脚本 (scripts/init.sh)

**用途**：一键初始化整个系统环境

**功能**：
- 检查系统依赖
- 创建项目目录
- 配置环境变量
- 创建数据库
- 安装Python依赖
- 安装前端依赖
- 初始化数据库
- 配置系统服务
- 配置防火墙
- 配置SSL证书（可选）
- 配置自动备份（可选）

**使用方法**：
```bash
sudo bash scripts/init.sh
```

### 2. 部署脚本 (scripts/deploy.sh)

**用途**：一键更新部署

**功能**：
- 备份当前数据库
- 拉取最新代码
- 更新Python依赖
- 运行数据库迁移
- 收集静态文件
- 构建前端
- 重启服务
- 运行测试
- 清理旧文件

**使用方法**：
```bash
# 生产环境部署
sudo bash scripts/deploy.sh

# 开发环境部署
sudo bash scripts/deploy.sh dev
```

### 3. 备份脚本 (scripts/backup.sh)

**用途**：自动备份数据库和文件

**功能**：
- 备份数据库
- 备份媒体文件
- 备份配置文件
- 清理过期备份
- 显示备份统计

**使用方法**：
```bash
# 备份所有
sudo bash scripts/backup.sh

# 仅备份数据库
sudo bash scripts/backup.sh --db-only

# 仅备份媒体文件
sudo bash scripts/backup.sh --media-only

# 仅备份配置文件
sudo bash scripts/backup.sh --config-only
```

### 4. 回滚脚本 (scripts/rollback.sh)

**用途**：回滚到之前的版本

**功能**：
- 列出可用备份
- 恢复数据库
- 恢复媒体文件
- 恢复配置文件
- 回滚代码提交

**使用方法**：
```bash
# 列出可用备份
sudo bash scripts/rollback.sh --list

# 恢复指定数据库备份
sudo bash scripts/rollback.sh --db /var/backups/member-management/db_backup_20240101_120000.sql.gz

# 恢复指定媒体文件备份
sudo bash scripts/rollback.sh --media /var/backups/member-management/media_backup_20240101_120000.tar.gz

# 回滚代码（回滚1个提交）
sudo bash scripts/rollback.sh --code 1

# 完整回滚
sudo bash scripts/rollback.sh /var/backups/member-management/db_backup_20240101_120000.sql.gz
```

## 配置文件说明

### 1. systemd服务配置 (configs/member-management.service)

**用途**：定义Django应用的系统服务

**配置项**：
- 工作目录
- 环境变量
- Gunicorn启动参数
- 日志文件位置
- 资源限制
- 重启策略

**安装方法**：
```bash
sudo cp configs/member-management.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable member-management
```

### 2. Nginx配置 (configs/nginx-member-management.conf)

**用途**：配置Nginx反向代理

**配置项**：
- 上游服务器配置
- SSL/TLS配置
- 静态文件服务
- API代理
- 安全头设置
- 限流配置

**安装方法**：
```bash
sudo cp configs/nginx-member-management.conf /etc/nginx/sites-available/member-management
sudo ln -s /etc/nginx/sites-available/member-management /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Docker配置说明

### 1. 后端Dockerfile (docker/Dockerfile.backend)

**用途**：构建Django后端Docker镜像

**特性**：
- 多阶段构建
- 非root用户运行
- 健康检查
- 静态文件收集

### 2. 前端Dockerfile (docker/Dockerfile.frontend)

**用途**：构建Vue前端Docker镜像

**特性**：
- 多阶段构建
- Nginx Alpine镜像
- 静态资源优化
- 健康检查

### 3. Docker Compose (docker/docker-compose.yml)

**用途**：定义完整的服务栈

**服务**：
- PostgreSQL数据库
- Redis缓存
- Django后端
- Vue前端
- Nginx反向代理
- Prometheus监控
- Grafana仪表盘

**使用方法**：
```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止所有服务
docker-compose down
```

## 环境变量说明

### 必需配置

- `SECRET_KEY`: Django密钥
- `DB_NAME`: 数据库名称
- `DB_USER`: 数据库用户
- `DB_PASSWORD`: 数据库密码
- `ALLOWED_HOSTS`: 允许的主机

### 可选配置

- `DEBUG`: 调试模式（生产环境设为False）
- `CORS_ALLOWED_ORIGINS`: CORS允许的源
- `EMAIL_HOST`: 邮件服务器
- `USE_S3`: 是否使用S3存储
- `REDIS_HOST`: Redis主机

## 部署文档说明

### 1. 完整部署文档 (DEPLOYMENT.md)

**内容**：
- 服务器要求
- 环境准备
- 后端部署步骤
- 前端部署步骤
- Nginx配置
- HTTPS证书配置
- 进程管理配置
- 监控和日志
- 备份策略
- 自动化部署脚本
- 性能优化
- 安全加固

**适用对象**：需要全面了解部署过程的运维人员

### 2. 快速入门指南 (QUICK_START.md)

**内容**：
- 三种部署方式概览
- 传统部署快速步骤
- Docker部署快速步骤
- 云平台部署指南
- 部署后检查清单
- 常用命令
- 故障排查

**适用对象**：需要快速上手的开发人员

## 部署流程

### 首次部署

1. **准备服务器**
   ```bash
   # 更新系统
   sudo apt update && sudo apt upgrade -y
   ```

2. **运行初始化脚本**
   ```bash
   cd /var/www/member-management
   sudo bash scripts/init.sh
   ```

3. **配置SSL证书**
   ```bash
   sudo certbot --nginx -d yourdomain.com
   ```

4. **验证部署**
   - 访问前端：https://yourdomain.com
   - 访问后端：https://api.yourdomain.com/api/
   - 访问后台：https://api.yourdomain.com/admin/

### 日常更新

1. **拉取代码**
   ```bash
   cd /var/www/member-management
   git pull origin main
   ```

2. **运行部署脚本**
   ```bash
   sudo bash scripts/deploy.sh
   ```

3. **验证更新**
   ```bash
   sudo systemctl status member-management
   ```

### 备份恢复

1. **手动备份**
   ```bash
   sudo bash scripts/backup.sh
   ```

2. **恢复备份**
   ```bash
   sudo bash scripts/rollback.sh --list
   sudo bash scripts/rollback.sh /path/to/backup.sql.gz
   ```

## 监控和维护

### 日志位置

- Django应用：`/var/log/member-management/`
- Nginx访问：`/var/log/nginx/member-*-access.log`
- Nginx错误：`/var/log/nginx/member-*-error.log`
- 系统日志：`sudo journalctl -u member-management`

### 备份位置

- 数据库备份：`/var/backups/member-management/db_backup_*.sql.gz`
- 媒体备份：`/var/backups/member-management/media_backup_*.tar.gz`
- 配置备份：`/var/backups/member-management/config_backup_*.tar.gz`

### 常用维护命令

```bash
# 查看服务状态
sudo systemctl status member-management

# 重启服务
sudo systemctl restart member-management

# 查看日志
sudo journalctl -u member-management -f

# 清理日志
sudo journalctl --vacuum-time=7d

# 检查磁盘空间
df -h

# 检查内存使用
free -h
```

## 安全建议

1. **定期更新**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. **配置防火墙**
   ```bash
   sudo ufw enable
   sudo ufw status
   ```

3. **定期备份**
   - 设置自动备份（crontab）
   - 测试恢复流程

4. **监控异常**
   - 配置日志告警
   - 使用Sentry追踪错误

5. **使用HTTPS**
   - 配置SSL证书
   - 强制HTTPS重定向

## 技术支持

如有问题，请查看：
- 完整文档：`DEPLOYMENT.md`
- 快速指南：`QUICK_START.md`
- 日志文件：`/var/log/member-management/`
- API文档：`https://api.yourdomain.com/api/docs/`

---

**部署完成后，请务必进行压力测试和安全扫描！**
