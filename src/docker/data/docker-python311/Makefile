# Define the container name
CONTAINER_NAME=my-container

build:
	docker build -t my-image .

run:
	docker run -it --rm --name $(CONTAINER_NAME) my-image

exec:
	docker exec -it $(CONTAINER_NAME) /bin/bash
