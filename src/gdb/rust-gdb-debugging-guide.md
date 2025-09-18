# Rust GDB 調試機制與程式碼行號對應原理

## 概述
本文檔說明 `rust-gdb -x rust_debug_solution.gdb ./intiface_central` 命令如何建立調試器與源代碼行號之間的映射關係。

## 一、核心組件

### 1.1 調試符號 (Debug Symbols)
當編譯 Rust 程式時加入 `-g` 參數，編譯器會在二進制檔案中嵌入 DWARF 調試信息：

```bash
# 檢查二進制檔案的調試信息
$ file intiface_central
intiface_central: ELF 64-bit LSB pie executable, x86-64, version 1 (SYSV),
                  with debug_info, not stripped
```

### 1.2 DWARF 調試段
二進制檔案包含以下關鍵調試段：

| 段名稱 | 功能說明 |
|--------|----------|
| `.debug_info` | 儲存變量、函數、類型等元數據 |
| `.debug_line` | **行號映射表** - 機器碼地址到源碼行的映射 |
| `.debug_str` | 調試字串（檔案路徑、函數名等） |
| `.debug_abbrev` | 調試信息縮寫表 |
| `.debug_addr` | 地址表 |
| `.symtab` | 符號表 |

## 二、行號映射機制

### 2.1 映射流程圖

```
┌─────────────────┐
│ 執行中的程式碼   │
│ (機器碼地址)     │
│ 0x7fff12345678  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  DWARF 調試信息  │
│  (.debug_line)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  源碼位置        │
│ server.rs:100   │
└─────────────────┘
```

### 2.2 GDB 查詢過程

1. **獲取當前執行位置**
   - GDB 讀取指令指標暫存器 (RIP/PC)
   - 取得當前執行的機器碼地址

2. **查詢調試信息**
   - 在 `.debug_line` 段中查找地址對應的源碼位置
   - 解析 DWARF 格式的行號表

3. **返回映射結果**
   - 源檔案完整路徑
   - 行號
   - 函數名（從 `.debug_info` 獲取）

## 三、GDB 腳本實現細節

### 3.1 Python 腳本獲取行號
```python
# rust_debug_solution.gdb 第 32-60 行
frame = gdb.selected_frame()    # 取得當前堆疊幀
sal = frame.find_sal()          # SAL = Source And Line

if sal.symtab:
    filename = sal.symtab.filename  # 源檔案路徑
    line = sal.line                 # 行號
else:
    filename = "unknown"
    line = "?"
```

### 3.2 斷點設置方式

#### 方式 1：函數名斷點
```gdb
break buttplug::server::server::ButtplugServer::new
```
- GDB 在符號表中查找函數入口地址
- 自動解析 Rust 的 mangled 名稱

#### 方式 2：檔案行號斷點
```gdb
break /home/shihyu/gdb-intiface-central-buttplug/buttplug/buttplug/src/server/server.rs:100
```
- 直接指定源檔案路徑和行號
- GDB 通過 `.debug_line` 找到對應的機器碼地址

#### 方式 3：正則表達式斷點
```gdb
rbreak buttplug::server::.*::new
```
- 匹配所有符合模式的函數
- 批量設置斷點

## 四、執行時顯示機制

### 4.1 自定義顯示函數
腳本定義了 `show_full_location` 函數來格式化顯示位置信息：

```
┌────────────────────────────────────────────────────────────────────
│ 📍 /path/to/server.rs:100
│ 🔧 in function: ButtplugServer::new
│ 📦 arguments: self=0x7fff1234, config=0x7fff5678
│ 📄 Source:
│    98:     impl ButtplugServer {
│    99:         pub fn new(config: ServerConfig) -> Self {
│ → 100:             let server = Self {
│   101:                 config,
│   102:                 clients: Vec::new(),
└────────────────────────────────────────────────────────────────────
```

### 4.2 源碼顯示
通過 `list` 命令（第 78 行）顯示當前位置的源碼：
- GDB 使用調試信息中的檔案路徑
- 讀取並顯示源檔案內容
- 標記當前執行行

## 五、動態庫處理

### 5.1 延遲載入處理
```gdb
# 第 87-88 行
catch load libintiface_engine_flutter_bridge.so
commands 1
    # 庫載入後才設置斷點
    break buttplug::server::server::ButtplugServer::new
    ...
end
```

動態庫的符號在運行時載入，因此需要：
1. 使用 `catch load` 等待庫載入
2. 載入後再設置斷點
3. 使用 `set solib-search-path ./lib` 指定庫搜尋路徑

## 六、Rust 特定處理

### 6.1 符號解析
```gdb
set print asm-demangle on    # 解析組合語言符號
set print demangle on        # 解析 mangled 名稱
set language rust            # 設置語言為 Rust
```

### 6.2 名稱簡化
Python 腳本簡化 Rust 函數名顯示：
```python
if "::" in func_name:
    parts = func_name.split("::")
    if len(parts) > 2:
        func_name = "::".join(parts[-2:])  # 只顯示最後兩個部分
```

將 `buttplug::server::server::ButtplugServer::new` 簡化為 `ButtplugServer::new`

## 七、實際工作流程

1. **啟動調試器**
   ```bash
   rust-gdb -x rust_debug_solution.gdb ./intiface_central
   ```

2. **載入腳本**
   - GDB 執行 `rust_debug_solution.gdb` 中的命令
   - 設置環境變量和配置

3. **程式啟動**
   - `start` 命令開始執行程式
   - 停在 main 函數入口

4. **動態設置斷點**
   - 等待動態庫載入
   - 根據符號表設置斷點
   - 配置斷點命令

5. **執行與追蹤**
   - 程式執行到斷點時暫停
   - 顯示完整位置信息
   - 記錄到日誌檔案

6. **行號對應**
   - 每次停止時通過 DWARF 信息查詢
   - 即時顯示源碼位置
   - 提供上下文信息

## 八、疑難排解

### 8.1 無法顯示行號
- 確認編譯時包含 `-g` 參數
- 檢查二進制檔案：`file <binary>`
- 驗證調試段：`readelf -S <binary> | grep debug`

### 8.2 源碼路徑不正確
- 使用絕對路徑設置斷點
- 設置源碼搜尋路徑：`set substitute-path <from> <to>`

### 8.3 動態庫符號缺失
- 確保 `.so` 檔案包含調試信息
- 正確設置 `solib-search-path`
- 使用 `info sharedlibrary` 檢查載入狀態

## 總結

rust-gdb 通過 DWARF 調試信息建立機器碼地址與源碼行號的映射關係。這個機制依賴於：
1. 編譯時保留的調試符號
2. GDB 的 DWARF 解析器
3. 運行時的動態查詢
4. Python 腳本的增強顯示

整個系統協同工作，實現了從二進制執行到源碼級調試的完整追蹤。