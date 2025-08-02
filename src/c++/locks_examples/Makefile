# Makefile for locks_guide examples
# 編譯所有鎖機制範例程式

CC = gcc
CXX = g++
CFLAGS = -Wall -Wextra -pthread -std=c99
CXXFLAGS = -Wall -Wextra -pthread -std=c++17

# Linux C examples
C_SOURCES = 01_pthread_mutex.c 02_semaphore.c 03_spinlock.c 04_rwlock.c 05_condition_variable.c
C_TARGETS = $(C_SOURCES:.c=)

# C++ examples  
CXX_SOURCES = 06_std_mutex.cpp 07_recursive_mutex.cpp 08_shared_mutex.cpp 09_condition_variable.cpp 10_atomic_basic.cpp 11_lockfree_queue.cpp 12_lock_comparison.cpp
CXX_TARGETS = $(CXX_SOURCES:.cpp=)

# All targets
ALL_TARGETS = $(C_TARGETS) $(CXX_TARGETS)

.PHONY: all clean test help linux cpp

# Default target
all: $(ALL_TARGETS)
	@echo "✅ 所有範例編譯完成!"
	@echo "可執行檔案: $(ALL_TARGETS)"

# Linux C examples
linux: $(C_TARGETS)
	@echo "✅ Linux C 範例編譯完成!"

# C++ examples
cpp: $(CXX_TARGETS)
	@echo "✅ C++ 範例編譯完成!"

# Individual C targets
$(C_TARGETS): %: %.c
	@echo "🔨 編譯 $<..."
	$(CC) $(CFLAGS) -o $@ $<

# Individual C++ targets  
$(CXX_TARGETS): %: %.cpp
	@echo "🔨 編譯 $<..."
	$(CXX) $(CXXFLAGS) -o $@ $<

# Test all examples
test: all
	@echo "🧪 測試所有範例..."
	@echo "\n=== Linux C Examples ==="
	@for target in $(C_TARGETS); do \
		echo "▶️  執行 $$target..."; \
		timeout 10s ./$$target || echo "⚠️  $$target 超時或錯誤"; \
		echo ""; \
	done
	@echo "\n=== C++ Examples ==="
	@for target in $(CXX_TARGETS); do \
		echo "▶️  執行 $$target..."; \
		timeout 10s ./$$target || echo "⚠️  $$target 超時或錯誤"; \
		echo ""; \
	done

# Quick test (shorter timeout)
quick-test: all
	@echo "⚡ 快速測試所有範例..."
	@for target in $(ALL_TARGETS); do \
		echo "▶️  $$target"; \
		timeout 3s ./$$target >/dev/null 2>&1 && echo "✅ OK" || echo "❌ FAIL"; \
	done

# Clean build artifacts
clean:
	@echo "🧹 清理編譯檔案..."
	rm -f $(ALL_TARGETS)
	@echo "✅ 清理完成!"

# Show build info
info:
	@echo "📋 編譯資訊:"
	@echo "C 編譯器: $(CC) $(CFLAGS)"
	@echo "C++ 編譯器: $(CXX) $(CXXFLAGS)"
	@echo "C 原始檔: $(C_SOURCES)"
	@echo "C++ 原始檔: $(CXX_SOURCES)" 
	@echo "所有目標: $(ALL_TARGETS)"

# Help message
help:
	@echo "📚 locks_guide 範例程式 Makefile"
	@echo ""
	@echo "🎯 可用目標:"
	@echo "  all        - 編譯所有範例 (預設)"
	@echo "  linux      - 只編譯 Linux C 範例"
	@echo "  cpp        - 只編譯 C++ 範例"
	@echo "  test       - 編譯並測試所有範例"
	@echo "  quick-test - 快速測試所有範例"
	@echo "  clean      - 清理編譯檔案"
	@echo "  info       - 顯示編譯資訊"
	@echo "  help       - 顯示此說明"
	@echo ""
	@echo "📝 範例列表:"
	@echo "  Linux C:"
	@printf "    %s\n" $(C_SOURCES)
	@echo "  C++:"
	@printf "    %s\n" $(CXX_SOURCES)
	@echo ""
	@echo "🚀 使用方法:"
	@echo "  make              # 編譯所有範例"
	@echo "  make test         # 編譯並測試"
	@echo "  make clean all    # 清理後重新編譯"
	@echo "  ./01_pthread_mutex # 執行特定範例"
