# 1. 抓取基底image: redis
FROM redis:6-alpine3.15 

# 2. 基於redis image, 開始安裝 python 相關環境與套件
RUN apk add --update --no-cache python3 && ln -sf python3 /usr/bin/python
RUN python3 -m ensurepip
RUN pip3 install --no-cache --upgrade pip setuptools
RUN pip install --no-cache-dir redis