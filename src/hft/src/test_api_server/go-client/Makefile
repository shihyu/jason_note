# Makefile for Go client

# Go compiler
GO := go

# Binary name
BINARY := go_client

# Build flags
GOFLAGS := -ldflags="-s -w"
# Compiler optimizations
GCFLAGS := -gcflags="-N -l"  # Disable optimizations for debug
GCFLAGS_OPT := -gcflags="all=-N=0 -l=0"  # Enable optimizations

# Default target
all: build

# Build the binary (with optimizations for fair comparison)
build:
	GOARCH=amd64 GOOS=linux CGO_ENABLED=0 $(GO) build -a $(GOFLAGS) -o $(BINARY) go_client.go

# Build with maximum optimization
release:
	GOARCH=amd64 GOOS=linux CGO_ENABLED=0 $(GO) build -a $(GOFLAGS) -o $(BINARY) go_client.go

# Run tests with default parameters
test: build
	./$(BINARY) --orders 100 --connections 10 --warmup 10

# Run full performance test
perf: build
	./$(BINARY) --orders 1000 --connections 100 --warmup 100

# Clean build artifacts
clean:
	rm -f $(BINARY)
	$(GO) clean

# Format the code
fmt:
	$(GO) fmt ./...

# Run go vet
vet:
	$(GO) vet ./...

# Install dependencies
deps:
	$(GO) mod download

.PHONY: all build release test perf clean fmt vet deps