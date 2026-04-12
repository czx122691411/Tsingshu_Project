#!/bin/bash

# 会员管理系统回滚脚本
# 使用方法: sudo bash rollback.sh [backup_file]

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 配置变量
PROJECT_DIR="/var/www/member-management"
BACKUP_DIR="/var/backups/member-management"
BACKEND_DIR="$PROJECT_DIR/backend"
LOG_FILE="/var/log/member-management/rollback.log"

# 日志函数
log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1" | tee -a "$LOG_FILE"
}

# 列出可用备份
list_backups() {
    echo ""
    echo "========================================="
    echo "可用备份列表"
    echo "========================================="
    echo ""

    echo "数据库备份:"
    ls -lht "$BACKUP_DIR"/db_backup_*.sql.gz 2>/dev/null | head -10 | awk '{print $9, $5, $6, $7, $8}' || echo "  无备份"

    echo ""
    echo "媒体文件备份:"
    ls -lht "$BACKUP_DIR"/media_backup_*.tar.gz 2>/dev/null | head -10 | awk '{print $9, $5, $6, $7, $8}' || echo "  无备份"

    echo ""
    echo "配置文件备份:"
    ls -lht "$BACKUP_DIR"/config_backup_*.tar.gz 2>/dev/null | head -10 | awk '{print $9, $5, $6, $7, $8}' || echo "  无备份"

    echo ""
    echo "========================================="
}

# 恢复数据库
restore_database() {
    local backup_file="$1"

    log "开始恢复数据库..."

    if [ ! -f "$backup_file" ]; then
        log_error "备份文件不存在: $backup_file"
        return 1
    fi

    if [ ! -f "$BACKEND_DIR/.env" ]; then
        log_error "未找到.env文件"
        return 1
    fi

    source "$BACKEND_DIR/.env"

    # 确认操作
    log_warning "即将用以下备份恢复数据库: $backup_file"
    read -p "确认继续？(yes/no): " confirm

    if [ "$confirm" != "yes" ]; then
        log "操作已取消"
        return 0
    fi

    # 先备份当前数据库
    log "备份当前数据库..."
    local current_backup="$BACKUP_DIR/before_restore_$(date +%Y%m%d_%H%M%S).sql.gz"
    PGPASSWORD="$DB_PASSWORD" pg_dump -h localhost -U "$DB_USER" "$DB_NAME" | gzip > "$current_backup"
    log "当前数据库已备份到: $current_backup"

    # 恢复数据库
    log "正在恢复数据库..."
    if gunzip -c "$backup_file" | PGPASSWORD="$DB_PASSWORD" psql -h localhost -U "$DB_USER" "$DB_NAME"; then
        log "数据库恢复成功"
    else
        log_error "数据库恢复失败"

        # 尝试恢复原数据库
        log "尝试恢复原数据库..."
        gunzip -c "$current_backup" | PGPASSWORD="$DB_PASSWORD" psql -h localhost -U "$DB_USER" "$DB_NAME"
        return 1
    fi
}

# 恢复媒体文件
restore_media() {
    local backup_file="$1"

    log "开始恢复媒体文件..."

    if [ ! -f "$backup_file" ]; then
        log_error "备份文件不存在: $backup_file"
        return 1
    fi

    # 先备份当前媒体文件
    log "备份当前媒体文件..."
    local current_backup="$BACKUP_DIR/media_before_restore_$(date +%Y%m%d_%H%M%S).tar.gz"
    tar -czf "$current_backup" -C "$BACKEND_DIR/media" . 2>/dev/null || true
    log "当前媒体文件已备份到: $current_backup"

    # 清空媒体目录
    log "清空媒体目录..."
    rm -rf "${BACKEND_DIR}/media/"*

    # 恢复媒体文件
    log "正在恢复媒体文件..."
    if tar -xzf "$backup_file" -C "$BACKEND_DIR/media"; then
        log "媒体文件恢复成功"
    else
        log_error "媒体文件恢复失败"

        # 尝试恢复原媒体文件
        log "尝试恢复原媒体文件..."
        tar -xzf "$current_backup" -C "$BACKEND_DIR/media"
        return 1
    fi
}

# 恢复配置文件
restore_config() {
    local backup_file="$1"

    log "开始恢复配置文件..."

    if [ ! -f "$backup_file" ]; then
        log_error "备份文件不存在: $backup_file"
        return 1
    fi

    # 恢复配置文件
    log "正在恢复配置文件..."
    tar -xzf "$backup_file" -C /

    # 重新加载Nginx
    log "重新加载Nginx..."
    systemctl reload nginx

    log "配置文件恢复成功"
}

# 回滚代码
rollback_code() {
    local commits="${1:-1}"

    log "回滚代码 $commits 个提交..."

    cd "$PROJECT_DIR"

    # 回滚后端
    if [ -d "$BACKEND_DIR/.git" ]; then
        log "回滚后端代码..."
        cd "$BACKEND_DIR"
        git reset --hard HEAD~"$commits"
    fi

    # 回滚前端
    if [ -d "$FRONTEND_DIR/.git" ]; then
        log "回滚前端代码..."
        cd "$FRONTEND_DIR"
        git reset --hard HEAD~"$commits"
    fi

    log "代码回滚完成"
}

# 完整回滚
full_rollback() {
    local backup_file="$1"

    log "========================================="
    log "开始完整回滚"
    log "========================================="

    # 恢复数据库
    if [[ "$backup_file" == *db_backup* ]]; then
        restore_database "$backup_file"
    fi

    # 恢复媒体文件
    if [[ "$backup_file" == *media_backup* ]]; then
        restore_media "$backup_file"
    fi

    # 恢复配置文件
    if [[ "$backup_file" == *config_backup* ]]; then
        restore_config "$backup_file"
    fi

    # 重启服务
    log "重启服务..."
    systemctl restart member-management
    systemctl reload nginx

    sleep 3

    # 检查服务状态
    if systemctl is-active --quiet member-management; then
        log "Django服务运行正常"
    else
        log_error "Django服务启动失败"
        return 1
    fi

    log "========================================="
    log "回滚完成！"
    log "========================================="
}

# 主函数
main() {
    log "========================================="
    log "会员管理系统回滚脚本"
    log "========================================="

    # 如果没有参数，列出可用备份
    if [ $# -eq 0 ]; then
        list_backups
        echo ""
        echo "使用方法:"
        echo "  $0 <backup_file>              # 恢复指定备份"
        echo "  $0 --db <backup_file>         # 恢复数据库"
        echo "  $0 --media <backup_file>      # 恢复媒体文件"
        echo "  $0 --config <backup_file>     # 恢复配置文件"
        echo "  $0 --code [commits]           # 回滚代码（默认1个提交）"
        echo ""
        exit 0
    fi

    case "$1" in
        --db)
            restore_database "$2"
            ;;
        --media)
            restore_media "$2"
            ;;
        --config)
            restore_config "$2"
            ;;
        --code)
            rollback_code "${2:-1}"
            ;;
        --list)
            list_backups
            ;;
        *)
            full_rollback "$1"
            ;;
    esac
}

# 捕获错误
trap 'log_error "回滚失败！"; exit 1' ERR

# 运行主函数
main "$@"
