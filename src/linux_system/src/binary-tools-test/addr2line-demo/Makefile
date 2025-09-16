CC = gcc
CXX = g++
CFLAGS = -g -O0 -fno-omit-frame-pointer -rdynamic -Wall
CXXFLAGS = -g -O0 -fno-omit-frame-pointer -rdynamic -Wall -std=c++11
LDFLAGS = -rdynamic

# 目標程序
TARGETS = segfault_demo backtrace_demo cpp_demo

# 構建所有目標
all: $(TARGETS)

# C 程序編譯規則
segfault_demo: segfault_demo.c
	$(CC) $(CFLAGS) $< -o $@ $(LDFLAGS)
	@echo "Built $@ with debug symbols"

backtrace_demo: backtrace_demo.c
	$(CC) $(CFLAGS) $< -o $@ $(LDFLAGS)
	@echo "Built $@ with debug symbols"

# C++ 程序編譯規則
cpp_demo: cpp_demo.cpp
	$(CXX) $(CXXFLAGS) $< -o $@ $(LDFLAGS)
	@echo "Built $@ with debug symbols"

# 運行測試
test: all
	@echo "=== Testing addr2line functionality ==="
	@./test_addr2line.sh

# 顯示函數地址
show-addresses: all
	@echo "=== Function Addresses ==="
	@echo "segfault_demo:"
	@nm segfault_demo | grep -E " T " | head -5
	@echo ""
	@echo "backtrace_demo:"
	@nm backtrace_demo | grep -E " T " | head -5
	@echo ""
	@echo "cpp_demo (demangled):"
	@nm -C cpp_demo | grep -E " T " | head -5

# 測試 addr2line
test-addr2line: segfault_demo
	@echo "=== Testing addr2line with segfault_demo ==="
	@echo "Getting function addresses..."
	@ADDR=$$(nm segfault_demo | grep " T main" | cut -d' ' -f1) && \
		echo "main address: 0x$$ADDR" && \
		echo "addr2line output:" && \
		addr2line -fe segfault_demo 0x$$ADDR
	@echo ""
	@ADDR=$$(nm segfault_demo | grep " T cause_segfault" | cut -d' ' -f1) && \
		echo "cause_segfault address: 0x$$ADDR" && \
		echo "addr2line output:" && \
		addr2line -fe segfault_demo 0x$$ADDR

# 測試 C++ demangling
test-cpp-addr2line: cpp_demo
	@echo "=== Testing addr2line with C++ symbols ==="
	@ADDR=$$(nm cpp_demo | grep "DebugHelper" | head -1 | cut -d' ' -f1) && \
		echo "Mangled symbol at: 0x$$ADDR" && \
		echo "Without demangling:" && \
		addr2line -fe cpp_demo 0x$$ADDR && \
		echo "With demangling (-C):" && \
		addr2line -Cfe cpp_demo 0x$$ADDR

# 生成崩潰並分析
crash-test: segfault_demo
	@echo "=== Generating crash for analysis ==="
	@echo "This will crash intentionally..."
	-./segfault_demo --crash 2>&1 | tee crash.log || true
	@echo "Check dmesg for segfault address:"
	@dmesg | tail -5 | grep -i segfault || echo "No segfault in dmesg"

# 清理
clean:
	rm -f $(TARGETS) *.o core core.* crash.log
	@echo "Cleaned all binaries and temporary files"

# 幫助信息
help:
	@echo "Available targets:"
	@echo "  all              - Build all demo programs"
	@echo "  test             - Run all tests"
	@echo "  show-addresses   - Show function addresses in binaries"
	@echo "  test-addr2line   - Test basic addr2line functionality"
	@echo "  test-cpp-addr2line - Test addr2line with C++ symbols"
	@echo "  crash-test       - Generate a crash and show how to analyze it"
	@echo "  clean            - Remove all built files"
	@echo ""
	@echo "Individual programs:"
	@echo "  segfault_demo    - Demo program that can cause segfault"
	@echo "  backtrace_demo   - Demo with backtrace functionality"
	@echo "  cpp_demo         - C++ demo with templates and namespaces"

.PHONY: all test show-addresses test-addr2line test-cpp-addr2line crash-test clean help