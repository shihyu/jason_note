## python 連接 redis

出處:https://cloud.tencent.com/developer/article/1892663

### redis 安裝

先確保redis 已經安裝並且啟動

(host port):(docker port)

```sh
docker pull redis:latest
docker run -itd --name redis-test -p 1234:6379 redis
```

```sh
docker ps
```

```sh
CONTAINER ID   IMAGE     COMMAND                  CREATED         STATUS         PORTS                                       NAMES
5ccd903da485   redis     "docker-entrypoint.s…"   6 minutes ago   Up 6 minutes   0.0.0.0:1234->6379/tcp, :::1234->6379/tcp   redis-test
```



進入docker容器

```sh
docker exec -it redis-test /bin/bash
```

進入容器後，可以使用redis-cli 命令`redis-cli SET key value`的值,`redis-cli GET key`取出對應的值

```sh
root@ec62efc510ce:/data# redis-cli SET yoyo "hello world"
OK
root@ec62efc510ce:/data# redis-cli GET yoyo              
"hello world"
```

經過簡單的測試，說明沒有問題

### python 連 reids

接著講下如何用 python 程式碼連上 redis [資料庫服務](https://cloud.tencent.com/product/dbexpert?from=10680)器。 先使用pip 安裝redis 驅動包

```sh
pip install redis
```

程式碼很簡單

```python
import redis
r = redis.StrictRedis(host='127.0.0.1', port=1234)
print(r.get('yoyo'))
```

運行結果是byte類型：`b'hello world'`，可以加個參數`decode_responses=True`,設定得到str字串

```python
import redis
r = redis.StrictRedis(host='127.0.0.1', port=1234, decode_responses=True)
print(r.get('yoyo'))
```

於是可以得到字串:`yoyo`

測試下set新增鍵值對，get取值，中文也是沒問題的

```python
import redis
r = redis.StrictRedis(host='127.0.0.1', port=1234, decode_responses=True)

# set 設定key-value
r.set("name", "上海-悠悠")
print(r.get("name"))
```

運行結果:上海-悠悠

當key不存在的時候，get()取值返回結果是None

##  Python Docker 容器與 Redis Docker 容器 連動

docker redis 安裝 

```sh
docker pull redis:latest
```

由於您的 Python Docker 容器與 Redis Docker 容器不在同一個 Docker 網路上，因此您需要將 Python Docker 容器加入相同的 Docker 網路。您可以使用以下命令創建一個名為 my-network 的 Docker 網路：
```sh
docker network create my-network
```

然後，您可以使用以下命令運行 Python Docker 容器，並將其加入 `my-network` 網路：

```sh
docker run -itd --name redis-test -p 1234:6379 --network my-network <image_name>  使用 docker images 查看

docker run -itd --name redis-test -p 1234:6379 --network my-network redis
```

### Build the python docker image:

- requirements.txt

```sh
requests
kafka-python
grpcio
protobuf
better-exceptions
loguru
pandas
python-binance
redis
aiohttp
flask
kubernetes
```

- Dockerfile

```sh
FROM python:3.11-slim

# Add requirements file in the container
COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

# Add source code in the container
COPY redis_test_script.py ./redis_test_script.py

# Define container entry point (could also work with CMD python main.py)
ENTRYPOINT ["python", "redis_test_script.py"]
```



在 Python 應用程式中使用 Redis 容器的 IP 位置，而不是使用 `127.0.0.1`。由於 Redis 容器的名稱為 `redis-test`，因此您可以使用以下程式碼來連接 Redis 服務：

- redis_test_script.py

```python
import redis
r = redis.StrictRedis(host='redis-test', port=6379, decode_responses=True)

# set 設定key-value
r.set("name", "上海-悠悠")
print(r.get("name"))
```

在這個命令中，-t 參數指定映像檔的名稱

```sh
docker build -t python-redis .
```

```sh
docker run -d --network=my-network --name my-db redis ...
docker run    --network=my-network python-redis ...
```

第一個指令 `docker run -d --network=my-network --name my-db redis ...` 是用來運行 Redis Docker 容器。這個指令中的 `--network=my-network` 參數表示將容器連接到 Docker 網路 `my-network` 中，因此其他 Docker 容器可以通過這個網路訪問 Redis 容器。 `--name my-db` 參數為容器指定了一個名稱 `my-db`，方便後續使用。`redis` 表示我們要使用的 Docker 映像檔名稱和版本。最後的 `...` 表示可以在這個命令後面加上其他的參數來運行 Redis 容器。

第二個指令 `docker run --network=my-network python-redis ...` 是用來運行 Python Docker 容器。這個指令中的 `--network=my-network` 參數表示將容器連接到 Docker 網路 `my-network` 中，這樣 Python 容器就可以通過這個網路訪問 Redis 容器。 `python-redis` 表示我們要使用的 Docker 映像檔名稱和版本。最後的 `...` 表示可以在這個命令後面加上其他的參數來運行 Python 容器。

在這兩個指令中，`--network` 參數用於指定容器所使用的 Docker 網路，讓不同的容器可以在同一個網路中進行通信。 `--name` 參數用於指定容器的名稱，方便後續使用。而最後的 `...` 可以用於指定其他的參數，例如指定容器運行的命令等等。

## Docker connect to host

```sh
docker build -t python-redis .

docker run --network=host -it  python-redis
```

Docker 容器內部的 Python 程式直接連接到宿主機器上運行的 Redis 服務。請注意，使用 `--network=host` 參數可能會降低容器的安全性，因為容器可以訪問宿主機器上的所有網路資源。因此，建議在必要時才使用這個參數。

```python
import redis

r = redis.StrictRedis(host='127.0.0.1', port=6379, decode_responses=True)
# set 設定key-value
r.set("name", "上海-悠悠 127.0.0.1")
print(r.get("name"))
```



