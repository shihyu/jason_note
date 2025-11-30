# 編譯器與直譯器

本目錄收集了與編譯器、直譯器、虛擬機以及系統軟體開發相關的學習資源和專案。

## 目錄結構

### data/
包含多個編譯器、直譯器和作業系統相關的專案和學習材料：

#### ChCore
一個教學用的作業系統內核專案，用於深入理解作業系統設計原理和系統軟體開發。

**相關主題：**
- 內核架構設計
- 進程與執行緒管理
- 記憶體管理與虛擬記憶體
- 中斷與異常處理
- 檔案系統實現
- 系統呼叫介面

#### ChCore_new
ChCore 的新版本或改進版本，可能包含最新的功能、效能最佳化和現代系統設計。

#### rCore-Tutorial-Book-v3
Rust 語言編寫的教學用作業系統專案（第三版），重點關注系統編程和編譯器最佳化。

**相關主題：**
- 用 Rust 編寫作業系統
- RISC-V 架構支援與最佳化
- 系統編程最佳實踐
- 記憶體安全與所有權管理
- 裸機編程（Bare Metal）
- 編譯器代碼生成最佳化
- 連結器與加載器整合

**學習價值：**
- 理解編譯器如何與作業系統互動
- Rust 在系統編程中的優勢
- 低級硬體互動和最佳化
- 現代 OS 設計思想

#### test_sel4
seL4 微內核作業系統的測試專案，強調形式化驗證和可靠性。

**相關主題：**
- 微內核架構 (Microkernel)
- 能力安全 (Capability-based Security)
- 形式化驗證與編譯器證明
- 即時作業系統（RTOS）特性
- IPC 通訊機制
- 編譯器安全最佳化

**特點：**
- 高可靠性和可驗證性（形式化方法）
- 最小化 TCB（信任計算基）
- 用於嵌入式和即時系統

### Crafting Interpreters（中文翻譯）
一本免費且優秀的編譯器和直譯器入門書籍，提供詳細的實踐指導。

**主要內容：**
- 詞彙分析與語法分析的完整實現
- AST 建構和遞迴下降解析
- 變數作用域和環境管理
- 函數定義與調用機制
- 控制流和迴圈實現
- 物件導向語言特性

**學習價值：**
- 從零開始實現 Lox 語言編譯器
- 理解直譯器工作原理
- 代碼實例清晰易懂
- 適合初學者入門

