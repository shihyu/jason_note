build-python3.11:
	docker build --build-arg PYTHON_VERSION=3.11 -t myapp:3.11 .

build-python3.10:
	docker build --build-arg PYTHON_VERSION=3.10 -t myapp:3.10 .

run-container-python3.11:
	docker run --name my-container myapp:3.11

run-container-python3.10:
	docker run --name my-container myapp:3.10

exec-container:
	docker exec -it my-container bash

