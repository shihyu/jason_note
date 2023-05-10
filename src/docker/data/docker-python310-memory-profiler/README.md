docker build -t docker-python-helloworld .
docker images 
# docker create -i -t --name 光碟機  iso
docker create -i -t --name  docker_test docker-python-helloworld
docker ps
docker start -i docker_test
docker stop docker_test
