#!/bin/bash

# 会员管理系统备份脚本
# 使用方法: sudo bash backup.sh [--db-only] [--media-only]

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
MEDIA_DIR="$BACKEND_DIR/media"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="/var/log/member-management/backup.log"

# 日志函数
log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1" | tee -a "$LOG_FILE"
}

# 创建备份目录
mkdir_backup_dir() {
    mkdir -p "$BACKUP_DIR"
    mkdir -p "$(dirname "$LOG_FILE")"
}

# 备份数据库
backup_database() {
    log "开始备份数据库..."

    if [ ! -f "$BACKEND_DIR/.env" ]; then
        log_error "未找到.env文件"
        return 1
    fi

    source "$BACKEND_DIR/.env"

    if [ -z "$DB_NAME" ] || [ -z "$DB_USER" ] || [ -z "$DB_PASSWORD" ]; then
        log_error "数据库配置不完整"
        return 1
    fi

    local backup_file="$BACKUP_DIR/db_backup_${TIMESTAMP}.sql.gz"

    if PGPASSWORD="$DB_PASSWORD" pg_dump -h localhost -U "$DB_USER" "$DB_NAME" | gzip > "$backup_file"; then
        local size=$(du -h "$backup_file" | cut -f1)
        log "数据库备份成功: $backup_file ($size)"

        # 验证备份文件
        if gzip -t "$backup_file" 2>/dev/null; then
            log "备份文件验证成功"
        else
            log_error "备份文件验证失败"
            rm -f "$backup_file"
            return 1
        fi
    else
        log_error "数据库备份失败"
        return 1
    fi

    # 清理旧备份（保留最近7天）
    find "$BACKUP_DIR" -name "db_backup_*.sql.gz" -mtime +7 -delete
    log "已清理7天前的数据库备份"
}

# 备份媒体文件
backup_media() {
    log "开始备份媒体文件..."

    if [ ! -d "$MEDIA_DIR" ]; then
        log "媒体文件目录不存在，跳过"
        return 0
    fi

    local backup_file="$BACKUP_DIR/media_backup_${TIMESTAMP}.tar.gz"

    if tar -czf "$backup_file" -C "$MEDIA_DIR" . 2>/dev/null; then
        local size=$(du -h "$backup_file" | cut -f1)
        log "媒体文件备份成功: $backup_file ($size)"

        # 验证备份文件
        if tar -tzf "$backup_file" >/dev/null 2>&1; then
            log "备份文件验证成功"
        else
            log_error "备份文件验证失败"
            rm -f "$backup_file"
            return 1
        fi
    else
        log_error "媒体文件备份失败"
        return 1
    fi

    # 清理旧备份（保留最近4周）
    find "$BACKUP_DIR" -name "media_backup_*.tar.gz" -mtime +28 -delete
    log "已清理4周前的媒体文件备份"
}

# 备份配置文件
backup_config() {
    log "开始备份配置文件..."

    local backup_file="$BACKUP_DIR/config_backup_${TIMESTAMP}.tar.gz"

    if tar -czf "$backup_file" \
        -C "$BACKEND_DIR" .env \
        -C /etc nginx/sites-available/member-management-* \
        -C /etc/systemd/system member-management.service 2>/dev/null; then
        local size=$(du -h "$backup_file" | cut -f1)
        log "配置文件备份成功: $backup_file ($size)"
    else
        log_error "配置文件备份失败"
        return 1
    fi

    # 清理旧备份（保留最近3个月）
    find "$BACKUP_DIR" -name "config_backup_*.tar.gz" -mtime +90 -delete
    log "已清理3个月前的配置文件备份"
}

# 显示备份统计
show_stats() {
    log ""
    log "========================================"
    log "备份统计信息"
    log "========================================"

    local db_count=$(find "$BACKUP_DIR" -name "db_backup_*.sql.gz" | wc -l)
    local media_count=$(find "$BACKUP_DIR" -name "media_backup_*.tar.gz" | wc -l)
    local config_count=$(find "$BACKUP_DIR" -name "config_backup_*.tar.gz" | wc -l)
    local total_size=$(du -sh "$BACKUP_DIR" 2>/dev/null | cut -f1)

    log "数据库备份数量: $db_count"
    log "媒体文件备份数量: $media_count"
    log "配置文件备份数量: $config_count"
    log "备份目录总大小: $total_size"
    log "========================================"
}

# 主函数
main() {
    log "========================================="
    log "开始备份会员管理系统"
    log "========================================="

    mkdir_backup_dir

    # 根据参数选择备份类型
    case "${1:-all}" in
        --db-only)
            backup_database
            ;;
        --media-only)
            backup_media
            ;;
        --config-only)
            backup_config
            ;;
        all)
            backup_database
            backup_media
            backup_config
            ;;
        *)
            echo "使用方法: $0 [--db-only] [--media-only] [--config-only]"
            exit 1
            ;;
    esac

    show_stats

    log ""
    log "备份完成！"
}

# 捕获错误
trap 'log_error "备份失败！"; exit 1' ERR

# 运行主函数
main "$@"
