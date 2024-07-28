https://github.com/Altinity/clickhouse-backup/releases


## 使用 docker cp 備份
docker cp my_clickhouse:/var/lib/clickhouse backup/


## 將備份資料複製回容器：
docker cp backup/clickhouse my_clickhouse:/var/lib/clickhouse
