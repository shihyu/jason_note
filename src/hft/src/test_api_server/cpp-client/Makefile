# Makefile for C++ API Client
CXX = g++
CXXFLAGS = -std=c++17 -Wall -Wextra -O3 -march=native -mtune=native -pthread -DNDEBUG
LDFLAGS = -lcurl -pthread
HFT_LDFLAGS = -lcurl -pthread -lnuma

# Target executables (only the two comparison versions)
TARGETS = cpp_client_original cpp_client_hft

# Default target
all: $(TARGETS)

# Build the original optimized client (baseline)
cpp_client_original: cpp_client_original.cpp
	$(CXX) $(CXXFLAGS) $< -o $@ $(LDFLAGS)

# Build the HFT client with AVX2 and NUMA support
cpp_client_hft: cpp_client_hft.cpp
	$(CXX) $(CXXFLAGS) -mavx2 $< -o $@ $(HFT_LDFLAGS)

# Clean build artifacts
clean:
	rm -f $(TARGETS) *.o

# Run a quick test
test: $(TARGETS)
	@echo "=== Testing Original Optimized C++ Client ==="
	./cpp_client_original 100 10 10
	@echo ""
	@echo "=== Testing HFT C++ Client ==="
	./cpp_client_hft 100 8 10

# Compare performance between versions
compare: $(TARGETS)
	@echo "=== Running Performance Comparison ==="
	@echo ""
	@echo ">>> Original Optimized version:"
	./cpp_client_original 1000 50 100
	@echo ""
	@echo ">>> HFT version (with OS optimizations):"
	./cpp_client_hft 1000 8 100

# Debug build
debug: CXXFLAGS += -g -DDEBUG
debug: clean $(TARGETS)

# Help target
help:
	@echo "Available targets:"
	@echo "  make                      - Build both client versions"
	@echo "  make clean                - Remove build artifacts"
	@echo "  make test                 - Run a quick test"
	@echo "  make compare              - Compare performance between versions"
	@echo "  make debug                - Build with debug symbols"
	@echo "  make help                 - Show this help message"
	@echo ""
	@echo "Individual targets:"
	@echo "  make cpp_client_original  - Build original optimized client (baseline)"
	@echo "  make cpp_client_hft       - Build HFT client with all optimizations"

.PHONY: all clean test compare debug help