備份資料

# 停止容器以确保数据一致性
docker stop my_clickhouse

# 备份数据到主机
docker cp my_clickhouse:/var/lib/clickhouse backup/

# 启动容器
docker start my_clickhouse


恢復資料

# 停止容器
docker stop my_clickhouse

# 清空容器中的现有数据目录（慎重操作）
docker exec my_clickhouse rm -rf /var/lib/clickhouse/*

# 将备份数据复制回容器
docker cp backup/clickhouse my_clickhouse:/var/lib/

# 设置正确的权限
docker exec -it my_clickhouse bash
chown -R clickhouse:clickhouse /var/lib/clickhouse
exit

# 启动容器
docker start my_clickhouse

