

# Hello Docker



- Dockerfile

```sh
FROM python:3.7-slim

# Add requirements file in the container
COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

# Add source code in the container
COPY main.py ./main.py

# Define container entry point (could also work with CMD python main.py)
ENTRYPOINT ["python", "main.py"]

```

- requirements.txt

```sh
requests==2.27.1
```

- main.py

```python
from pip import _internal

if __name__ == '__main__':
    print('Hello Docker world!')
    _internal.main(['list'])
```



```sh
docker build -t docker-python-helloworld .
docker images 
# docker create -i -t --name 光碟機  iso
docker create -i -t --name  docker_test docker-python-helloworld
docker ps
docker start -i docker_test
docker stop docker_test
```

