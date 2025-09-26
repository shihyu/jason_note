#!/bin/bash

# 設定變數
BACKUP_DIR="/home/$USER/github/jason_note/src/database/setup_clickhouse/backup"
CONTAINER_NAME="clickhouse-server"
SETUP_DIR="/home/$USER/github/jason_note/src/database/setup_clickhouse"

# 顏色輸出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 列出可用備份
list_backups() {
    echo -e "${GREEN}=== Available Backups ===${NC}"
    ls -la "$BACKUP_DIR" 2>/dev/null | grep -E "physical_backup.*tar.gz" | nl
}

# 還原備份
restore_backup() {
    list_backups

    echo -e "${YELLOW}Enter the number of backup to restore:${NC}"
    read backup_num

    backup_file=$(ls "$BACKUP_DIR" 2>/dev/null | grep -E "physical_backup.*tar.gz" | sed -n "${backup_num}p")

    if [ -z "$backup_file" ]; then
        echo -e "${RED}Invalid selection!${NC}"
        exit 1
    fi

    echo -e "${YELLOW}⚠️  WARNING: This will stop ClickHouse and restore data!${NC}"
    echo "Restore from: $backup_file"
    echo "Continue? (yes/no)"
    read confirm

    if [ "$confirm" != "yes" ]; then
        echo "Restore cancelled"
        exit 0
    fi

    # 停止容器
    echo "Stopping ClickHouse..."
    cd "$SETUP_DIR"
    docker-compose down

    # 備份當前數據（安全起見）
    echo "Backing up current data..."
    if [ -d "$SETUP_DIR/data" ]; then
        mv "$SETUP_DIR/data" "$SETUP_DIR/data.old.$(date +%Y%m%d_%H%M%S)"
    fi
    mkdir -p "$SETUP_DIR/data"

    # 解壓備份
    echo "Restoring backup..."
    tar xzf "$BACKUP_DIR/$backup_file" -C "$SETUP_DIR/data" --strip-components=3

    # 修正權限
    chmod -R 777 "$SETUP_DIR/data"

    # 重啟容器
    echo "Starting ClickHouse..."
    docker-compose up -d

    # 等待服務啟動
    sleep 10

    # 檢查服務狀態
    docker exec $CONTAINER_NAME clickhouse-client --query "SELECT 'Restore completed successfully!'"

    echo -e "${GREEN}✅ Restore completed!${NC}"
}

# 主程序
restore_backup