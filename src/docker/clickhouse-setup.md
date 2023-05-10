# Tutorial for set up clickhouse server

https://github.com/jneo8/clickhouse-setup

- Makefile

```makefile
run-single-server:
	docker run -d --name clickhouse-server -p 9911:9000 -p 1121:8123 --ulimit nofile=262144:262144 yandex/clickhouse-server

run-single-client:
	docker run -it --rm --link clickhouse-server:clickhouse-server yandex/clickhouse-client  --host clickhouse-server

run-cluster-client-1:
	docker run -it --rm --network="clickhouse-net" --link clickhouse-01:clickhouse-server yandex/clickhouse-client --host clickhouse-server
run-cluster-client-2:
	docker run -it --rm --network="clickhouse-net" --link clickhouse-02:clickhouse-server yandex/clickhouse-client --host clickhouse-server
run-cluster-client-3:
	docker run -it --rm --network="clickhouse-net" --link clickhouse-03:clickhouse-server yandex/clickhouse-client --host clickhouse-server
run-cluster-client-4:
	docker run -it --rm --network="clickhouse-net" --link clickhouse-04:clickhouse-server yandex/clickhouse-client --host clickhouse-server
run-cluster-client-5:
	docker run -it --rm --network="clickhouse-net" --link clickhouse-05:clickhouse-server yandex/clickhouse-client --host clickhouse-server
run-cluster-client-6:
	docker run -it --rm --network="clickhouse-net" --link clickhouse-06:clickhouse-server yandex/clickhouse-client --host clickhouse-server

run-cluster-client-1-auth:
	docker run -it --rm --network="clickhouse-net" --link clickhouse-01:clickhouse-server yandex/clickhouse-client --host clickhouse-server -u user1 --password 123456

exec:
	docker exec -it clickhouse-server /bin/bash
```

- docker-compose.yml

```dockerfile
version: '3'

services:
    clickhouse-zookeeper:
        image: zookeeper
        ports:
            - "2181:2181"
            - "2182:2182"
        container_name: clickhouse-zookeeper
        hostname: clickhouse-zookeeper

    clickhouse-01:
        image: yandex/clickhouse-server
        hostname: clickhouse-01
        container_name: clickhouse-01
        ports:
            - 9001:9000
        volumes:
                - ./config/clickhouse_config.xml:/etc/clickhouse-server/config.xml
                - ./config/clickhouse_metrika.xml:/etc/clickhouse-server/metrika.xml
                - ./config/macros/macros-01.xml:/etc/clickhouse-server/config.d/macros.xml
                - ./config/users.xml:/etc/clickhouse-server/users.xml
                # - ./data/server-01:/var/lib/clickhouse
        ulimits:
            nofile:
                soft: 262144
                hard: 262144
        depends_on:
            - "clickhouse-zookeeper"

    clickhouse-02:
        image: yandex/clickhouse-server
        hostname: clickhouse-02
        container_name: clickhouse-02
        ports:
            - 9002:9000
        volumes:
                - ./config/clickhouse_config.xml:/etc/clickhouse-server/config.xml
                - ./config/clickhouse_metrika.xml:/etc/clickhouse-server/metrika.xml
                - ./config/macros/macros-02.xml:/etc/clickhouse-server/config.d/macros.xml
                - ./config/users.xml:/etc/clickhouse-server/users.xml
                # - ./data/server-02:/var/lib/clickhouse
        ulimits:
            nofile:
                soft: 262144
                hard: 262144
        depends_on:
            - "clickhouse-zookeeper"

    clickhouse-03:
        image: yandex/clickhouse-server
        hostname: clickhouse-03
        container_name: clickhouse-03
        ports:
            - 9003:9000
        volumes:
                - ./config/clickhouse_config.xml:/etc/clickhouse-server/config.xml
                - ./config/clickhouse_metrika.xml:/etc/clickhouse-server/metrika.xml
                - ./config/macros/macros-03.xml:/etc/clickhouse-server/config.d/macros.xml
                - ./config/users.xml:/etc/clickhouse-server/users.xml
                # - ./data/server-03:/var/lib/clickhouse
        ulimits:
            nofile:
                soft: 262144
                hard: 262144
        depends_on:
            - "clickhouse-zookeeper"

    clickhouse-04:
        image: yandex/clickhouse-server
        hostname: clickhouse-04
        container_name: clickhouse-04
        ports:
            - 9004:9000
        volumes:
                - ./config/clickhouse_config.xml:/etc/clickhouse-server/config.xml
                - ./config/clickhouse_metrika.xml:/etc/clickhouse-server/metrika.xml
                - ./config/macros/macros-04.xml:/etc/clickhouse-server/config.d/macros.xml
                - ./config/users.xml:/etc/clickhouse-server/users.xml
                # - ./data/server-04:/var/lib/clickhouse
        ulimits:
            nofile:
                soft: 262144
                hard: 262144
        depends_on:
            - "clickhouse-zookeeper"

    clickhouse-05:
        image: yandex/clickhouse-server
        hostname: clickhouse-05
        container_name: clickhouse-05
        ports:
            - 9005:9000
        volumes:
                - ./config/clickhouse_config.xml:/etc/clickhouse-server/config.xml
                - ./config/clickhouse_metrika.xml:/etc/clickhouse-server/metrika.xml
                - ./config/macros/macros-05.xml:/etc/clickhouse-server/config.d/macros.xml
                - ./config/users.xml:/etc/clickhouse-server/users.xml
                # - ./data/server-05:/var/lib/clickhouse
        ulimits:
            nofile:
                soft: 262144
                hard: 262144
        depends_on:
            - "clickhouse-zookeeper"

    clickhouse-06:
        image: yandex/clickhouse-server
        hostname: clickhouse-06
        container_name: clickhouse-06
        ports:
            - 9006:9000
        volumes:
                - ./config/clickhouse_config.xml:/etc/clickhouse-server/config.xml
                - ./config/clickhouse_metrika.xml:/etc/clickhouse-server/metrika.xml
                - ./config/macros/macros-06.xml:/etc/clickhouse-server/config.d/macros.xml
                - ./config/users.xml:/etc/clickhouse-server/users.xml
                # - ./data/server-06:/var/lib/clickhouse
        ulimits:
            nofile:
                soft: 262144
                hard: 262144
        depends_on:
            - "clickhouse-zookeeper"
networks:
    default:
        external:
            name: clickhouse-net
```

## Host 建立資料庫

```python
import clickhouse_driver
import pandas as pd


connection_settings = {
    'host': 'localhost',
    'port': '9911',
}

client = clickhouse_driver.Client(**connection_settings)

# 建立新資料庫
client.execute('CREATE DATABASE IF NOT EXISTS CRYPTO')

print(client.execute("SHOW DATABASES"))
client.execute('USE CRYPTO')

# 創建一個簡單的表格
df = pd.DataFrame({'name': ['Alice', 'Bob', 'Charlie']*3333, 'age': [25, 30, 35]*3333})
#df = pd.DataFrame({'name': ['Alice', 'Bob', 'Charlie'], 'age': [25, 30, 35]})

client.execute('CREATE TABLE IF NOT EXISTS test_table (name String, age Int32) ENGINE = Memory')
#client.execute('CREATE TABLE IF NOT EXISTS test_table (name String, age Int32) ENGINE = MergeTree PARTITION BY name ORDER BY age')


# 將資料框寫入表格
client.execute('INSERT INTO test_table VALUES', df.to_dict('records'))

# 讀取表格中的資料
result = client.execute('SELECT * FROM test_table')
print(result)

# 刪除表格
# client.execute('DROP TABLE IF EXISTS test_table')
```

