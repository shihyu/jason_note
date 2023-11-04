## Docker 安裝 python 運行 local  python  script

```dockerfile
# 使用官方的Python 3.10鏡像作為基礎鏡像
FROM python:3.10

# 將當前目錄下的所有文件複製到容器的/app目錄
COPY . /app

# 設置工作目錄為/app
WORKDIR /app
```

```
docker build -t my-python-app .


docker run -v /本地文件的絕對路徑:/app my-python-app python /app/my_script.py
docker run -v /tmp/test_docker:/app my-python-app python my_script.py 
```

```python
# my_script.py 
print('hello')
```

