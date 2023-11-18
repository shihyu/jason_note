.PHONY: up down

up: rebuild
	docker-compose -f docker-compose.local.yml up

down:
	docker-compose -f docker-compose.local.yml down

rebuild:
	docker-compose -f docker-compose.local.yml build
