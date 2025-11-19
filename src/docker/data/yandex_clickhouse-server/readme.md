備份資料
# 停止容器以確保數據一致性
docker stop my_clickhouse

# 備份數據到主機
docker cp my_clickhouse:/var/lib/clickhouse backup/



恢復資料
# 停止容器
docker stop my_clickhouse

# 將備份數據複製回容器
docker cp backup/clickhouse my_clickhouse:/var/lib/
