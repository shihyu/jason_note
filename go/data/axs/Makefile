


infra-up:
	docker-compose -f $(CURDIR)/deployment/local/docker-compose.infra.yaml up -d

infra-down:
	docker-compose -f $(CURDIR)/deployment/local/docker-compose.infra.yaml down

infra-restart:
	@docker-compose -f $(CURDIR)/deployment/local/docker-compose.infra.yaml down
	@docker-compose -f $(CURDIR)/deployment/local/docker-compose.infra.yaml up -d

svc-up:
	docker-compose -f $(CURDIR)/deployment/local/docker-compose.svc.yaml up -d

svc-down:
	docker-compose -f $(CURDIR)/deployment/local/docker-compose.svc.yaml down

svc-rebuild:
	@docker-compose -f $(CURDIR)/deployment/local/docker-compose.svc.yaml down
	@docker-compose -f $(CURDIR)/deployment/local/docker-compose.svc.yaml up -d --build

gen-proto:
	@protoc -I $(CURDIR)/pb/eventpb  --go_out=$(CURDIR)/pb/eventpb --go-grpc_out=$(CURDIR)/pb/eventpb --go_opt=paths=source_relative --go-grpc_opt=paths=source_relative $(CURDIR)/pb/eventpb/*.proto
	@protoc -I $(CURDIR)/pb/apipb  --go_out=$(CURDIR)/pb/apipb --go-grpc_out=$(CURDIR)/pb/apipb --go_opt=paths=source_relative --go-grpc_opt=paths=source_relative api.proto $(CURDIR)/pb/apipb/*.proto

migrate-create:
	goose -dir $(CURDIR)/migration/db create $(m) sql

build-setup-image:
	docker build -f $(CURDIR)/Dockerfile.setup -t axs-setup:latest .

build-axs-image:
	docker build -f $(CURDIR)/Dockerfile -t axs-app:latest .

local-run-consumer:
	CONSUMER_ORDINAL=$(ORDINAL) go run $(CURDIR)/main.go consumer

local-run-grpc:
	go run $(CURDIR)/main.go grpc

build:
	go build  -o axs-app ./main.go

test:
	go test ./... -count=1 -p=1