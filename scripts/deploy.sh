#!/bin/bash

# 会员管理系统一键部署脚本
# 使用方法: sudo bash deploy.sh [environment]
# environment: dev|staging|production (默认: production)

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 配置变量
ENVIRONMENT=${1:-production}
PROJECT_DIR="/var/www/member-management"
BACKUP_DIR="/var/backups/member-management"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"
VENV_DIR="$BACKEND_DIR/venv"

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

# 备份数据库
backup_database() {
    log_info "正在备份数据库..."
    mkdir -p "$BACKUP_DIR"

    if [ -f "$BACKEND_DIR/.env" ]; then
        source "$BACKEND_DIR/.env"
        TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
        BACKUP_FILE="$BACKUP_DIR/db_backup_${TIMESTAMP}.sql.gz"

        if PGPASSWORD="$DB_PASSWORD" pg_dump -h localhost -U "$DB_USER" "$DB_NAME" 2>/dev/null | gzip > "$BACKUP_FILE"; then
            log_success "数据库备份完成: $BACKUP_FILE"

            # 保留最近7天的备份
            find "$BACKUP_DIR" -name "db_backup_*.sql.gz" -mtime +7 -delete
        else
            log_warning "数据库备份失败，继续部署..."
        fi
    else
        log_warning "未找到.env文件，跳过数据库备份"
    fi
}

# 更新后端代码
update_backend() {
    log_info "正在更新后端代码..."

    cd "$BACKEND_DIR"

    # 拉取最新代码
    if [ -d ".git" ]; then
        git pull origin main || git pull origin master
        log_success "代码更新完成"
    else
        log_warning "不是git仓库，跳过代码更新"
    fi

    # 激活虚拟环境
    if [ ! -d "$VENV_DIR" ]; then
        log_info "创建Python虚拟环境..."
        python3 -m venv "$VENV_DIR"
    fi

    source "$VENV_DIR/bin/activate"

    # 更新依赖
    log_info "正在安装Python依赖..."
    pip install --upgrade pip setuptools wheel
    pip install -r requirements.txt
    pip install gunicorn psycopg2-binary

    # 运行迁移
    log_info "正在运行数据库迁移..."
    python manage.py migrate --noinput

    # 收集静态文件
    log_info "正在收集静态文件..."
    python manage.py collectstatic --noinput --clear

    log_success "后端更新完成"
}

# 更新前端代码
update_frontend() {
    log_info "正在更新前端代码..."

    cd "$FRONTEND_DIR"

    # 拉取最新代码
    if [ -d ".git" ]; then
        git pull origin main || git pull origin master
    fi

    # 安装依赖
    log_info "正在安装前端依赖..."
    npm install

    # 构建生产版本
    log_info "正在构建前端..."
    npm run build

    log_success "前端更新完成"
}

# 重启服务
restart_services() {
    log_info "正在重启服务..."

    # 重新加载Nginx
    systemctl reload nginx

    # 重启Django服务
    systemctl restart member-management

    # 等待服务启动
    sleep 3

    # 检查服务状态
    if systemctl is-active --quiet member-management; then
        log_success "Django服务运行正常"
    else
        log_error "Django服务启动失败"
        systemctl status member-management --no-pager
        exit 1
    fi

    if systemctl is-active --quiet nginx; then
        log_success "Nginx服务运行正常"
    else
        log_error "Nginx服务启动失败"
        systemctl status nginx --no-pager
        exit 1
    fi
}

# 运行测试
run_tests() {
    log_info "正在运行测试..."

    cd "$BACKEND_DIR"
    source "$VENV_DIR/bin/activate"

    # 运行Django检查
    python manage.py check --deploy 2>/dev/null || log_warning "Django部署检查发现警告"

    # 运行测试（如果有）
    if [ -f "manage.py" ] && grep -q "test" manage.py; then
        python manage.py test || log_warning "部分测试失败"
    fi

    log_success "测试完成"
}

# 清理旧文件
cleanup() {
    log_info "正在清理旧文件..."

    # 清理Python缓存
    find "$BACKEND_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find "$BACKEND_DIR" -type f -name "*.pyc" -delete 2>/dev/null || true

    # 清理npm缓存
    npm cache clean --force 2>/dev/null || true

    # 清理旧备份（保留最近30天）
    find "$BACKUP_DIR" -name "db_backup_*.sql.gz" -mtime +30 -delete 2>/dev/null || true

    log_success "清理完成"
}

# 显示部署信息
show_info() {
    echo ""
    echo "========================================"
    log_success "部署完成！"
    echo "========================================"
    echo ""
    echo "环境: $ENVIRONMENT"
    echo "项目目录: $PROJECT_DIR"
    echo "备份目录: $BACKUP_DIR"
    echo ""
    echo "服务状态:"
    echo "  Django: $(systemctl is-active member-management)"
    echo "  Nginx: $(systemctl is-active nginx)"
    echo ""
    echo "日志查看:"
    echo "  Django: sudo journalctl -u member-management -f"
    echo "  Nginx: sudo tail -f /var/log/nginx/member-*-error.log"
    echo ""
    echo "========================================"
}

# 主函数
main() {
    log_info "开始部署会员管理系统..."
    log_info "环境: $ENVIRONMENT"
    echo ""

    check_root
    backup_database
    update_backend
    update_frontend
    restart_services
    run_tests
    cleanup
    show_info
}

# 捕获错误
trap 'log_error "部署失败！"; exit 1' ERR

# 运行主函数
main "$@"
