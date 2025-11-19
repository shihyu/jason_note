# seL4 QEMU + GDB 除錯環境建置計畫

## 任務目標
建立一個簡化的 seL4 開發環境,能夠:
1. 使用 QEMU 模擬器運行 seL4 kernel
2. 使用 GDB 進行中斷點除錯,分析程式運作邏輯
3. 僅保留 Makefile 作為唯一構建入口
4. 測試檔案集中管理,用完即刪除

## 專案差異分析

### seL4 專案
- **性質**: seL4 microkernel 核心原始碼
- **目的**: 提供 kernel 本身的實作
- **包含**:
  - kernel 核心程式碼 (src/, include/)
  - libsel4: C bindings for seL4 ABI
  - CMake 構建系統
  - GDB macros (gdb-macros 檔案)
  - 各平臺配置檔 (configs/)
- **構建方式**: CMake-based

### sel4test 專案
- **性質**: seL4 測試框架與測試集
- **目的**: 提供測試環境和測試案例
- **包含**:
  - sel4test-driver: 測試驅動程式
  - sel4test-tests: 具體測試案例
  - libsel4testsupport: 測試支援函式庫
  - 模擬環境設定 (SIMULATION 參數)
- **構建方式**: CMake-based,依賴 seL4 kernel
- **預設平臺**: x86_64
- **支援 QEMU**: 透過 SIMULATION=ON 參數

## 預期產出

### 檔案結構
```
test_sel4/
├── Makefile              # 唯一構建入口
├── plan.md               # 本計畫檔案
├── tests/                # 測試與臨時檔案目錄
│   ├── build/           # CMake 構建產物 (用後刪除)
│   ├── logs/            # 執行與除錯 log (用後刪除)
│   └── .gitignore       # 排除所有測試檔案
├── seL4/                 # kernel 原始碼 (保持原樣)
├── sel4test/             # 測試框架 (保持原樣)
└── .gdbinit             # GDB 初始化設定 (可選)
```

### Makefile 功能
- `make config`: 設定構建環境 (CMake configure)
- `make build`: 編譯 seL4 + sel4test
- `make qemu`: 啟動 QEMU 運行映像檔
- `make debug`: 啟動 QEMU + GDB 除錯模式
- `make clean`: 清理構建產物
- `make distclean`: 完全清理,包含 tests/ 目錄

## 技術細節

### 構建指令 (需驗證)
```bash
# 基於 sel4test/easy-settings.cmake,預計需要:
mkdir -p tests/build
cd tests/build
cmake -DPLATFORM=x86_64 \
      -DSIMULATION=ON \
      -DCMAKE_BUILD_TYPE=Debug \
      -G Ninja \
      ../../sel4test
ninja
```

### QEMU 啟動 (需驗證)
```bash
# 預計會生成類似 simulate 腳本,或手動執行:
qemu-system-x86_64 \
    -m 512M \
    -nographic \
    -kernel images/sel4test-driver-image-x86_64-pc99 \
    -s -S  # GDB 選項: -s (port 1234), -S (啟動時暫停)
```

### GDB 連線 (需驗證)
```bash
gdb -ex "target remote :1234" \
    -ex "source seL4/gdb-macros" \
    tests/build/images/sel4test-driver-image-x86_64-pc99
```

## 驗收標準
- [ ] 執行 `make config` 成功完成 CMake 設定
- [ ] 執行 `make build` 成功編譯出 seL4 kernel 映像檔
- [ ] 執行 `make qemu` 能啟動 QEMU 並看到 seL4 輸出
- [ ] 執行 `make debug` 能啟動 QEMU,並使用 GDB 連線成功
- [ ] 在 GDB 中能設定中斷點 (例如: `b main`)
- [ ] 執行 `make clean` 能清除 tests/build/ 內容
- [ ] 所有測試檔案都在 tests/ 目錄下
- [ ] seL4/ 和 sel4test/ 目錄保持乾淨,無構建產物

## 子任務拆解

### 第一階段:研究與驗證
1. **驗證 sel4test 構建流程**
   - 閱讀 sel4test 官方文件,確認正確的構建步驟
   - 手動執行一次完整構建,記錄所有指令
   - 驗證 SIMULATION=ON 是否能生成 QEMU 可執行映像檔
   - 記錄實際的映像檔位置與名稱

