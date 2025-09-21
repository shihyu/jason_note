# Makefile for C++ API Client
CXX = g++
CXXFLAGS = -std=c++17 -Wall -Wextra -O3 -march=native -mtune=native -pthread -DNDEBUG
LDFLAGS = -lcurl -pthread

# Target executable
TARGET = cpp_client

# Source files
SOURCES = cpp_client.cpp

# Object files
OBJECTS = $(SOURCES:.cpp=.o)

# Default target
all: $(TARGET)

# Build the executable
$(TARGET): $(OBJECTS)
	$(CXX) $(OBJECTS) -o $(TARGET) $(LDFLAGS)

# Compile source files to object files
%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

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
debug: CXXFLAGS += -g -DDEBUG
debug: clean $(TARGET)

# Help target
help:
	@echo "Available targets:"
	@echo "  make         - Build the C++ client"
	@echo "  make clean   - Remove build artifacts"
	@echo "  make run     - Build and run with default parameters (1000 orders)"
	@echo "  make test    - Build and run a quick test (10 orders)"
	@echo "  make debug   - Build with debug symbols"
	@echo "  make help    - Show this help message"

.PHONY: all clean run test debug help