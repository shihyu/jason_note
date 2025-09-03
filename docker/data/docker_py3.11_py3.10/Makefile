# make build-and-run PYTHON_VERSION=3.11
# make build-and-run PYTHON_VERSION=3.10

build-and-run:
	docker build --build-arg PYTHON_VERSION=$(PYTHON_VERSION) -t myapp:$(PYTHON_VERSION) .
	docker run --name my-container myapp:$(PYTHON_VERSION)

exec-container:
	docker exec -it my-container bash

