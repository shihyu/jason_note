備份資料
# 停止容器以确保数据一致性
docker stop my_clickhouse

# 备份数据到主机
docker cp my_clickhouse:/var/lib/clickhouse backup/



恢復資料
# 停止容器
docker stop my_clickhouse

# 将备份数据复制回容器
docker cp backup/clickhouse my_clickhouse:/var/lib/
