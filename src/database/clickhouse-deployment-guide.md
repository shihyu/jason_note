# ClickHouse Docker 完整部署指南

## 📋 目錄
- [系統需求](#系統需求)
- [快速安裝](#快速安裝)
- [生產環境配置](#生產環境配置)
- [自動備份設置](#自動備份設置)
- [測試範例](#測試範例)
- [監控與維護](#監控與維護)
- [常見問題](#常見問題)

## 系統需求

### 最低配置
- CPU: 4 核心
- RAM: 8 GB
- Storage: 100 GB SSD
- OS: Linux (Ubuntu 20.04+ / CentOS 7+)
- Docker: 20.10+
- Docker Compose: 2.0+

### 建議配置
- CPU: 8+ 核心
- RAM: 32+ GB
- Storage: NVMe SSD (越快越好)
- Network: 1 Gbps+

## 快速安裝

### 1. 安裝 Docker (Ubuntu 為例)
```bash
# 更新系統
sudo apt-get update
sudo apt-get upgrade -y

# 安裝 Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 安裝 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 將當前用戶加入 docker 群組
sudo usermod -aG docker $USER
newgrp docker

# 驗證安裝
docker --version
docker-compose --version
```

### 2. 建立專案目錄結構
```bash
# 建立目錄
mkdir -p ~/clickhouse-docker/{config,data,logs,backup,scripts}
cd ~/clickhouse-docker

# 建立必要的目錄權限
sudo mkdir -p /data/clickhouse
sudo chown -R $USER:$USER /data/clickhouse
```

## 生產環境配置

### 3. 創建優化的 docker-compose.yml
```yaml
# ~/clickhouse-docker/docker-compose.yml
version: '3.8'

services:
  clickhouse:
    image: clickhouse/clickhouse-server:24.8-alpine
    container_name: clickhouse-server
    hostname: clickhouse-server
    
    # 效能優化：使用 host 網路模式
    network_mode: host
    
    # 環境變數
    environment:
      # 初始資料庫設置
      CLICKHOUSE_DB: market_data
      CLICKHOUSE_USER: trader
      CLICKHOUSE_PASSWORD: SecurePass123!
      CLICKHOUSE_DEFAULT_ACCESS_MANAGEMENT: 1
      # 效能相關
      CLICKHOUSE_MAX_MEMORY_USAGE: 10000000000  # 10GB
      CLICKHOUSE_MAX_MEMORY_USAGE_FOR_USER: 10000000000
      
    # 資源限制
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 16G
        reservations:
          cpus: '2'
          memory: 8G
    
    # 掛載設定
    volumes:
      # 資料目錄 - 使用本地 SSD
      - type: bind
        source: /data/clickhouse
        target: /var/lib/clickhouse
      # 日誌目錄
      - type: bind
        source: ./logs
        target: /var/log/clickhouse-server
      # 自定義配置
      - type: bind
        source: ./config
        target: /etc/clickhouse-server/config.d
        read_only: true
      # 備份目錄
      - type: bind
        source: ./backup
        target: /backups
    
    # 系統限制優化
    ulimits:
      nofile:
        soft: 262144
        hard: 262144
      memlock:
        soft: -1
        hard: -1
      nproc:
        soft: 131072
        hard: 131072
    
    # 健康檢查
    healthcheck:
      test: ["CMD", "clickhouse-client", "--host", "localhost", "--query", "SELECT 1"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 30s
    
    # 自動重啟
    restart: unless-stopped
    
    # 日誌設置
    logging:
      driver: "json-file"
      options:
        max-size: "100m"
        max-file: "3"
```

### 4. 創建自定義配置文件

#### 儲存優化配置
```xml
<!-- ~/clickhouse-docker/config/storage.xml -->
<?xml version="1.0"?>
<clickhouse>
    <storage_configuration>
        <disks>
            <default>
                <path>/var/lib/clickhouse/</path>
            </default>
            <fast_ssd>
                <path>/var/lib/clickhouse/fast/</path>
            </fast_ssd>
        </disks>
        <policies>
            <tiered>
                <volumes>
                    <hot>
                        <disk>fast_ssd</disk>
                        <max_data_part_size_bytes>10737418240</max_data_part_size_bytes>
                    </hot>
                    <cold>
                        <disk>default</disk>
                    </cold>
                </volumes>
                <move_factor>0.2</move_factor>
            </tiered>
        </policies>
    </storage_configuration>
    
    <!-- 壓縮設置 -->
    <compression>
        <case>
            <method>lz4hc</method>
            <level>12</level>
        </case>
    </compression>
</clickhouse>
```

#### 效能優化配置
```xml
<!-- ~/clickhouse-docker/config/performance.xml -->
<?xml version="1.0"?>
<clickhouse>
    <!-- 查詢效能優化 -->
    <max_threads>8</max_threads>
    <max_memory_usage>10000000000</max_memory_usage>
    <max_memory_usage_for_user>10000000000</max_memory_usage_for_user>
    <max_bytes_before_external_group_by>5000000000</max_bytes_before_external_group_by>
    
    <!-- 網路優化 -->
    <max_concurrent_queries>100</max_concurrent_queries>
    <max_connections>4096</max_connections>
    
    <!-- 背景任務優化 -->
    <background_pool_size>16</background_pool_size>
    <background_schedule_pool_size>16</background_schedule_pool_size>
    
    <!-- MergeTree 優化 -->
    <merge_tree>
        <max_suspicious_broken_parts>5</max_suspicious_broken_parts>
        <max_parts_in_total>100000</max_parts_in_total>
        <max_bytes_to_merge_at_max_space_in_pool>161061273600</max_bytes_to_merge_at_max_space_in_pool>
    </merge_tree>
</clickhouse>
```

## 自動備份設置

### 5. 備份腳本

#### 主備份腳本
```bash
#!/bin/bash
# ~/clickhouse-docker/scripts/backup.sh

# 設定變數
BACKUP_DIR="/home/$USER/clickhouse-docker/backup"
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
        -C ~/clickhouse-docker config/ docker-compose.yml \
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
    ls -lah "$BACKUP_DIR" | grep -E "*.tar.gz" | tail -5
    
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
```

#### 還原腳本
```bash
#!/bin/bash
# ~/clickhouse-docker/scripts/restore.sh

# 設定變數
BACKUP_DIR="/home/$USER/clickhouse-docker/backup"
CONTAINER_NAME="clickhouse-server"

# 顏色輸出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 列出可用備份
list_backups() {
    echo -e "${GREEN}=== Available Backups ===${NC}"
    ls -la "$BACKUP_DIR" | grep -E "physical_backup.*tar.gz" | nl
}

# 還原備份
restore_backup() {
    list_backups
    
    echo -e "${YELLOW}Enter the number of backup to restore:${NC}"
    read backup_num
    
    backup_file=$(ls "$BACKUP_DIR" | grep -E "physical_backup.*tar.gz" | sed -n "${backup_num}p")
    
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
    docker-compose -f ~/clickhouse-docker/docker-compose.yml down
    
    # 備份當前數據（安全起見）
    echo "Backing up current data..."
    sudo mv /data/clickhouse /data/clickhouse.old.$(date +%Y%m%d_%H%M%S)
    sudo mkdir -p /data/clickhouse
    
    # 解壓備份
    echo "Restoring backup..."
    sudo tar xzf "$BACKUP_DIR/$backup_file" -C / --strip-components=2
    
    # 修正權限
    sudo chown -R 101:101 /data/clickhouse
    
    # 重啟容器
    echo "Starting ClickHouse..."
    docker-compose -f ~/clickhouse-docker/docker-compose.yml up -d
    
    # 等待服務啟動
    sleep 10
    
    # 檢查服務狀態
    docker exec $CONTAINER_NAME clickhouse-client --query "SELECT 'Restore completed successfully!'"
    
    echo -e "${GREEN}✅ Restore completed!${NC}"
}

# 主程序
restore_backup
```

### 6. 設置 Crontab 自動備份
```bash
# 使腳本可執行
chmod +x ~/clickhouse-docker/scripts/*.sh

# 設置每日自動備份 (每天凌晨 2 點)
crontab -e

# 添加以下行
0 2 * * * /home/$USER/clickhouse-docker/scripts/backup.sh >> /home/$USER/clickhouse-docker/backup/cron.log 2>&1
```

## 測試範例

### 7. 啟動服務
```bash
cd ~/clickhouse-docker
docker-compose up -d

# 檢查狀態
docker-compose ps
docker logs clickhouse-server --tail 50
```

### 8. 創建測試表並導入數據

#### 創建市場數據表
```sql
# 連接到 ClickHouse
docker exec -it clickhouse-server clickhouse-client --user trader --password SecurePass123!

-- 創建資料庫
CREATE DATABASE IF NOT EXISTS market_data;
USE market_data;

-- 創建優化的 tick 數據表
CREATE TABLE market_ticks (
    ts DateTime64(3) CODEC(DoubleDelta, LZ4),
    symbol LowCardinality(String),
    close Decimal32(2) CODEC(Gorilla, LZ4),
    volume UInt32 CODEC(T64, LZ4),
    bid_price Decimal32(2) CODEC(Gorilla, LZ4),
    bid_volume UInt32 CODEC(T64, LZ4),
    ask_price Decimal32(2) CODEC(Gorilla, LZ4),
    ask_volume UInt32 CODEC(T64, LZ4),
    tick_type UInt8
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(ts)
ORDER BY (symbol, ts)
SETTINGS index_granularity = 8192;

-- 查看表結構
DESCRIBE TABLE market_ticks;
```

#### 導入測試數據
```bash
# 創建測試 CSV 文件
cat > ~/clickhouse-docker/test_data.csv << 'EOF'
ts,symbol,close,volume,bid_price,bid_volume,ask_price,ask_volume,tick_type
2025-09-25 17:25:00.044,AAPL,1325.0,7,1320.0,160,1325.0,22,1
2025-09-25 17:25:02.207,AAPL,1325.0,1,1320.0,160,1325.0,22,1
2025-09-25 17:25:03.125,AAPL,1325.0,1,1320.0,161,1325.0,21,1
2025-09-25 17:25:47.863,AAPL,1325.0,1,1320.0,162,1325.0,21,1
2025-09-25 17:26:14.894,TSLA,1325.0,1,1320.0,181,1325.0,18,1
2025-09-25 17:26:51.365,TSLA,1325.0,1,1320.0,181,1325.0,27,1
2025-09-25 17:29:59.655,TSLA,1325.0,3,1320.0,177,1325.0,31,1
2025-09-25 17:30:06.262,NVDA,1325.0,1,1320.0,180,1325.0,28,1
2025-09-25 17:30:14.542,NVDA,1325.0,3,1320.0,183,1325.0,27,1
2025-09-25 17:30:52.600,NVDA,1320.0,2,1320.0,185,1325.0,22,2
EOF

# 導入數據
docker exec -i clickhouse-server clickhouse-client \
    --user trader --password SecurePass123! \
    --query "INSERT INTO market_data.market_ticks FORMAT CSVWithNames" \
    < ~/clickhouse-docker/test_data.csv
```

### 9. 測試查詢

#### 基本查詢測試
```sql
-- 連接到資料庫
docker exec -it clickhouse-server clickhouse-client \
    --user trader --password SecurePass123! \
    --database market_data

-- 查詢記錄數
SELECT count(*) FROM market_ticks;

-- 查看最新數據
SELECT * FROM market_ticks ORDER BY ts DESC LIMIT 5;

-- 按 symbol 聚合
SELECT 
    symbol,
    count(*) as tick_count,
    avg(close) as avg_price,
    max(volume) as max_volume
FROM market_ticks
GROUP BY symbol;

-- 時間範圍查詢
SELECT *
FROM market_ticks
WHERE ts >= '2025-09-25 17:25:00'
  AND ts <= '2025-09-25 17:30:00'
ORDER BY ts;

-- 查看壓縮效果
SELECT 
    formatReadableSize(sum(data_compressed_bytes)) as compressed,
    formatReadableSize(sum(data_uncompressed_bytes)) as uncompressed,
    round(sum(data_uncompressed_bytes) / sum(data_compressed_bytes), 2) as ratio
FROM system.parts
WHERE database = 'market_data' AND table = 'market_ticks';
```

#### 效能測試
```sql
-- 插入大量測試數據
INSERT INTO market_ticks 
SELECT 
    now() - randUniform(0, 86400) as ts,
    arrayElement(['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'NVDA'], randUniform(1, 5)) as symbol,
    1000 + randNormal(0, 50) as close,
    randUniform(1, 1000) as volume,
    1000 + randNormal(-5, 45) as bid_price,
    randUniform(1, 500) as bid_volume,
    1000 + randNormal(5, 55) as ask_price,
    randUniform(1, 500) as ask_volume,
    randUniform(1, 3) as tick_type
FROM numbers(1000000);

-- 測試查詢效能
SELECT 
    symbol,
    toStartOfMinute(ts) as minute,
    avg(close) as avg_price,
    sum(volume) as total_volume
FROM market_ticks
WHERE ts >= now() - INTERVAL 1 DAY
GROUP BY symbol, minute
ORDER BY minute DESC, symbol
LIMIT 100
FORMAT Null;

-- 顯示查詢統計
SHOW PROCESSLIST;
```

## 監控與維護

### 10. 監控腳本
```bash
#!/bin/bash
# ~/clickhouse-docker/scripts/monitor.sh

echo "=== ClickHouse Monitoring Dashboard ==="
echo "======================================="

# 系統資源使用
echo -e "\n📊 Resource Usage:"
docker stats clickhouse-server --no-stream

# 資料庫大小
echo -e "\n💾 Database Size:"
docker exec clickhouse-server clickhouse-client --user trader --password SecurePass123! --query "
SELECT 
    database,
    formatReadableSize(sum(bytes_on_disk)) as size,
    formatReadableQuantity(sum(rows)) as rows,
    count() as tables
FROM system.parts
WHERE active
GROUP BY database
FORMAT Pretty"

# 查詢效能
echo -e "\n⚡ Recent Queries:"
docker exec clickhouse-server clickhouse-client --user trader --password SecurePass123! --query "
SELECT 
    substring(query, 1, 50) as query_preview,
    formatReadableSize(memory_usage) as memory,
    query_duration_ms,
    read_rows,
    written_rows
FROM system.query_log
WHERE type = 'QueryFinish'
ORDER BY event_time DESC
LIMIT 5
FORMAT Pretty"

# 系統健康狀態
echo -e "\n✅ Health Check:"
docker exec clickhouse-server clickhouse-client --query "SELECT 'ClickHouse is running OK!'"
```

### 11. 日常維護命令
```bash
# 優化表（整理碎片）
docker exec clickhouse-server clickhouse-client --user trader --password SecurePass123! \
    --query "OPTIMIZE TABLE market_data.market_ticks FINAL"

# 清理舊分區
docker exec clickhouse-server clickhouse-client --user trader --password SecurePass123! \
    --query "ALTER TABLE market_data.market_ticks DROP PARTITION '202501'"

# 查看慢查詢
docker exec clickhouse-server clickhouse-client --user trader --password SecurePass123! \
    --query "
    SELECT 
        query,
        query_duration_ms,
        memory_usage
    FROM system.query_log
    WHERE query_duration_ms > 1000
    ORDER BY query_duration_ms DESC
    LIMIT 10"

# 重啟服務
docker-compose restart

# 升級 ClickHouse
docker-compose pull
docker-compose up -d
```

## 常見問題

### Q1: 記憶體不足錯誤
```bash
# 調整記憶體限制
docker exec clickhouse-server clickhouse-client --query "
SET max_memory_usage = 5000000000;
SET max_memory_usage_for_user = 5000000000;"
```

### Q2: 磁碟空間不足
```bash
# 檢查空間使用
df -h /data/clickhouse

# 清理舊數據
docker exec clickhouse-server clickhouse-client --query "
ALTER TABLE market_data.market_ticks 
DROP PARTITION WHERE toYYYYMM(ts) < toYYYYMM(now() - INTERVAL 6 MONTH)"
```

### Q3: 連接被拒絕
```bash
# 檢查容器狀態
docker ps | grep clickhouse

# 查看日誌
docker logs clickhouse-server --tail 100

# 重啟容器
docker-compose restart
```

### Q4: 查詢太慢
```sql
-- 分析查詢計畫
EXPLAIN SELECT * FROM market_ticks WHERE symbol = 'AAPL';

-- 創建索引
ALTER TABLE market_ticks ADD INDEX idx_symbol (symbol) TYPE minmax GRANULARITY 4;
```

## 效能調優建議

1. **使用 SSD/NVMe** - I/O 是最大瓶頸
2. **適當分區** - 按月分區對 tick 數據最合適
3. **批量插入** - 單筆插入效能差，建議批量 10000+ 筆
4. **定期 OPTIMIZE** - 每週執行一次 OPTIMIZE TABLE
5. **監控記憶體** - ClickHouse 是記憶體密集型資料庫

## 安全建議

1. **修改預設密碼** - 立即修改 docker-compose.yml 中的密碼
2. **限制網路存取** - 使用防火牆限制 8123/9000 端口
3. **定期備份** - 確保自動備份正常運行
4. **監控日誌** - 定期檢查異常存取
5. **更新版本** - 關注安全更新

## 支援資源

- [官方文檔](https://clickhouse.com/docs)
- [Docker Hub](https://hub.docker.com/r/clickhouse/clickhouse-server)
- [GitHub Issues](https://github.com/ClickHouse/ClickHouse/issues)
- [社群論壇](https://clickhouse.com/community)

---

**最後更新**: 2025-09-26  
**版本**: ClickHouse 24.8  
**作者**: DevOps Team