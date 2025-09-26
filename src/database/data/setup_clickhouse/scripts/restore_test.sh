#!/bin/bash

# 手動還原測試腳本

BACKUP_FILE="backup_20250927_005048.tar.gz"

echo "開始還原測試..."
echo "備份檔案: $BACKUP_FILE"

# 停止容器
echo "1. 停止容器..."
docker-compose down

# 清理舊資料
echo "2. 清理舊資料..."
sudo rm -rf data/*

# 重新啟動容器
echo "3. 重新啟動容器..."
docker-compose up -d
sleep 15

# 解壓備份到臨時目錄
echo "4. 解壓備份..."
mkdir -p /tmp/restore_test
tar xzf backup/$BACKUP_FILE -C /tmp/restore_test

# 複製資料到容器
echo "5. 複製資料到容器..."
docker cp /tmp/restore_test/var/lib/clickhouse/data clickhouse-server:/var/lib/clickhouse/
docker cp /tmp/restore_test/var/lib/clickhouse/metadata clickhouse-server:/var/lib/clickhouse/

# 修正權限
echo "6. 修正權限..."
docker exec clickhouse-server chown -R clickhouse:clickhouse /var/lib/clickhouse/

# 重啟容器
echo "7. 重啟容器..."
docker-compose restart
sleep 15

# 驗證還原
echo "8. 驗證還原結果..."
docker exec clickhouse-server clickhouse-client --user trader --password SecurePass123! --database market_data --query "SELECT count(*) as restored_records FROM market_ticks"

# 清理臨時目錄
rm -rf /tmp/restore_test

echo "✅ 還原測試完成"