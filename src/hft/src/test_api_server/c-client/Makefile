# Makefile for C API Client
CC = gcc
CFLAGS = -Wall -Wextra -O3 -march=native -mtune=native -pthread -std=c11 -D_GNU_SOURCE -DNDEBUG
LDFLAGS = -lcurl -pthread -lm

# Target executable
TARGET = c_client

# Source files
SOURCES = c_client.c

# Object files
OBJECTS = $(SOURCES:.c=.o)

# Default target
all: $(TARGET)

# Build the executable
$(TARGET): $(OBJECTS)
	$(CC) $(OBJECTS) -o $(TARGET) $(LDFLAGS)

# Compile source files to object files
%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

# Clean build artifacts
clean:
	rm -f $(OBJECTS) $(TARGET)

# Run the client with default parameters
run: $(TARGET)
	./$(TARGET) 1000 100 100

# Run a quick test
test: $(TARGET)
	@echo "Running quick test with 10 orders..."
	./$(TARGET) 10 1 0
	@echo "Test completed successfully!"

# Debug build
debug: CFLAGS += -g -DDEBUG
debug: clean $(TARGET)

# Performance build with aggressive optimizations
perf: CFLAGS = -O3 -march=native -mtune=native -pthread -std=c11 -D_GNU_SOURCE -DNDEBUG
perf: clean $(TARGET)

# Help target
help:
	@echo "Available targets:"
	@echo "  make         - Build the C client"
	@echo "  make clean   - Remove build artifacts"
	@echo "  make run     - Build and run with default parameters (1000 orders)"
	@echo "  make test    - Build and run a quick test (10 orders)"
	@echo "  make debug   - Build with debug symbols"
	@echo "  make perf    - Build with aggressive optimizations"
	@echo "  make help    - Show this help message"

.PHONY: all clean run test debug perf help