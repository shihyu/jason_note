# FFI 範例 Makefile
# 支援 Linux, macOS 和 Windows (使用 MinGW)

# 偵測作業系統
UNAME_S := $(shell uname -s)
ifeq ($(UNAME_S),Linux)
    SO_EXT := so
    LDFLAGS := -shared -fPIC
    RUST_TARGET := 
endif
ifeq ($(UNAME_S),Darwin)
    SO_EXT := dylib
    LDFLAGS := -shared -fPIC
    RUST_TARGET := 
endif
ifeq ($(OS),Windows_NT)
    SO_EXT := dll
    LDFLAGS := -shared
    RUST_TARGET := 
endif

# 編譯器
CC := gcc
CXX := g++
PYTHON := python3

# 路徑
C_LIBS_DIR := c_libs
PYTHON_DIR := python
RUST_FFI_DIR := rust_libs/rust_ffi
RUST_LIB_DIR := rust_libs/rust_lib

# 目標
C_LIB := $(C_LIBS_DIR)/libmath.$(SO_EXT)
CPP_LIB := $(C_LIBS_DIR)/libcpp_wrapper.$(SO_EXT)
RUST_LIB := $(RUST_LIB_DIR)/target/release/librust_lib.$(SO_EXT)

# 顏色輸出
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[1;33m
NC := \033[0m # No Color

.PHONY: all clean test build build-c build-cpp build-rust test-python test-rust help

# 預設目標
all: build test

help:
	@echo "$(GREEN)FFI 範例 Makefile$(NC)"
	@echo "================================"
	@echo "可用的目標："
	@echo "  $(YELLOW)make all$(NC)        - 編譯所有程式並執行測試"
	@echo "  $(YELLOW)make build$(NC)      - 編譯所有函式庫"
	@echo "  $(YELLOW)make test$(NC)       - 執行所有測試"
	@echo "  $(YELLOW)make clean$(NC)      - 清理所有編譯產物"
	@echo ""
	@echo "個別目標："
	@echo "  $(YELLOW)make build-c$(NC)    - 編譯 C 函式庫"
	@echo "  $(YELLOW)make build-cpp$(NC)  - 編譯 C++ 函式庫"
	@echo "  $(YELLOW)make build-rust$(NC) - 編譯 Rust 函式庫"
	@echo "  $(YELLOW)make test-python$(NC)- 執行 Python 測試"
	@echo "  $(YELLOW)make test-rust$(NC)  - 執行 Rust 測試"

# 編譯所有
build: build-c build-cpp build-rust
	@echo "$(GREEN)✓ 所有函式庫編譯完成！$(NC)"

# 編譯 C 函式庫
build-c: $(C_LIB)

$(C_LIB): $(C_LIBS_DIR)/math_lib.c $(C_LIBS_DIR)/math_lib.h
	@echo "$(YELLOW)編譯 C 函式庫...$(NC)"
	$(CC) $(LDFLAGS) -o $@ $(C_LIBS_DIR)/math_lib.c
	@echo "$(GREEN)✓ C 函式庫編譯完成$(NC)"

# 編譯 C++ 函式庫
build-cpp: $(CPP_LIB)

$(CPP_LIB): $(C_LIBS_DIR)/cpp_wrapper.cpp $(C_LIB)
	@echo "$(YELLOW)編譯 C++ 函式庫...$(NC)"
	$(CXX) $(LDFLAGS) -o $@ $(C_LIBS_DIR)/cpp_wrapper.cpp -L$(C_LIBS_DIR) -lmath -std=c++11
	@echo "$(GREEN)✓ C++ 函式庫編譯完成$(NC)"

# 編譯 Rust 函式庫
build-rust: build-rust-lib build-rust-ffi

build-rust-lib:
	@echo "$(YELLOW)編譯 Rust 函式庫...$(NC)"
	cd $(RUST_LIB_DIR) && cargo build --release
	@echo "$(GREEN)✓ Rust 函式庫編譯完成$(NC)"

build-rust-ffi: $(C_LIB)
	@echo "$(YELLOW)編譯 Rust FFI 範例...$(NC)"
	cd $(RUST_FFI_DIR) && cargo build --release
	@echo "$(GREEN)✓ Rust FFI 範例編譯完成$(NC)"

# 執行所有測試
test: build test-python test-rust
	@echo ""
	@echo "$(GREEN)================================$(NC)"
	@echo "$(GREEN)✅ 所有 FFI 測試通過！$(NC)"
	@echo "$(GREEN)================================$(NC)"

# Python 測試
test-python: test-python-c test-python-rust test-python-cpp

test-python-c: $(C_LIB)
	@echo ""
	@echo "$(YELLOW)執行 Python 調用 C 測試...$(NC)"
	@echo "================================"
	cd $(PYTHON_DIR) && $(PYTHON) python_ffi.py
	@echo ""

test-python-rust: build-rust-lib
	@echo ""
	@echo "$(YELLOW)執行 Python 調用 Rust 測試...$(NC)"
	@echo "================================"
	cd $(PYTHON_DIR) && $(PYTHON) python_call_rust.py
	@echo ""

test-python-cpp: $(CPP_LIB)
	@echo ""
	@echo "$(YELLOW)執行 Python 調用 C++ 測試...$(NC)"
	@echo "================================"
	cd $(PYTHON_DIR) && LD_LIBRARY_PATH=../$(C_LIBS_DIR):$$LD_LIBRARY_PATH /usr/bin/python3 python_call_cpp.py || \
		(echo "$(YELLOW)嘗試使用系統 Python...$(NC)" && /usr/bin/python3 python_call_cpp.py)
	@echo ""

# Rust 測試
test-rust: $(C_LIB)
	@echo ""
	@echo "$(YELLOW)執行 Rust 調用 C 測試...$(NC)"
	@echo "================================"
	cd $(RUST_FFI_DIR) && LD_LIBRARY_PATH=../../$(C_LIBS_DIR):$$LD_LIBRARY_PATH cargo run
	@echo ""

# 清理
clean:
	@echo "$(YELLOW)清理編譯產物...$(NC)"
	rm -f $(C_LIBS_DIR)/*.$(SO_EXT)
	rm -f $(C_LIBS_DIR)/*.dll
	rm -f $(C_LIBS_DIR)/*.dylib
	rm -f $(C_LIBS_DIR)/*.so
	cd $(RUST_LIB_DIR) && cargo clean
	cd $(RUST_FFI_DIR) && cargo clean
	rm -rf $(PYTHON_DIR)/__pycache__
	@echo "$(GREEN)✓ 清理完成$(NC)"

# 個別清理目標
clean-c:
	rm -f $(C_LIB)

clean-cpp:
	rm -f $(CPP_LIB)

clean-rust:
	cd $(RUST_LIB_DIR) && cargo clean
	cd $(RUST_FFI_DIR) && cargo clean

clean-python:
	rm -rf $(PYTHON_DIR)/__pycache__

# 安裝依賴（可選）
install-deps:
	@echo "$(YELLOW)檢查依賴...$(NC)"
	@which gcc > /dev/null || (echo "$(RED)需要安裝 gcc$(NC)" && exit 1)
	@which g++ > /dev/null || (echo "$(RED)需要安裝 g++$(NC)" && exit 1)
	@which cargo > /dev/null || (echo "$(RED)需要安裝 Rust/Cargo$(NC)" && exit 1)
	@which python3 > /dev/null || (echo "$(RED)需要安裝 Python 3$(NC)" && exit 1)
	@echo "$(GREEN)✓ 所有依賴已安裝$(NC)"

# 顯示環境資訊
info:
	@echo "$(GREEN)系統資訊：$(NC)"
	@echo "  作業系統: $(UNAME_S)"
	@echo "  函式庫副檔名: .$(SO_EXT)"
	@echo "  C 編譯器: $(CC)"
	@echo "  C++ 編譯器: $(CXX)"
	@echo "  Python: $(PYTHON)"
	@echo ""
	@echo "$(GREEN)版本資訊：$(NC)"
	@$(CC) --version | head -n1
	@$(CXX) --version | head -n1
	@cargo --version
	@$(PYTHON) --version