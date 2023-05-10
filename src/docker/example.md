## 在dockerfile中設定時區

基於 Debian 鏡像

由於 Debian 鏡像中已經包含了tzdata，因此設定時區的方法比較簡單，只需新增環境變數TZ即可。

```
FROM debian:stretch

ENV TZ=Asia/Taipei
```

基於 Alpine 鏡像

```
FROM alpine:3.9

ENV TZ=Asia/Taipei

RUN apk update \
    && apk add tzdata \
    && echo "${TZ}" > /etc/timezone \
    && ln -sf /usr/share/zoneinfo/${TZ} /etc/localtime \
    && rm /var/cache/apk/*
```

基於 Ubuntu 鏡像

```
FROM ubuntu:bionic

ENV TZ=Asia/Taipei

RUN echo "${TZ}" > /etc/timezone \
    && ln -sf /usr/share/zoneinfo/${TZ} /etc/localtime \
    && apt update \
    && apt install -y tzdata \
    && rm -rf /var/lib/apt/lists/*
```

## 簡單範例

```py
from pip import _internal
import time

if __name__ == '__main__':
    _internal.main(['list'])
    while True:
        print('Hello Docker world!')
        time.sleep(1)
```

```dockerfile
FROM python:3.10-slim

# Add requirements file in the container
COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

# Add source code in the container
COPY main.py ./main.py

# Define container entry point (could also work with CMD python main.py)
ENTRYPOINT ["python", "main.py"]
```

- requirements.txt
```
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

```sh
# 編譯 image
docker build -t my-image-name .  

# Run docker
docker run -it my-image-name

#查看 container_name or id
docker ps
79c7e6661fa2   my-image-name                     "python main.py"         54 seconds ago   Up 54 seconds                                                                                                    beautiful_khayyam

docker exec -it 79c7e6661fa2 /bin/bash
docker exec -it beautiful_khayyam /bin/bash
```

---

1. 使用命令行將上述 Dockerfile 文件保存在您的計算機上。

2. 創建 Docker 映像，請在命令行中導航到 Dockerfile 文件所在的目錄，並運行以下命令：

   ```sh
   docker build -t image_name .
   ```

   其中，`image_name` 是您要為映像命名的名稱，`.` 表示當前目錄是上下文。

3. 運行 Docker 映像，請使用以下命令：

   ```sh
   docker run -it --rm image_name
   ```

   其中，`-it` 表示要使用互動式終端來運行容器，`--rm` 表示當容器停止時，自動刪除容器。

4. 如果需要，在運行容器的情況下登入 Docker，請使用以下命令：

   ```sh
   docker exec -it container_name /bin/bash
   ```

   其中，`container_name` 是您要登入的容器的名稱，`/bin/bash` 是您要在容器中運行的命令。

希望這些命令可以幫助您成功編譯、運行和登入您的 Docker 映像。
