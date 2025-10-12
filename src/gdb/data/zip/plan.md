# 使用 GDB 調試 zip 程式碼專案計畫

## 任務目標
建立可使用 GDB 調試的 zip 程式編譯環境,方便進行程式碼追蹤與除錯分析。

## 專案資訊
- **專案類型**: R package with C extensions (zip 壓縮庫)
- **主要程式碼**:
  - `src/zip.c` - 核心 zip/unzip 功能
  - `src/miniz.c` - miniz 壓縮庫
  - `src/tools/cmdzip.c` - 命令列 zip 工具
  - `src/tools/cmdunzip.c` - 命令列 unzip 工具
- **編譯器**: gcc 13.3.0

## 預期產出

### 1. 編譯產物
- **可執行檔 (附除錯符號)**:
  - `tests/cmdzip_debug` - 可用 GDB 調試的 zip 工具
  - `tests/cmdunzip_debug` - 可用 GDB 調試的 unzip 工具
- **編譯腳本**:
  - `tests/build_debug.sh` - 自動化編譯除錯版本的腳本

### 2. 測試與驗證檔案
- `tests/test_data/` - 測試用的資料檔案目錄
- `tests/gdb_commands.txt` - GDB 常用命令參考
- `tests/debug_example.sh` - 示範如何用 GDB 追蹤程式碼的腳本

### 3. 文件產出
- `tests/DEBUG_GUIDE.md` - 除錯指南文件

## Build/Debug/Test 指令

### 編譯除錯版本
```bash
# 編譯附帶除錯符號的程式 (在 tests/ 目錄執行)
cd tests
bash build_debug.sh
```

### GDB 除錯指令
```bash
# 基本除錯
gdb ./tests/cmdzip_debug

# 帶參數除錯
gdb --args ./tests/cmdzip_debug test.zip file1.txt file2.txt

# 使用 GDB 命令檔
gdb -x tests/gdb_commands.txt ./tests/cmdzip_debug
```

### 測試指令
```bash
# 執行除錯版本功能測試
cd tests
bash debug_example.sh
```

## 驗收標準

### 必要條件
1. ✅ 編譯成功產生附除錯符號的執行檔 (`-g -O0` flags)
2. ✅ 可使用 GDB 載入並顯示原始碼
3. ✅ 可在關鍵函數設定中斷點 (例: `zip_zip`, `zip_unzip`, `main`)
4. ✅ 可單步執行並檢視變數值
5. ✅ 可追蹤函數呼叫堆疊 (backtrace)

### 加分項目
- ✅ 提供常用 GDB 命令參考檔案
- ✅ 示範腳本展示如何追蹤 zip/unzip 流程
- ✅ 除錯指南文件說明如何分析特定問題

## 子任務拆解

### Phase 1: 環境準備與分析 (15min)
- [x] 檢查專案結構與相依性
- [ ] 分析現有的編譯設定 (`src/Makevars`, `src/Makevars.win`)
- [ ] 確認 GCC 與 GDB 版本

### Phase 2: 建立編譯腳本 (20min)
- [ ] 撰寫 `tests/build_debug.sh` 編譯腳本
  - 包含 `-g -O0 -Wall` 編譯選項
  - 連結所需的 C 檔案 (zip.c, miniz.c, unixutils.c 等)
  - 輸出到 `tests/` 目錄
- [ ] 測試編譯腳本是否正常運作
- [ ] 驗證產生的執行檔包含除錯符號 (`file` 命令檢查)

### Phase 3: GDB 測試與驗證 (15min)
- [ ] 使用 GDB 載入程式並設定中斷點
- [ ] 測試基本除錯功能:
  - 設定中斷點在 `main`, `zip_zip`, `zip_unzip`
  - 單步執行 (step, next)
  - 檢視變數 (print, display)
  - 檢視呼叫堆疊 (backtrace)

### Phase 4: 建立除錯輔助檔案 (20min)
- [ ] 建立 `tests/gdb_commands.txt` - GDB 命令範例
- [ ] 建立 `tests/debug_example.sh` - 示範除錯流程
- [ ] 準備測試資料 `tests/test_data/` (簡單的文字檔)

### Phase 5: 文件撰寫 (15min)
- [ ] 撰寫 `tests/DEBUG_GUIDE.md`
  - 如何編譯除錯版本
  - 如何使用 GDB 追蹤程式碼
  - 常見除錯情境範例
  - 關鍵函數說明

## 關鍵技術點

### 編譯選項說明
- `-g`: 產生除錯符號
- `-O0`: 關閉最佳化,方便除錯
- `-Wall`: 顯示所有警告
- `-D_GNU_SOURCE`: 啟用 GNU 擴充功能

### 需要編譯的檔案
```
主程式: src/tools/cmdzip.c 或 src/tools/cmdunzip.c
核心庫: src/zip.c, src/miniz.c
平台相依: src/unixutils.c (Linux) 或 src/winutils.c (Windows)
```

### 關鍵函數追蹤點
1. `main()` - 程式進入點
2. `zip_zip()` - 壓縮函數 (src/zip.c:319)
3. `zip_unzip()` - 解壓縮函數 (src/zip.c:128)
4. `mz_zip_writer_add_cfile()` - miniz 寫入函數
5. `mz_zip_reader_extract_to_cfile()` - miniz 讀取函數

## 注意事項
1. 所有測試與除錯產物必須放在 `tests/` 目錄
2. 不修改原始專案的 `src/` 目錄
3. 編譯腳本需要考慮 Linux/Unix 環境
4. 確保 GDB 可以找到原始碼檔案路徑

## 當前狀態
- [x] 專案結構分析完成
- [x] 建立 build 目錄與 Makefile
- [x] GDB 除錯測試成功
- [x] 文件撰寫完成

## 使用方式

```bash
cd build

# 編譯並執行 GDB 追蹤
make test

# 或分步執行
make           # 編譯
make debug     # 執行 GDB 追蹤
make gdb       # 互動式 GDB
make clean     # 清理
```