**資源連結：**
- [Crafting Interpreters 繁體中文版](https://shihyu.github.io/crafting_interpreters_zh_tw/)
- [官方英文版](https://craftinginterpreters.com/)

### SICP 計算機程式的構造和解釋（Python 版本）
經典的計算機科學教材，以 Python 重新編寫，強調程式設計基礎概念。

**主要內容：**
- 程式語言的設計與實現
- 過程抽象 (Procedural Abstraction)
- 資料抽象 (Data Abstraction)
- 元程式設計 (Metaprogramming)
- 編譯器設計基礎
- 虛擬機和求值器實現

**學習價值：**
- 深入理解編程語言的本質
- 從直譯器和編譯器角度思考問題
- 強調抽象層次和模組化設計
- 培養系統思維能力

**資源連結：**
- [SICP Python 繁體中文版](https://shihyu.github.io/sicp-py-zh-tw/)
- [官方英文版](https://composingprograms.com/)

## 編譯器與直譯器核心概念

### 編譯器的角色
編譯器是連接高級語言和作業系統之間的橋樑：

**編譯過程三大階段：**
1. **前端 (Frontend)**
   - 詞彙分析 (Lexical Analysis)：源碼 → Token 流
   - 語法分析 (Syntax Analysis)：Token 流 → AST（抽象語法樹）
   - 語意分析 (Semantic Analysis)：型別檢查、符號表管理

2. **中端 (Middle-end)**
   - 中間表示 (IR) 轉換
   - 代碼最佳化：循環最佳化、死代碼消除、內聯展開
   - 控制流分析、資料流分析

3. **後端 (Backend)**
   - 代碼生成：IR → 匯編代碼
   - 暫存器分配
   - 指令調度
   - 機器碼生成

### 直譯器與虛擬機
- **直譯器 (Interpreter)**：逐行執行位元組碼或 AST，無編譯過程
- **JIT 編譯 (Just-In-Time)**：運行時動態編譯熱點代碼，結合編譯器和直譯器的優點
- **虛擬機 (Virtual Machine)**：提供執行環境和資源管理（如 JVM、Python VM）
- **位元組碼 (Bytecode)**：編譯器和直譯器的中間格式

### 系統軟體開發關鍵環節
```
源碼 → 詞彙分析 → 語法分析 → 語意分析 → 中間代碼 → 代碼最佳化 → 代碼生成 → 匯編 → 連結 → 可執行檔
```

## 編譯器種類

### 按輸出分類
| 類型 | 描述 | 應用場景 |
|------|------|--------|
| **原生編譯器** | 編譯為機器碼 | C++、Rust、Go |
| **直譯器** | 直接執行源碼或位元組碼 | Python、JavaScript、Ruby |
| **JIT 編譯器** | 運行時編譯 | Java、JavaScript (V8)、C# |
| **交叉編譯器** | 在一個平臺生成另一平臺代碼 | 嵌入式開發、ARM 編譯 |

### 按技術分類
- **靜態編譯**：編譯時進行所有分析與最佳化
- **動態編譯**：運行時進行編譯和最佳化
- **增量編譯**：只重新編譯改變的部分
- **形式化驗證**：證明代碼正確性（如 seL4）

## 關鍵學習路徑

### 1. 編譯器基礎（從易到難）
**初級：**
- 詞彙分析和語法分析（正規表示式、有限狀態自動機）
- 構建簡單計算器或玩具語言編譯器
- 理解 AST 和遞迴下降解析

**中級：**
- 語意分析與型別檢查
- 中間代碼生成
- 基本代碼最佳化（常數折疊、死代碼消除）

**進階：**
- 進階最佳化（迴圈轉換、向量化）
- 暫存器分配演算法
- 機器碼生成與指令調度
- 形式化驗證

### 2. 不同架構與設計

| 架構 | 特色 | 編譯器角色 |
|------|------|---------|
| **宏內核** (ChCore) | 模組化，功能齊全 | 編譯器可針對性最佳化 |
| **微內核** (seL4) | 最小化特權代碼 | 形式化驗證對編譯器安全性的要求 |
| **Rust OS** (rCore) | 記憶體安全設計 | 利用編譯器保證安全性 |

### 3. 語言與工具鏈

**系統編程語言：**
- **C/C++**：傳統系統編程（ChCore 可能使用）
- **Rust**：記憶體安全性，編譯時檢查（rCore）
- **Zig**：低階控制，安全性

**編譯器基礎設施：**
- **LLVM**：模組化編譯器框架
- **GCC**：傳統編譯器
- **Cranelift**：Rust 寫的快速編譯器
- **TVM**：機器學習編譯器

**低級語言：**
- **RISC-V 匯編**：開放指令集架構
- **x86-64 匯編**：主流處理器架構

### 4. 虛擬機與直譯器
- **Python 直譯器**：教學用途
- **Java 虛擬機**：工業級 JIT 編譯
- **WebAssembly VM**：跨平臺執行

## 實踐建議

### 從零開始的學習順序

**第一階段：編譯器基礎（4-6 週）**
1. 學習編譯原理基礎（自動機、形式語言）
2. 實現簡單計算器編譯器
3. 實現玩具語言（如 Lox 或 Lua 子集）

**第二階段：系統軟體（8-12 週）**
1. 研究 rCore
   - 理解 Rust 編譯器如何處理低級代碼
   - 學習系統編程最佳實踐
   - 見識現代編譯器技術的應用

2. 研究 ChCore
   - 理解傳統內核架構
   - C 編譯器最佳化的重要性
   - 系統軟體的設計模式

**第三階段：進階主題（12+ 週）**
1. 深入 seL4
   - 形式化驗證方法
   - 編譯器安全證明
   - 高可靠性系統設計

2. LLVM/GCC 研究
   - 中間表示優化
   - 後端代碼生成
   - 指令選擇與調度

### 編譯器開發路線圖
```
編譯原理基礎
    ↓
簡單直譯器（Python/JavaScript 子集）
    ↓
位元組碼編譯器（編譯到位元組碼）
    ↓
原生代碼編譯器（編譯到機器碼）
    ↓
最佳化編譯器（加入各種最佳化）
    ↓
JIT 編譯器（運行時編譯）
```

## 編譯器 vs 直譯器

### 編譯器優點
✅ 執行速度快（預先編譯為機器碼）
✅ 代碼最佳化充分
✅ 錯誤提前發現
✅ 二進制分發（保護源碼）

### 編譯器缺點
❌ 編譯時間長
❌ 缺乏靈活性
❌ 跨平臺需重新編譯

### 直譯器優點
✅ 快速開發迭代
✅ 動態特性豐富
✅ 跨平臺自動支援
✅ 動態除錯和自省

### 直譯器缺點
❌ 執行速度慢
❌ 記憶體開銷大
❌ 無法提前最佳化

## 相關資源連結

### 官方專案
- [ChCore Project](https://github.com/OS-F23/ChCore)
- [rCore-Tutorial-Book](https://github.com/rcore-os/rCore-Tutorial-Book-v3)
- [seL4 Official](https://sel4.systems/)

### 編譯器學習資源

#### 入門階段
- **[Crafting Interpreters 繁體中文版](https://shihyu.github.io/crafting_interpreters_zh_tw/)** - 免費線上書，詳細講解詞彙分析、語法分析、AST 和直譯器實現
  - 包含 Lox 語言的完整實現（Java 版和 C 版）
  - 適合初學者，代碼實例豐富

- **[SICP Python 繁體中文版](https://shihyu.github.io/sicp-py-zh-tw/)** - 經典計算機科學教材，強調抽象和系統思維
  - 涵蓋編譯器和直譯器的理論基礎
  - 適合深入理解語言設計原理

#### 進階學習
- [Engineering a Compiler](https://www.elsevier.com/books/engineering-a-compiler/cooper/978-0-12-815412-0)
- [LLVM 官方文件](https://llvm.org/docs/)
- [Compiler Explorer](https://godbolt.org/) - 線上編譯器探索工具

### 編譯器專案
- [LLVM](https://llvm.org/) - 模組化編譯器框架
- [GCC](https://gcc.gnu.org/) - GNU 編譯器集合
- [Rust 編譯器 (rustc)](https://github.com/rust-lang/rust)
- [Cranelift](https://github.com/bytecodealliance/cranelift) - Rust 寫的快速編譯器

## 更多學習內容

### 系統軟體相關
- [Linux 內核調試](../kernel/linux_kernel.md)
- [eBPF 完整指南](../linux_system/ebpf-complete-guide.md)
- [Linux 系統深度解析](../linux_system/linux_system.md)
- [Linker and Loader Guide](../kernel/linker-loader-guide.md)

### 編譯器相關
- [LLVM 編譯器架構與語言效能深度解析](../tools/llvm_guide.md)
- [Cross Compiler 與 LLVM vs GCC 完整解析](../tools/cross-compiler-llvm-gcc-guide.md)

### 語言系統編程
- [Rust 系統編程](../rust/rust.md)
- [Rust 標準函式庫範例](../rust/rust-stdlib-examples.md)
- [Rust Unsafe 底層分析與最佳化技術](../rust/rust-unsafe-analysis.md)
- [C++ 高級特性](../c++/cpp.md)
- [Go 編程實戰派](../go/go.md)

### 效能優化
- [Rust 程式追蹤與分析完整指南](../rust/rust_trace_guide.md)
- [Linux 效能檢測工具完整指南](../linux_system/linux-performance-tools.md)
- [Flamegraph 效能分析指南](../tools/flamegraph-guide.md)
- [Google Benchmark 指南](../c++/google_benchmark_guide.md)

### 虛擬機與執行時
- [WebAssembly 相容性與載入器完整指南](../web/wasm_compatibility_guide.md)
- [WebAssembly (WASM) 完整開發指南](../web/webassembly_complete_guide.md)
- [Python 異步程式效能基準測試完整指南](../python/complete-async-benchmark.md)

# 線上編譯器 / IDE / 編譯器分析工具整理

本表整理常用的線上程式編譯、執行與反組譯工具，依用途分成兩大類：

1. **多語言線上編譯器 / IDE**
2. **編譯器產物分析（組語 / 反組譯）**

---

## 一、支援多種程式語言的線上編譯器 / IDE

這類平台主要用來 **編譯、執行程式碼**，快速測試語法或分享程式碼片段。

| 網站名稱        | 主要特色                            | 支援語言數量           |
| ----------- | ------------------------------- | ---------------- |
| [JDoodle](https://www.jdoodle.com/) | 簡潔、易用，支援執行及 API 呼叫              | 超過 **88** 種語言    |
| [Ideone](https://www.ideone.com/)  | 老牌線上編譯器，適合快速測試程式碼片段             | 超過 **60** 種語言    |
| [Replit](https://replit.com/)  | 完整線上 IDE，支援專案結構、協作、部署           | 超過 **60** 種語言與框架 |
| [Wandbox](https://wandbox.org/) | 專注在 C++ 多版本、多編譯器測試（GCC / Clang） | 多種語言（主打 C/C++）   |

### 💡補充推薦

| 網站名稱          | 特色補充                                                |
| ------------- | --------------------------------------------------- |
| [OnlineGDB](https://www.onlinegdb.com/) | 支援 **除錯器 (Debugger)**，可逐步執行、觀察變數（C/C++/Java/Python） |
| [Paiza.IO](https://paiza.io/)  | 免登入快速執行程式，速度快                                       |
| [Glot.io](https://glot.io/)   | 支援 API，可用來當作「線上沙盒」執行程式碼                             |

---

## 二、編譯器輸出分析（組合語言 / 反組譯器）

這類網站著重於 **研究編譯器產生的機器碼**，適合系統工程師、逆向工程、優化分析。

| 網站名稱                                  | 主要特色                                           | 支援語言 / 目標                             |
| ------------------------------------- | ---------------------------------------------- | ------------------------------------- |
| [Compiler Explorer (Godbolt)](https://godbolt.org/) | 即時顯示不同編譯器輸出的組合語言；常用於 C++ 優化分析                  | C/C++, Rust, Go, Zig, D, C#, Python 等 |
| [Decompiler Explorer (Dogbolt.org)](https://dogbolt.org/) | 同一個二進位檔可用多種反組譯器分析輸出（Ghidra / IDA / Hex-Rays 等） | ELF, PE, Mach-O 等多種格式                 |
| [Online Java Decompiler](https://www.decompiler.com/)            | 專門將 `.class` / `.jar` 反組譯回 Java 原始碼            | Java bytecode                         |

### 💡補充推薦（逆向工具）

| 工具名稱                           | 特色                                          |
| ------------------------------ | ------------------------------------------- |
| [Godbolt Rust MIR / LLVM IR](https://godbolt.org/) | Godbolt 除了組語，也能顯示 Rust MIR、LLVM IR，用於學習編譯流程 |
| [WebAssembly Explorer](https://mbebenita.github.io/WasmExplorer/)       | 將 C/C++ 轉成 WASM，查看編譯細節                      |
| [JSFuck](https://www.jsfuck.com/) / [Babel Repl](https://babeljs.io/repl)        | 適合看 JS 如何被轉換、壓縮、混淆                          |

---

## 三、用途總結

| 用途                       | 推薦工具                                  |
| ------------------------ | ------------------------------------- |
| **快速跑程式碼 / 多語言支援**       | Replit、JDoodle、Ideone、Paiza、OnlineGDB |
| **研究編譯器行為（組合語言）**        | Compiler Explorer (Godbolt)           |
| **研究二進位、反組譯、逆向工程**       | Decompiler Explorer、Ghidra（需本地）       |
| **測試 C/C++ 不同編譯器 / ABI** | Wandbox、Godbolt                       |