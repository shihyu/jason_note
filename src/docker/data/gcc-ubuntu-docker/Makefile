# Docker image name
IMAGE_NAME = my-gcc-image

# Dockerfile path
DOCKERFILE = Dockerfile

# Build Docker image
build:
	docker build -t $(IMAGE_NAME) .

# Run Docker container with bash
run:
	docker run -it --rm $(IMAGE_NAME) /bin/bash

# Default target
.PHONY: build run

