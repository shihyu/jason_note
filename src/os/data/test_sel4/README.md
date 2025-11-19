# seL4 QEMU + GDB 開發環境

一個簡化的 seL4 開發環境，使用 QEMU 模擬器運行 seL4 kernel，並支援 GDB 除錯。

## 快速開始

### 環境需求

- Linux 系統 (已測試: Ubuntu 20.04+)
- 基本工具：
  ```bash
  sudo apt install build-essential cmake ninja-build python3-dev python3-pip git curl
  sudo apt install qemu-system-x86 gdb
  ```
- Google repo 工具：
  ```bash
  mkdir -p ~/.local/bin
  curl https://storage.googleapis.com/git-repo-downloads/repo > ~/.local/bin/repo
  chmod a+x ~/.local/bin/repo
  export PATH=~/.local/bin:$PATH
  ```

### 首次使用

```bash
# 1. 初始化專案（下載 seL4 原始碼）
make init

# 2. 編譯
make build

# 3. 運行 seL4 測試
make qemu
```

## 主要功能

### 查看說明
```bash
make help
```

### 查看專案狀態
```bash
make status
```

### QEMU 運行
```bash
make qemu
```
按 `Ctrl+A` 然後按 `X` 退出 QEMU

### GDB 除錯

需要兩個終端：

**終端 1 - 啟動 QEMU + GDB server:**
```bash
make debug
```

**終端 2 - 連線 GDB:**
```bash
make gdb
```

**常用 GDB 命令：**
```gdb
(gdb) break main              # 設定中斷點
(gdb) continue                # 繼續執行 (簡寫: c)
(gdb) step                    # 單步執行，進入函式 (簡寫: s)
(gdb) next                    # 單步執行，不進入函式 (簡寫: n)
(gdb) info registers          # 顯示暫存器
(gdb) backtrace               # 顯示呼叫堆疊 (簡寫: bt)
(gdb) print variable          # 印出變數值 (簡寫: p)
(gdb) list                    # 顯示原始碼 (簡寫: l)
(gdb) quit                    # 退出 GDB (簡寫: q)
```

**推薦的中斷點位置：**

*用戶空間除錯：*
```gdb
(gdb) break main              # 主程式入口 (main.c:596, 位址 0x405074)
(gdb) break _start            # 程式啟動點 (0x401039)
```

*Kernel 空間除錯（進階）：*
```gdb
(gdb) break init_freemem      # 記憶體初始化
(gdb) break init_core_state   # 核心狀態初始化
(gdb) break handle_syscall    # 系統呼叫處理
(gdb) break c_handle_syscall  # C 層系統呼叫處理
```

**查找可用函式：**
```gdb
(gdb) info functions <關鍵字>    # 搜尋包含關鍵字的函式
(gdb) info functions test         # 範例：搜尋測試相關函式
(gdb) info functions init         # 範例：搜尋初始化函式
```

### 清理

```bash
# 清理構建產物
make clean

# 完全清理（包含下載的原始碼）
make distclean
```

## 目錄結構

```
test_sel4/
├── Makefile              # 主要構建腳本
├── README.md             # 本檔案
├── plan.md               # 專案計畫與實施記錄
├── tests/                # 測試與構建產物（可刪除）
│   ├── build/           # seL4 專案根目錄
│   │   ├── kernel/      # seL4 kernel 原始碼
│   │   ├── projects/    # sel4test 專案
│   │   ├── tools/       # 構建工具
│   │   └── build-x86_64/  # 構建產物
│   │       ├── images/     # 可執行映像檔
│   │       ├── simulate*   # QEMU 啟動腳本
│   │       └── launch_gdb* # GDB 連線腳本
│   └── logs/            # 構建與測試日誌
├── seL4/                # 原始 kernel repo (僅供參考)
└── sel4test/            # 原始 sel4test repo (僅供參考)
```

## 技術細節

- **平臺**: x86_64
- **構建系統**: CMake + Ninja
- **QEMU 版本**: 8.2.2+
- **GDB 連線**: localhost:1234
- **映像檔位置**: `tests/build/build-x86_64/images/sel4test-driver-image-x86_64-pc99`

## Makefile 目標說明

| 目標 | 說明 |
|------|------|
| `make help` | 顯示使用說明 |
| `make status` | 顯示專案當前狀態 |
| `make init` | 初始化專案（下載 seL4 原始碼）|
| `make config` | CMake 配置 |
| `make build` | 編譯 seL4 kernel 與測試 |
| `make qemu` | 啟動 QEMU 運行 seL4 |
| `make debug` | 啟動 QEMU + GDB server |
| `make gdb` | 連線到 QEMU 的 GDB server |
| `make clean` | 清理構建產物 |
| `make distclean` | 完全清理 |

## 常見問題

### Q: 如何在 kernel 中設定中斷點？

A: 在 GDB 中，你可以對 kernel 函式設定中斷點：
```gdb
(gdb) break handleSyscall
(gdb) continue
```

### Q: 如何查看 seL4 特定資料結構？

A: seL4 提供了 GDB macros，已自動載入（位於 `tests/build/kernel/gdb-macros`）。可以使用：
```gdb
(gdb) info functions seL4_
```

### Q: GDB 無法連接？

A: 確認以下事項：
1. QEMU Debug 模式是否在運行：
   ```bash
   ps aux | grep qemu
   ```
2. 如果沒有，重新啟動：
   ```bash
   make debug
   ```
3. 確認符號表已載入（應該看到 `Reading symbols from images/sel4test-driver-image-x86_64-pc99...`）

### Q: 中斷點沒有中斷執行？

A: 需要在 QEMU 啟動時處於暫停狀態：
1. 先啟動 `make debug`（QEMU 會自動暫停等待 GDB）
2. 再啟動 `make gdb`
3. 設定中斷點後執行 `continue`

### Q: QEMU 視窗在哪裡？

A: 使用 `-nographic` 模式，所有輸出都在終端中。

### Q: 如何修改構建選項？

A: 編輯 Makefile 中的變數：
- `PLATFORM` - 目標平臺
- `SIMULATION` - 模擬模式
- `BUILD_TYPE` - 構建類型 (Debug/Release)

## 參考資源

### 專案文件
- [plan.md](plan.md) - 詳細的專案計畫與實施記錄
- [tests/logs/gdb-test-report.md](tests/logs/gdb-test-report.md) - GDB 測試報告 (2025-10-04)

### seL4 官方資源
- [seL4 官方網站](https://sel4.systems/)
- [seL4 文件](https://docs.sel4.systems/)
- [seL4 GitHub](https://github.com/seL4/seL4)
- [sel4test 文件](https://docs.sel4.systems/projects/sel4test/)

## 授權

本專案遵循 seL4 原始碼的授權條款。

---

**最後更新**: 2025-10-04  
**測試環境**: Linux 6.14.0-32-generic, Ubuntu  
**GDB 測試狀態**: ✅ 通過所有測試