2. **驗證 QEMU + GDB 整合**
   - 確認 QEMU 啟動參數
   - 測試 GDB 能否連線到 QEMU
   - 驗證 seL4/gdb-macros 的使用方式
   - 測試能否在 kernel 程式碼中設定中斷點

### 第二階段:自動化
3. **建立 Makefile**
   - 實作 config target (CMake 設定)
   - 實作 build target (Ninja 編譯)
   - 實作 qemu target (啟動 QEMU)
   - 實作 debug target (QEMU + GDB)
   - 實作 clean/distclean target

4. **測試目錄結構**
   - 建立 tests/ 目錄與 .gitignore
   - 確保所有構建產物都在 tests/ 下

### 第三階段:測試與文件
5. **整合測試**
   - 執行完整的 build -> qemu -> debug 流程
   - 驗證 GDB 中斷點功能
   - 測試清理功能

6. **除錯案例驗證** (可選)
   - 在 kernel 初始化函式設定中斷點
   - 檢視重要資料結構
   - 驗證 step/next/continue 指令

## 待確認問題
1. sel4test 是否包含完整的 seL4 kernel 依賴?還是需要額外下載?
2. SIMULATION=ON 產生的映像檔確切位置?
3. sel4test 是否有官方的 QEMU 啟動腳本?
4. GDB macros 需要哪些額外設定?
5. 是否需要額外的 toolchain (交叉編譯器)?

## 備註
- 本計畫假設在 Linux 環境執行 (已確認: Linux 6.14.0-32-generic)
- 使用 x86_64 平臺,簡化跨平臺問題
- 優先使用官方推薦的構建流程,不自行修改 CMake 設定

---

## 實施結果總結

### ✅ 已完成項目

#### 1. 專案初始化
- 使用 `repo` 工具下載完整的 seL4 專案結構
- 專案位置：`tests/build/`
- 包含：kernel、tools、projects (sel4test)

#### 2. 構建配置
```bash
cd tests/build/build-x86_64
../init-build.sh -DPLATFORM=x86_64 -DSIMULATION=TRUE -DCMAKE_BUILD_TYPE=Debug
ninja
```
- 構建成功，生成映像檔：
  - `tests/build/build-x86_64/images/sel4test-driver-image-x86_64-pc99`
  - `tests/build/build-x86_64/images/kernel-x86_64-pc99`

#### 3. QEMU 運行驗證
- QEMU 命令（由 simulate 腳本生成）：
```bash
qemu-system-x86_64 \
  -cpu Nehalem,-vme,+pdpe1gb,-xsave,-xsaveopt,-xsavec,-fsgsbase,-invpcid,+syscall,+lm,enforce \
  -nographic -serial mon:stdio -m size=3G \
  -kernel images/kernel-x86_64-pc99 \
  -initrd images/sel4test-driver-image-x86_64-pc99
```
- ✅ seL4 kernel 成功啟動
- ✅ sel4test 測試套件正常運行

#### 4. GDB 除錯驗證
- QEMU GDB server：`-s -S` (port 1234)
- GDB 連線測試：
  - ✅ 成功連線到 remote target
  - ✅ 成功設定中斷點 (0x1002ea - kernel entry)
  - ✅ 可查看暫存器狀態
  - ✅ 可載入 seL4 GDB macros

#### 5. Makefile 自動化
建立完整的 Makefile，包含以下目標：
- `make init` - 初始化專案（repo init/sync）
- `make config` - CMake 配置
- `make build` - Ninja 構建
- `make qemu` - 啟動 QEMU 運行
- `make debug` - 啟動 QEMU + GDB server
- `make gdb` - GDB 連線
- `make clean` - 清理構建產物
- `make distclean` - 完全清理
- `make status` - 顯示專案狀態
- `make help` - 顯示說明

