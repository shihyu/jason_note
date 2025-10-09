# llama.cpp GDB 測試

測試 llama.cpp 的 4 個核心 .so 函式庫,使用 gdb 中斷追蹤。

## 檔案說明

- `test_4_so.c` - 測試程式,呼叫 4 個 .so 的函數
- `test_final.sh` - GDB 測試腳本
- `Makefile` - 編譯配置

## 測試的函式庫

1. **libggml.so** - `ggml_backend_load_all()`
2. **libllama.so** - `llama_model_default_params()`
3. **libggml-base.so** - `ggml_init()`
4. **libggml-cpu.so** - `ggml_backend_cpu_init()`

## 使用方式

### 完整流程 (推薦)

```bash
# 一鍵編譯和測試
./build_and_test.sh
```

這個腳本會自動:
1. 建立 build 目錄
2. 執行 cmake (Debug 模式)
3. 編譯整個專案
4. 編譯測試程式
5. 執行 gdb 測試

### 僅測試 (已編譯過)

```bash
# 編譯測試程式
make

# 執行測試
make test

# 清理
make clean

# 手動執行
./test_final.sh
```

## 必要條件

- gdb 已安裝
- LD_LIBRARY_PATH 自動設定為 `../build/bin`

## 輸出範例

```
✓ [1/4] libggml.so
✓ [2/4] libllama.so
✓ [3/4] libggml-base.so
✓ [4/4] libggml-cpu.so
```

每個測試會顯示 backtrace 和函式庫載入資訊。
