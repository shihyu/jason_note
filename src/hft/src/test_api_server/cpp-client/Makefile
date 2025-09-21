# Makefile for C++ API Client
CXX = g++
CXXFLAGS = -std=c++17 -Wall -Wextra -O3 -march=native -mtune=native -pthread -DNDEBUG
LDFLAGS = -lcurl -pthread
HFT_LDFLAGS = -lcurl -pthread -lnuma

# Target executable
TARGETS = cpp_client_hft

# Default target
all: $(TARGETS)

# Build the HFT client with AVX2 and NUMA support
cpp_client_hft: cpp_client_hft.cpp
	$(CXX) $(CXXFLAGS) -mavx2 $< -o $@ $(HFT_LDFLAGS)

# Clean build artifacts
clean:
	rm -f $(TARGETS) *.o

# Run a quick test
test: $(TARGETS)
	@echo "=== Testing HFT C++ Client ==="
	./cpp_client_hft 100 8 10

# Run performance test
performance: $(TARGETS)
	@echo "=== Running Performance Test ==="
	@echo ""
	@echo ">>> HFT version (with OS optimizations):"
	./cpp_client_hft 1000 8 100

# Debug build
debug: CXXFLAGS += -g -DDEBUG
debug: clean $(TARGETS)

# Help target
help:
	@echo "Available targets:"
	@echo "  make                      - Build HFT client"
	@echo "  make clean                - Remove build artifacts"
	@echo "  make test                 - Run a quick test"
	@echo "  make performance          - Run performance test"
	@echo "  make debug                - Build with debug symbols"
	@echo "  make help                 - Show this help message"
	@echo ""
	@echo "Individual target:"
	@echo "  make cpp_client_hft       - Build HFT client with all optimizations"

.PHONY: all clean test performance debug help