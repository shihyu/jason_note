#up：啟動 Docker 組合。
#down：停止 Docker 組合。
#logs：顯示 Docker 組合的日誌。
#redis-cli：啟動 Redis 容器的 CLI。
#build：編譯映像。
REDIS_COMPOSE = docker-compose.yml
REDIS_CONTAINER = shioaji
IMAGE_NAME = docker-shioaji

.PHONY: up down logs redis-cli exec build

up:
	@docker-compose -f $(REDIS_COMPOSE) up -d

down:
	@docker-compose -f $(REDIS_COMPOSE) down

logs:
	@docker-compose -f $(REDIS_COMPOSE) logs -f

redis-cli:
	@docker exec -it $(REDIS_CONTAINER) redis-cli

exec:
	@docker exec -it $(REDIS_CONTAINER) /bin/bash

build:
	docker build -t $(IMAGE_NAME) .
