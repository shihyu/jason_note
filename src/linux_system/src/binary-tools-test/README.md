# Linux Binary Tools Test Suite with Makefile

## 概述
這是一個完整的 Linux 二進制工具測試套件，使用 Makefile 自動化測試所有範例。

## 快速開始

```bash
# 顯示幫助
make help

# 檢查工具可用性
make check-tools

# 建置並測試所有內容
make all

# 只建置
make build-all

# 只測試
make test-all

# 清理
make clean
```

## 目錄結構

```
binary-tools-test/
├── Makefile              # 主 Makefile
├── core-tools/           # 核心二進制分析工具測試
│   └── Makefile
├── static-lib/           # 靜態庫測試
│   └── Makefile
├── dynamic-lib/          # 動態庫測試
│   └── Makefile
├── dlopen-demo/          # dlopen 和插件系統測試
│   ├── Makefile
│   └── plugins/          # 插件目錄
└── README.md             # 本文件
```

## 各模組測試

### 1. Core Tools (核心工具)
```bash
cd core-tools
make all          # 建置所有測試程式
make test         # 執行基本測試
make analysis     # 進階分析
make profile      # 性能分析 (gprof)
make trace        # 系統調用追蹤
```

### 2. Static Library (靜態庫)
```bash
cd static-lib
make all          # 建置靜態庫和測試程式
make test         # 執行測試
make analysis     # 詳細分析
make compare      # 比較不同鏈接方法
```

### 3. Dynamic Library (動態庫)
```bash
cd dynamic-lib
make all          # 建置動態庫和測試程式
make test         # 執行測試
make analysis     # 庫分析
make ld-test      # 測試 LD 環境變數
make rpath-test   # 測試 RPATH/RUNPATH
```

### 4. dlopen and Plugins (動態加載和插件)
```bash
cd dlopen-demo
make all          # 建置所有程式和插件
make test         # 執行測試
make analysis     # 插件系統分析
make advanced-test # 進階 dlopen 功能
make plugin-dev   # 插件開發測試
```

## 主要功能測試

### ✅ 已驗證功能

| 類別 | 工具/功能 | 狀態 |
|------|-----------|------|
| **核心工具** | nm, objdump, readelf, strings, file, size | ✅ |
| **靜態庫** | ar, ranlib, 靜態鏈接 | ✅ |
| **動態庫** | SONAME, 符號可見性, 構造/析構函數 | ✅ |
| **動態鏈接** | ldd, ldconfig, LD_LIBRARY_PATH, RPATH | ✅ |
| **動態加載** | dlopen, dlsym, dlclose, 插件系統 | ✅ |
| **調試工具** | strace, gprof, 安全特性檢查 | ✅ |
| **LD 環境** | LD_DEBUG, LD_PRELOAD, LD_BIND_NOW | ✅ |

## 進階測試

### 性能分析
```bash
# 使用 gprof
make -C core-tools profile

# 查看統計
make test-all VERBOSE=1
```

### 安全特性檢查
```bash
# 檢查二進制安全特性
make -C core-tools analysis
```

### LD 環境變數測試
```bash
# 完整 LD 測試
make -C dynamic-lib ld-test
```

## 常見問題

### 1. ltrace 未安裝
```bash
sudo apt-get install ltrace
```

### 2. valgrind 未安裝
```bash
sudo apt-get install valgrind
```

### 3. Makefile 警告
動態庫 Makefile 可能出現符號覆蓋警告，這是正常的，不影響功能。

## 測試驗證

所有測試都已通過驗證：
- ✅ 核心二進制分析工具
- ✅ 靜態庫創建和鏈接
- ✅ 動態庫版本控制
- ✅ dlopen 動態加載
- ✅ 插件系統架構
- ✅ LD 環境變數功能

## 相關文件
- [Linux Binary Tools Guide](../../linux-binary-tools-guide.md)
- [TEST_REPORT.md](TEST_REPORT.md)

## 使用建議

1. **開發新功能**：複製相關 Makefile 模板
2. **調試問題**：使用 `make analysis` 進行深入分析
3. **性能優化**：使用 `make profile` 進行性能分析
4. **安全檢查**：檢查 RELRO, Stack Canary, NX, PIE 等特性

## License
Educational purposes only.