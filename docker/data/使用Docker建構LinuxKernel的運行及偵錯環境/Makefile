IMAGE_NAME = linux-builder
IMAGE_VERSION = latest
WORKDIR = $(HOME)/linux

.PHONY: build run

build:
	docker build -t $(IMAGE_NAME):$(IMAGE_VERSION) .

build_kernel:
	docker run -it --rm -v $(WORKDIR):/workspace $(IMAGE_NAME):$(IMAGE_VERSION) bash build-kernel.sh

run: 
	docker run -it -v $(WORKDIR):/workspace $(IMAGE_NAME):$(IMAGE_VERSION) 

clean:
	docker rmi -f $(IMAGE_NAME) || true

.DEFAULT_GOAL := help

help:
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  build     Build the Docker image"
	@echo "  run       Run the Docker container"
	@echo "  clean     Remove the Docker container and image"
	@echo "  help      Display this help message"
