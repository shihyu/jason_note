# 定義一些變量
DOCKER_COMPOSE = docker-compose
CLICKHOUSE_CONTAINER = my_clickhouse
MAIN_CONTAINER = my_main_app
SERVICE = main

# 幫助信息
.PHONY: help
help:
	@echo "可用的目標："
	@echo "  build        - 構建 Docker 映像"
	@echo "  up           - 啟動 Docker 容器"
	@echo "  down         - 停止 Docker 容器"
	@echo "  logs         - 查看服務日誌"
	@echo "  restart      - 重啟服務"
	@echo "  clean        - 清理未使用的 Docker 資源"
	@echo "  exec-clickhouse - 進入 ClickHouse 容器並啟動 Bash"
	@echo "  exec-main    - 進入主應用容器並啟動 Bash"

# 構建 Docker 映像
.PHONY: build
build:
	$(DOCKER_COMPOSE) build

# 啟動 Docker 容器
.PHONY: up
up:
	$(DOCKER_COMPOSE) up -d

# 停止 Docker 容器
.PHONY: down
down:
	$(DOCKER_COMPOSE) down

# 查看服務日誌
.PHONY: logs
logs:
	$(DOCKER_COMPOSE) logs -f $(SERVICE)

# 重啟服務
.PHONY: restart
restart:
	$(DOCKER_COMPOSE) restart $(SERVICE)

# 清理未使用的 Docker 資源
.PHONY: clean
clean:
	docker system prune -f

# 進入 ClickHouse 容器並啟動 Bash
.PHONY: exec-clickhouse
exec-clickhouse:
	docker exec -it $(CLICKHOUSE_CONTAINER) bash

# 進入主應用容器並啟動 Bash
.PHONY: exec-main
exec-main:
	docker exec -it $(MAIN_CONTAINER) bash

