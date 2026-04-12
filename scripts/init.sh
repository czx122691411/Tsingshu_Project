#!/bin/bash

# 会员管理系统初始化脚本
# 使用方法: sudo bash init.sh

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 配置变量
PROJECT_DIR="/var/www/member-management"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"
VENV_DIR="$BACKEND_DIR/venv"
ENV_FILE="$BACKEND_DIR/.env"
ENV_EXAMPLE="$PROJECT_DIR/.env.example"

# 日志函数
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# 检查是否为root用户
check_root() {
    if [ "$EUID" -ne 0 ]; then
        log_error "请使用root权限或sudo运行此脚本"
        exit 1
    fi
}

# 显示欢迎信息
show_welcome() {
    echo ""
    echo "========================================="
    echo "  会员管理系统 - 初始化向导"
    echo "========================================="
    echo ""
}

# 检查系统依赖
check_dependencies() {
    log_info "检查系统依赖..."

    local missing_deps=()

    # 检查必需的命令
    for cmd in python3 pip3 node npm postgresql; do
        if ! command -v $cmd &> /dev/null; then
            missing_deps+=($cmd)
        fi
    done

    if [ ${#missing_deps[@]} -gt 0 ]; then
        log_error "缺少以下依赖: ${missing_deps[*]}"
        log_info "请先运行: sudo apt install -y python3 python3-pip nodejs npm postgresql postgresql-contrib"
        exit 1
    fi

    log_success "所有依赖已安装"
}

# 创建项目目录
create_directories() {
    log_info "创建项目目录..."

    mkdir -p "$PROJECT_DIR"
    mkdir -p "$BACKEND_DIR/logs"
    mkdir -p "$BACKEND_DIR/media"
    mkdir -p "/var/log/member-management"

    log_success "目录创建完成"
}

# 配置环境变量
configure_env() {
    log_info "配置环境变量..."

    if [ -f "$ENV_FILE" ]; then
        log_warning ".env文件已存在"
        read -p "是否重新配置？(yes/no): " reconfigure

        if [ "$reconfigure" != "yes" ]; then
            log_info "跳过环境配置"
            return 0
        fi
    fi

    # 生成随机密钥
    log_info "生成Django密钥..."
    SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")

    # 收集用户输入
    echo ""
    log_info "请输入配置信息："
    echo ""

    read -p "域名 (例如: example.com): " domain
    read -p "数据库名称 [默认: memberdb]: " db_name
    db_name=${db_name:-memberdb}
    read -p "数据库用户 [默认: memberuser]: " db_user
    db_user=${db_user:-memberuser}
    read -s -p "数据库密码: " db_password
    echo ""
    read -s -p "数据库密码（确认）: " db_password_confirm
    echo ""

    if [ "$db_password" != "$db_password_confirm" ]; then
        log_error "密码不匹配"
        exit 1
    fi

    # 创建.env文件
    cat > "$ENV_FILE" << EOF
# Django配置
SECRET_KEY=$SECRET_KEY
DEBUG=False
ALLOWED_HOSTS=$domain,www.$domain

# 数据库配置
DB_ENGINE=django.db.backends.postgresql
DB_NAME=$db_name
DB_USER=$db_user
DB_PASSWORD=$db_password
DB_HOST=localhost
DB_PORT=5432

# CORS配置
CORS_ALLOWED_ORIGINS=https://$domain,https://www.$domain

# JWT配置
JWT_ACCESS_TOKEN_LIFETIME=60
JWT_REFRESH_TOKEN_LIFETIME=1440
EOF

    chmod 600 "$ENV_FILE"
    log_success "环境配置完成"
}

# 创建数据库
create_database() {
    log_info "创建数据库..."

    source "$ENV_FILE"

    # 检查数据库是否已存在
    if sudo -u postgres psql -lqt | cut -d \| -f 1 | grep -qw "$DB_NAME"; then
        log_warning "数据库 $DB_NAME 已存在"
        read -p "是否删除并重新创建？(yes/no): " recreate

        if [ "$recreate" == "yes" ]; then
            sudo -u postgres psql -c "DROP DATABASE $DB_NAME;"
            sudo -u postgres psql -c "CREATE DATABASE $DB_NAME;"
            log_success "数据库已重新创建"
        fi
    else
        sudo -u postgres psql -c "CREATE DATABASE $DB_NAME;"
        log_success "数据库创建完成"
    fi

    # 创建用户（如果不存在）
    if ! sudo -u postgres psql -t -c "SELECT 1 FROM pg_user WHERE usename = '$DB_USER'" | grep -q 1; then
        sudo -u postgres psql -c "CREATE USER $DB_USER WITH ENCRYPTED PASSWORD '$DB_PASSWORD';"
        sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"
        log_success "数据库用户创建完成"
    else
        sudo -u postgres psql -c "ALTER USER $DB_USER WITH ENCRYPTED PASSWORD '$DB_PASSWORD';"
        log_success "数据库用户密码已更新"
    fi
}

# 配置Python虚拟环境
setup_python_env() {
    log_info "配置Python虚拟环境..."

    if [ ! -d "$VENV_DIR" ]; then
        python3 -m venv "$VENV_DIR"
        log_success "虚拟环境创建完成"
    else
        log_info "虚拟环境已存在"
    fi

    source "$VENV_DIR/bin/activate"

    log_info "安装Python依赖..."
    pip install --upgrade pip setuptools wheel
    pip install -r "$BACKEND_DIR/requirements.txt"
    pip install gunicorn psycopg2-binary

    log_success "Python依赖安装完成"
}

# 配置前端环境
setup_frontend_env() {
    log_info "配置前端环境..."

    cd "$FRONTEND_DIR"

    # 创建前端环境变量
    source "$ENV_FILE"
    cat > .env.production << EOF
VITE_API_BASE_URL=https://${ALLOWED_HOSTS%%,*}/api
VITE_APP_TITLE=会员管理系统
EOF

    log_info "安装前端依赖..."
    npm install

    log_success "前端依赖安装完成"
}

# 初始化数据库
init_database() {
    log_info "初始化数据库..."

    cd "$BACKEND_DIR"
    source "$VENV_DIR/bin/activate"
    source "$ENV_FILE"

    # 运行迁移
    python manage.py migrate --noinput

    # 创建超级用户
    log_info "创建管理员账户..."
    read -p "管理员用户名 [默认: admin]: " admin_user
    admin_user=${admin_user:-admin}
    read -s -p "管理员密码: " admin_password
    echo ""
    read -s -p "管理员密码（确认）: " admin_password_confirm
    echo ""

    if [ "$admin_password" != "$admin_password_confirm" ]; then
        log_error "密码不匹配"
        exit 1
    fi

    # 使用Django命令创建超级用户
    from django.contrib.auth import get_user_model
    User = get_user_model()
    if not User.objects.filter(username='$admin_user').exists():
        User.objects.create_superuser('$admin_user', 'admin@$domain', '$admin_password')
    else:
        print('管理员账户已存在')

    python manage.py createsuperuser \
        --username "$admin_user" \
        --email "admin@$domain" \
        --noinput || true

    # 收集静态文件
    log_info "收集静态文件..."
    python manage.py collectstatic --noinput

    log_success "数据库初始化完成"
}

# 设置文件权限
set_permissions() {
    log_info "设置文件权限..."

    chown -R www-data:www-data "$PROJECT_DIR"
    chmod -R 755 "$PROJECT_DIR"
    chmod 600 "$ENV_FILE"

    log_success "文件权限设置完成"
}

# 配置系统服务
setup_services() {
    log_info "配置系统服务..."

    # 复制systemd服务文件
    if [ -f "$PROJECT_DIR/configs/member-management.service" ]; then
        cp "$PROJECT_DIR/configs/member-management.service" /etc/systemd/system/
        systemctl daemon-reload
        systemctl enable member-management
        log_success "Django服务已配置"
    fi

    # 配置Nginx
    if [ -f "$PROJECT_DIR/configs/nginx-member-management.conf" ]; then
        cp "$PROJECT_DIR/configs/nginx-member-management.conf" /etc/nginx/sites-available/member-management
        ln -sf /etc/nginx/sites-available/member-management /etc/nginx/sites-enabled/
        nginx -t && systemctl reload nginx
        log_success "Nginx配置已完成"
    fi
}

# 设置防火墙
setup_firewall() {
    log_info "配置防火墙..."

    if command -v ufw &> /dev/null; then
        ufw allow 22/tcp
        ufw allow 80/tcp
        ufw allow 443/tcp
        ufw --force enable
        log_success "UFW防火墙配置完成"
    elif command -v firewall-cmd &> /dev/null; then
        firewall-cmd --permanent --add-service=ssh
        firewall-cmd --permanent --add-service=http
        firewall-cmd --permanent --add-service=https
        firewall-cmd --reload
        log_success "firewalld防火墙配置完成"
    else
        log_warning "未找到防火墙工具"
    fi
}

# 配置SSL证书
setup_ssl() {
    log_info "配置SSL证书..."

    source "$ENV_FILE"
    domain=${ALLOWED_HOSTS%%,*}

    if command -v certbot &> /dev/null; then
        certbot --nginx -d "$domain" -d "www.$domain" --non-interactive --agree-tos --email "admin@$domain"
        log_success "SSL证书配置完成"
    else
        log_warning "Certbot未安装，请手动安装: sudo apt install certbot python3-certbot-nginx"
    fi
}

# 创建备份脚本
setup_backup() {
    log_info "配置自动备份..."

    # 复制备份脚本
    if [ -f "$PROJECT_DIR/scripts/backup.sh" ]; then
        cp "$PROJECT_DIR/scripts/backup.sh" /usr/local/bin/member-backup.sh"
        chmod +x /usr/local/bin/member-backup.sh"
    fi

    # 添加定时任务
    (crontab -l 2>/dev/null; echo "0 2 * * * /usr/local/bin/member-backup.sh") | crontab -

    log_success "自动备份配置完成"
}

# 显示完成信息
show_completion() {
    echo ""
    echo "========================================="
    log_success "初始化完成！"
    echo "========================================="
    echo ""
    echo "项目目录: $PROJECT_DIR"
    echo "后端目录: $BACKEND_DIR"
    echo "前端目录: $FRONTEND_DIR"
    echo ""
    echo "下一步操作："
    echo "  1. 启动服务: sudo systemctl start member-management"
    echo "  2. 查看状态: sudo systemctl status member-management"
    echo "  3. 查看日志: sudo journalctl -u member-management -f"
    echo "  4. 配置SSL: sudo bash $PROJECT_DIR/scripts/setup-ssl.sh"
    echo ""
    echo "========================================="
}

# 主函数
main() {
    show_welcome
    check_root
    check_dependencies
    create_directories
    configure_env
    create_database
    setup_python_env
    setup_frontend_env
    init_database
    set_permissions
    setup_services
    setup_firewall

    echo ""
    read -p "是否现在配置SSL证书？(yes/no): " setup_ssl_now

    if [ "$setup_ssl_now" == "yes" ]; then
        setup_ssl
    fi

    read -p "是否配置自动备份？(yes/no): " setup_backup_now

    if [ "$setup_backup_now" == "yes" ]; then
        setup_backup
    fi

    show_completion
}

# 捕获错误
trap 'log_error "初始化失败！"; exit 1' ERR

# 运行主函数
main "$@"
