#!/bin/bash

# 設定變數
BACKUP_DIR="/home/$USER/github/jason_note/src/database/setup_clickhouse/backup"
CONTAINER_NAME="clickhouse-server"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=7
LOG_FILE="$BACKUP_DIR/backup.log"

# 顏色輸出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 日誌函數
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# 錯誤處理
error_exit() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
    exit 1
}

# 檢查容器是否運行
check_container() {
    if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        error_exit "Container ${CONTAINER_NAME} is not running!"
    fi
}

# 執行備份
perform_backup() {
    log "Starting backup..."

    # 方法 1: 使用 ClickHouse 原生備份（推薦）
    log "Creating ClickHouse native backup..."

    # 創建所有表的備份
    docker exec $CONTAINER_NAME clickhouse-client --query "
        SELECT concat('BACKUP TABLE ', database, '.', name, ' TO Disk(''backups'', ''', '${DATE}/', database, '_', name, ''');')
        FROM system.tables
        WHERE database NOT IN ('system', 'information_schema', 'INFORMATION_SCHEMA')
    " | while read backup_cmd; do
        if [ ! -z "$backup_cmd" ]; then
            docker exec $CONTAINER_NAME clickhouse-client --query "$backup_cmd" || log "Warning: Failed to backup a table"
        fi
    done

    # 方法 2: 物理備份（完整備份）
    log "Creating physical backup..."
    docker exec $CONTAINER_NAME bash -c "
        tar czf /backups/physical_backup_${DATE}.tar.gz \
        --exclude='/var/lib/clickhouse/preprocessed_configs' \
        --exclude='/var/lib/clickhouse/tmp' \
        /var/lib/clickhouse/data \
        /var/lib/clickhouse/metadata
    " || error_exit "Physical backup failed"

    # 備份配置文件
    log "Backing up configuration..."
    tar czf "$BACKUP_DIR/config_backup_${DATE}.tar.gz" \
        -C "$(dirname "$BACKUP_DIR")" config/ docker-compose.yml \
        || error_exit "Config backup failed"

    log "Backup completed successfully!"
}

# 清理舊備份
cleanup_old_backups() {
    log "Cleaning up old backups (older than $RETENTION_DAYS days)..."

    # 清理本地備份
    find "$BACKUP_DIR" -name "*.tar.gz" -type f -mtime +$RETENTION_DAYS -delete

    # 清理容器內備份
    docker exec $CONTAINER_NAME bash -c "
        find /backups -name '*.tar.gz' -type f -mtime +$RETENTION_DAYS -delete
    "

    log "Cleanup completed"
}

# 顯示備份資訊
show_backup_info() {
    echo -e "${GREEN}=== Backup Information ===${NC}"
    echo "Backup Location: $BACKUP_DIR"
    echo "Latest Backups:"
    ls -lah "$BACKUP_DIR" 2>/dev/null | grep -E "*.tar.gz" | tail -5

    # 顯示備份大小統計
    total_size=$(du -sh "$BACKUP_DIR" 2>/dev/null | cut -f1)
    echo -e "\nTotal backup size: ${YELLOW}$total_size${NC}"
}

# 主程序
main() {
    echo -e "${GREEN}=== ClickHouse Backup Script ===${NC}"

    # 創建備份目錄
    mkdir -p "$BACKUP_DIR"

    # 執行備份流程
    check_container
    perform_backup
    cleanup_old_backups
    show_backup_info

    echo -e "${GREEN}✅ Backup process completed!${NC}"
}

# 執行主程序
main