# Makefile for HFT-Optimized C Client

CC = gcc
CFLAGS = -O3 -march=native -mtune=native -Wall -Wextra -std=gnu11
CFLAGS += -mavx2 -mfma  # Enable AVX2 and FMA instructions
LDFLAGS = -lcurl -lpthread -lnuma -lm

TARGET = c_client_hft
TARGET_SIMPLE = c_client_simple_hft
SRC = c_client_hft.c
SRC_SIMPLE = c_client_simple_hft.c

.PHONY: all clean test check-deps simple

all: check-deps $(TARGET_SIMPLE)

simple: check-deps $(TARGET_SIMPLE)

$(TARGET): $(SRC)
	@echo "Building HFT-optimized C client (full version)..."
	$(CC) $(CFLAGS) -o $(TARGET) $(SRC) $(LDFLAGS)
	@echo "✓ Build complete: $(TARGET)"

$(TARGET_SIMPLE): $(SRC_SIMPLE)
	@echo "Building HFT-optimized C client (simple version)..."
	$(CC) $(CFLAGS) -o $(TARGET_SIMPLE) $(SRC_SIMPLE) $(LDFLAGS)
	@echo "✓ Build complete: $(TARGET_SIMPLE)"
	@echo ""
	@echo "Optional: Set capabilities to run without sudo:"
	@echo "  sudo setcap cap_ipc_lock+ep ./$(TARGET_SIMPLE)"

check-deps:
	@echo "Checking dependencies..."
	@which gcc > /dev/null || (echo "Error: gcc not found" && exit 1)
	@pkg-config --exists libcurl || (echo "Error: libcurl-dev not found. Install: sudo apt-get install libcurl4-openssl-dev" && exit 1)
	@ldconfig -p | grep libnuma > /dev/null || (echo "Error: libnuma not found. Install: sudo apt-get install libnuma-dev" && exit 1)
	@echo "✓ All dependencies found"

test: $(TARGET_SIMPLE)
	@echo "Running quick test (100 orders, 10 connections, 10 warmup)..."
	./$(TARGET_SIMPLE) 100 10 10

clean:
	rm -f $(TARGET) $(TARGET_SIMPLE) *.o

install-caps: $(TARGET_SIMPLE)
	sudo setcap cap_ipc_lock+ep ./$(TARGET_SIMPLE)
	@echo "✓ Capabilities set. You can now run without sudo"