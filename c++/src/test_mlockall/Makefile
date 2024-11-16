CC = gcc
CFLAGS = -Wall -O2
TARGET = mlockall_test
SRCS = mlockall_test.c
PERF = perf stat -e page-faults,major-faults,minor-faults,cpu-migrations,context-switches

.PHONY: all clean test test-normal test-mlockall

all: $(TARGET)

$(TARGET): $(SRCS)
	$(CC) $(CFLAGS) -o $@ $^

clean:
	rm -f $(TARGET)

# 執行不使用 mlockall 的測試
test-normal:
	@echo "\n=== Running test without mlockall ==="
	@sudo $(PERF) ./$(TARGET)

# 執行使用 mlockall 的測試
test-mlockall:
	@echo "\n=== Running test with mlockall ==="
	@sudo $(PERF) ./$(TARGET) -m

# 執行兩種測試並比較
test: $(TARGET) test-normal test-mlockall
	@echo "\n=== Test completed ==="

# 顯示幫助資訊
help:
	@echo "Available targets:"
	@echo "  make          - Build the test program"
	@echo "  make test     - Run both tests (with and without mlockall)"
	@echo "  make clean    - Remove built files"
	@echo "  make help     - Show this help message"
	@echo "\nIndividual test targets:"
	@echo "  make test-normal   - Test without mlockall"
	@echo "  make test-mlockall - Test with mlockall"
