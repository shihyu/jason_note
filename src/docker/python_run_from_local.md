## Docker 安裝 python 運行 local  python  script

```dockerfile
# 使用官方的Python 3.10镜像作为基础镜像
FROM python:3.10

# 将当前目录下的所有文件复制到容器的/app目录
COPY . /app

# 设置工作目录为/app
WORKDIR /app
```

```
docker build -t my-python-app .


docker run -v /本地文件的绝对路径:/app my-python-app python /app/my_script.py
docker run -v /tmp/test_docker:/app my-python-app python my_script.py 
```

```python
# my_script.py 
print('hello')
```