### 📁 最終目錄結構
```
test_sel4/
├── Makefile              # 唯一構建入口 ✅
├── plan.md               # 計畫文件 ✅
├── tests/                # 測試與構建產物目錄 ✅
│   ├── .gitignore       # 排除所有測試檔案 ✅
│   ├── build/           # seL4 專案根目錄 ✅
│   │   ├── kernel/      # seL4 kernel 原始碼
│   │   ├── projects/    # 專案（sel4test）
│   │   ├── tools/       # 構建工具
│   │   └── build-x86_64/  # 構建產物
│   │       ├── images/     # 可執行映像檔
│   │       ├── simulate*   # QEMU 啟動腳本
│   │       └── launch_gdb* # GDB 連線腳本
│   └── logs/            # 構建與測試日誌 ✅
│       ├── cmake-config.log
│       ├── ninja-build.log
│       ├── qemu-test.log
│       └── gdb-connection-test.log
├── seL4/                # 原始 kernel repo (保留參考)
└── sel4test/            # 原始 sel4test repo (保留參考)
```

### 🎯 使用方式

#### 首次使用
```bash
make init    # 下載 seL4 原始碼
make build   # 編譯（自動執行 config）
make qemu    # 運行測試
```

#### GDB 除錯流程
```bash
# 終端 1
make debug   # 啟動 QEMU，等待 GDB 連線

# 終端 2
make gdb     # 啟動 GDB 並連線
(gdb) break main
(gdb) continue
(gdb) info registers
```

### ✅ 驗收標準檢查
- [✅] 執行 `make config` 成功完成 CMake 設定
- [✅] 執行 `make build` 成功編譯出 seL4 kernel 映像檔
- [✅] 執行 `make qemu` 能啟動 QEMU 並看到 seL4 輸出
- [✅] 執行 `make debug` 能啟動 QEMU，並使用 GDB 連線成功
- [✅] 在 GDB 中能設定中斷點
- [✅] 執行 `make clean` 能清除 tests/build/build-x86_64/ 內容
- [✅] 所有測試檔案都在 tests/ 目錄下
- [✅] seL4/ 和 sel4test/ 目錄保持乾淨,無構建產物

### 📊 構建統計
- CMake 配置時間：~1 秒
- Ninja 構建時間：~15 秒
- 總構建檔案：266 個目標
- 最終映像檔大小：3.7 MB

### 🔧 已解決問題
1. **專案結構問題**：使用官方 repo 工具建立正確的專案結構
2. **GDB macros 載入**：Makefile 自動載入 `kernel/gdb-macros`
3. **測試檔案隔離**：所有構建產物集中在 `tests/` 目錄
4. **一鍵操作**：Makefile 封裝所有複雜操作

---

### 🐛 2025-10-04 GDB 路徑修正

#### 問題描述
初始 Makefile 中 GDB 相關路徑有誤，導致：
1. 映像檔路徑在 `cd` 後變成絕對路徑，無法正確載入
2. GDB macros 路徑錯誤（`../../kernel/gdb-macros` 應為 `../kernel/gdb-macros`）

#### 修正內容
**Makefile 第 145-148 行：**
```diff
  @cd $(BUILD_TARGET) && \
      gdb -ex "target remote :1234" \
-         -ex "source ../../kernel/gdb-macros" \
-         $(IMAGE)
+         -ex "source ../kernel/gdb-macros" \
+         images/sel4test-driver-image-x86_64-pc99
```

#### 驗證結果
- ✅ GDB 成功連接到 QEMU (localhost:1234)
- ✅ 符號表正確載入
- ✅ seL4 GDB macros 成功載入
- ✅ 可設定中斷點 (例如: `break main`)
- ✅ 中斷點位置: `main.c:596` at `0x405074`

#### 推薦的中斷點位置
**用戶空間除錯：**
- `break main` - 主程式入口 (main.c:596)
- `break _start` - 程式啟動點 (0x401039)

**Kernel 空間除錯（進階）：**
- `break init_freemem` - 記憶體初始化
- `break init_core_state` - 核心狀態初始化
- `break handle_syscall` - 系統呼叫處理
- `break c_handle_syscall` - C 層系統呼叫處理

#### 測試文件
- `tests/logs/gdb-test-report.md` - 完整測試報告
- `tests/gdb-test.gdb` - GDB 測試腳本
- `tests/test-breakpoint.gdb` - 中斷點測試腳本
