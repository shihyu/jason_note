#!/bin/bash

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
FORMAT Pretty" 2>/dev/null

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
FORMAT Pretty" 2>/dev/null

# 系統健康狀態
echo -e "\n✅ Health Check:"
docker exec clickhouse-server clickhouse-client --query "SELECT 'ClickHouse is running OK!'" 2>/dev/null || echo "ClickHouse is not running!"