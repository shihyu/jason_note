# 編譯器與直譯器

本目錄收集了編譯器、直譯器、虛擬機的學習資源、實作教學和專案範例。從零基礎到進階主題，提供完整的學習路徑與實作指引。

**適合對象：**
- 想了解程式語言如何運作的開發者
- 希望實作自己的程式語言或 DSL
- 對編譯器最佳化技術感興趣的工程師
- 準備相關面試或研究所考試的學生

## 目錄結構

### data/
包含編譯器與直譯器相關的學習材料和專案實作範例。

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

### 2. 語言與工具鏈

**常見實現語言：**
- **C/C++**：傳統編譯器實現（GCC、Clang）
- **Rust**：現代編譯器開發（rustc、Cranelift）
- **OCaml/Haskell**：函數式編譯器（Reason、GHC）
- **Java/Kotlin**：基於 JVM 的編譯器
- **Python**：原型設計與教學用途

**編譯器基礎設施：**
- **LLVM**：模組化編譯器框架
- **GCC**：傳統編譯器
- **Cranelift**：Rust 寫的快速編譯器
- **TVM**：機器學習編譯器

**目標平臺：**
- **RISC-V**：開放指令集架構
- **x86-64**：主流處理器架構
- **ARM**：行動與嵌入式系統
- **WebAssembly**：瀏覽器與跨平臺

### 3. 虛擬機與直譯器範例
- **CPython**：Python 官方直譯器（位元組碼）
- **JVM**：Java 虛擬機（JIT 編譯）
- **V8**：JavaScript 引擎（多層 JIT）
- **LuaJIT**：高效能 Lua JIT 編譯器
- **WebAssembly VM**：安全沙盒執行環境

## 實踐建議

### 從零開始的學習順序

**第一階段：編譯器基礎**
1. 學習理論基礎
   - 正規表達式與有限狀態機
   - 上下文無關文法（CFG）
   - 詞彙分析與語法分析算法

2. 實作練習
   - 簡單計算器（支援四則運算）
   - 表達式求值器（含變數）
   - Lox 語言編譯器（跟隨 Crafting Interpreters）

**第二階段：中階技術**
1. 語意分析與型別系統
   - 符號表管理
   - 型別檢查與推導
   - 作用域分析

2. 中間表示與最佳化
   - AST 與 IR 設計
   - 基礎最佳化（常數折疊、死代碼消除）
   - 控制流與資料流分析

**第三階段：進階主題**
1. 代碼生成
   - 目標機器指令選擇
   - 暫存器分配
   - 指令調度

2. 進階最佳化
   - SSA 形式
   - 迴圈最佳化
   - 內聯與逃逸分析

3. 現代技術
   - JIT 編譯
   - 垃圾回收
   - 並行編譯

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

## 編譯器與直譯器學習資源

### 📚 入門書籍與教材

**免費線上資源：**

- **[Crafting Interpreters 繁體中文版](https://shihyu.github.io/crafting_interpreters_zh_tw/)** ⭐ 強力推薦
  - 從零開始實現 Lox 語言
  - 包含樹走訪直譯器（Java）和位元組碼虛擬機（C）
  - 詞彙分析、語法分析、AST、環境管理、閉包實現
  - 適合完全初學者，代碼清晰易懂
  - [官方英文版](https://craftinginterpreters.com/)

- **[SICP Python 繁體中文版](https://shihyu.github.io/sicp-py-zh-tw/)**
  - 經典計算機科學教材的 Python 改寫版
  - 語言設計哲學與抽象思維
  - 求值器與編譯器基礎
  - 元語言抽象與程式即資料
  - [官方英文版](https://composingprograms.com/)

- **[Let's Build a Compiler (Jack Crenshaw)](https://compilers.iecc.com/crenshaw/)**
  - 經典的編譯器教學系列
  - 遞迴下降解析器
  - 直接生成彙編代碼
  - 實用導向

**經典教科書：**

- **Dragon Book** - [Compilers: Principles, Techniques, and Tools](https://suif.stanford.edu/dragonbook/)
  - 編譯器領域的聖經
  - 理論完整但較艱深
  - 適合作為參考書

- **Engineering a Compiler (Cooper & Torczon)**
  - 現代編譯器設計
  - 重視最佳化技術
  - 工程實踐導向

- **Modern Compiler Implementation (Appel)**
  - 提供 C/Java/ML 三種語言版本
  - Tiger 語言完整實現
  - 理論與實作兼顧

### 🎓 線上課程

- **[Stanford CS143: Compilers](https://web.stanford.edu/class/cs143/)**
  - 史丹佛大學編譯器課程
  - Cool 語言編譯器實作
  - 完整的課程影片與作業

- **[MIT 6.035: Computer Language Engineering](https://ocw.mit.edu/courses/6-035-computer-language-engineering-spring-2010/)**
  - MIT 開放課程
  - Decaf 語言編譯器
  - 進階最佳化技術

- **[Building a LISP](https://www.buildyourownlisp.com/)**
  - 用 C 實現 LISP 直譯器
  - 從解析到求值的完整過程

### 🛠️ 編譯器框架與專案

**產業級框架：**

- **[LLVM](https://llvm.org/)** - 模組化編譯器基礎架構
  - [LLVM Tutorial](https://llvm.org/docs/tutorial/) - Kaleidoscope 語言教學
  - SSA 中間表示
  - 強大的最佳化 Pass 系統
  - 多目標平臺支援

- **[GCC](https://gcc.gnu.org/)** - GNU 編譯器集合
  - C/C++/Fortran/Ada 等多語言支援
  - GIMPLE 中間表示
  - [GCC Internals](https://gcc.gnu.org/onlinedocs/gccint/)

**現代編譯器專案：**

- **[Rust 編譯器 (rustc)](https://github.com/rust-lang/rust)**
  - [Rustc Dev Guide](https://rustc-dev-guide.rust-lang.org/) - 編譯器開發指南
  - 借用檢查器與生命週期分析
  - MIR（中階中間表示）設計

- **[Cranelift](https://github.com/bytecodealliance/cranelift)**
  - Rust 實現的快速代碼生成器
  - 用於 WebAssembly 和 Rust

- **[TinyCC (TCC)](https://bellard.org/tcc/)**
  - 極小的 C 編譯器
  - 編譯速度極快
  - 適合學習 C 編譯器實現

### 💻 直譯器實作資源

**直譯器教學專案：**

- **[Write an Interpreter in Go](https://interpreterbook.com/)**
  - Monkey 語言直譯器
  - 用 Go 實現
  - 詞彙分析、語法分析、求值

- **[Build Your Own Lisp in C](https://www.buildyourownlisp.com/)**
  - 從零開始的 LISP 直譯器
  - 理解 S-表達式與求值

- **[mal (Make a Lisp)](https://github.com/kanaka/mal)**
  - 用任何語言實現 LISP
  - 支援超過 80 種語言版本
  - 逐步引導的教學

**虛擬機設計：**

- **[Write a Simple 16-bit VM](https://www.jmeiners.com/lc3-vm/)**
  - LC-3 虛擬機實現
  - 理解指令集與執行循環

- **[A Python Interpreter Written in Python](https://www.aosabook.org/en/500L/a-python-interpreter-written-in-python.html)**
  - Byterun：Python 位元組碼直譯器
  - 理解 CPython 內部運作

### 🔬 進階主題

**最佳化技術：**

- **[SSA Book](https://pfalcon.github.io/ssabook/latest/book-full.pdf)** - Static Single Assignment 形式
- **[Optimizing Compilers](https://www.clear.rice.edu/comp512/)** - Rice 大學課程

**型別系統：**

- **[Type Systems](http://lucacardelli.name/Topics/TypeSystems/)** - Luca Cardelli
- **[Types and Programming Languages (TAPL)](https://www.cis.upenn.edu/~bcpierce/tapl/)** - Benjamin Pierce

**垃圾回收：**

- **[The Garbage Collection Handbook](https://gchandbook.org/)**
- **[Baby's First Garbage Collector](https://journal.stuffwithstuff.com/2013/12/08/babys-first-garbage-collector/)**

### 🎯 實作練習建議

**初學者專案（1-2 週）：**
1. 正規表達式引擎（詞彙分析基礎）
2. JSON/INI 解析器（練習遞迴下降）
3. 簡單計算器（含變數）
4. Lisp 子集直譯器

**中階專案（4-8 週）：**
1. Lox 語言完整實現（跟隨 Crafting Interpreters）
2. Scheme 子集編譯器
3. Stack-based 虛擬機
4. 簡單型別推導系統

**進階專案（12+ 週）：**
1. LLVM 前端（自定義語言 → LLVM IR）
2. JIT 編譯器（結合直譯與編譯）
3. 增量編譯器（如 TypeScript）
4. 帶 GC 的語言實現

### 🌐 社群與論壇

- **[/r/Compilers](https://www.reddit.com/r/Compilers/)** - Reddit 編譯器社群
- **[LLVM Discourse](https://discourse.llvm.org/)** - LLVM 官方論壇
- **[Compiler Explorer (Godbolt)](https://godbolt.org/)** - 線上編譯器探索工具

## 編譯器相關延伸閱讀

### 編譯器工具鏈
- [LLVM 編譯器架構與語言效能深度解析](../tools/llvm_guide.md)
- [Cross Compiler 與 LLVM vs GCC 完整解析](../tools/cross-compiler-llvm-gcc-guide.md)
- [Linker and Loader Guide](../kernel/linker-loader-guide.md)

### 虛擬機與執行時環境
- [WebAssembly 相容性與載入器完整指南](../web/wasm_compatibility_guide.md)
- [WebAssembly (WASM) 完整開發指南](../web/webassembly_complete_guide.md)

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

---

## 編譯器開發實用工具

### 解析器生成器 (Parser Generators)

| 工具 | 語言 | 特色 |
|------|------|------|
| **[ANTLR](https://www.antlr.org/)** | Java/C#/Python/C++/Go | 強大的 LL(*) 解析器，支援多種目標語言 |
| **[Bison](https://www.gnu.org/software/bison/)** | C/C++ | GNU 項目，LALR 解析器生成器 |
| **[Yacc](http://dinosaur.compilertools.net/)** | C | 經典的 LALR 解析器 |
| **[PEG.js](https://pegjs.org/)** | JavaScript | PEG 解析器，適合 JS 生態 |
| **[Pest](https://pest.rs/)** | Rust | Rust 的 PEG 解析器 |
| **[Tree-sitter](https://tree-sitter.github.io/tree-sitter/)** | 多語言 | 增量解析器，用於編輯器與代碼分析 |

### 詞彙分析工具 (Lexer Generators)

| 工具 | 語言 | 特色 |
|------|------|------|
| **[Flex](https://github.com/westes/flex)** | C/C++ | Fast Lexical Analyzer，業界標準 |
| **[Lex](http://dinosaur.compilertools.net/)** | C | 經典詞彙分析器生成器 |
| **[RE/flex](https://www.genivia.com/doc/reflex/html/)** | C++ | 現代化的 Flex 替代品 |

### 中間表示與最佳化框架

- **[LLVM](https://llvm.org/)** - 模組化編譯器框架，SSA 形式
- **[MLIR](https://mlir.llvm.org/)** - 多層次中間表示（用於機器學習編譯器）
- **[Graal](https://www.graalvm.org/)** - 多語言 JIT 編譯器
- **[Cranelift](https://cranelift.dev/)** - 快速代碼生成器（Rust）

### 除錯與分析工具

- **[Valgrind](https://valgrind.org/)** - 記憶體檢查與性能分析
- **[GDB](https://www.gnu.org/software/gdb/)** - GNU 除錯器
- **[LLDB](https://lldb.llvm.org/)** - LLVM 除錯器
- **[perf](https://perf.wiki.kernel.org/)** - Linux 性能分析
- **[Flamegraph](https://www.brendangregg.com/flamegraphs.html)** - 視覺化性能分析

---

## 快速參考

### 編譯器實作核心步驟

```
1. 詞彙分析 (Lexical Analysis)
   輸入：源代碼字串
   輸出：Token 流
   工具：手寫/Flex/Lex

2. 語法分析 (Syntax Analysis)
   輸入：Token 流
   輸出：抽象語法樹 (AST)
   方法：遞迴下降/LL/LR/PEG
   工具：手寫/ANTLR/Bison

3. 語意分析 (Semantic Analysis)
   - 符號表建立與查詢
   - 型別檢查
   - 作用域解析
   輸出：帶標註的 AST

4. 中間代碼生成 (IR Generation)
   輸入：AST
   輸出：中間表示（如 LLVM IR、三地址碼）

5. 最佳化 (Optimization)
   - 控制流分析（CFG）
   - 資料流分析（DFA）
   - SSA 轉換
   - 常見優化：
     * 常數折疊
     * 死代碼消除
     * 公共子表達式消除
     * 迴圈不變量外提
     * 內聯

6. 代碼生成 (Code Generation)
   - 指令選擇
   - 暫存器分配
   - 指令調度
   輸出：組合語言或機器碼
```

### 常見文法類型

| 文法類型 | 解析方法 | 特點 | 適用場景 |
|---------|---------|------|---------|
| **LL(1)** | 遞迴下降 | 左到右掃描，最左推導 | 手寫解析器 |
| **LR(1)** | 移進-歸約 | 左到右掃描，最右推導 | 解析器生成器 |
| **LALR(1)** | LR 簡化版 | 狀態數較少 | Yacc/Bison |
| **PEG** | Packrat | 有序選擇，無歧義 | 現代解析器 |

### 中間表示形式

| IR 類型 | 代表 | 特點 |
|---------|------|------|
| **AST** | 抽象語法樹 | 高階，保留語法結構 |
| **三地址碼** | x = y op z | 簡單，易於最佳化 |
| **SSA** | Static Single Assignment | 每個變數只賦值一次 |
| **CPS** | Continuation-Passing Style | 函數式風格 |
| **字節碼** | JVM bytecode, Python bytecode | 便於直譯執行 |

### 型別系統分類

| 分類維度 | 類型 | 範例語言 |
|---------|------|---------|
| **型別檢查時機** | 靜態 | C, Java, Rust, Haskell |
|  | 動態 | Python, JavaScript, Ruby |
| **型別強度** | 強型別 | Java, Python, Haskell |
|  | 弱型別 | C, JavaScript |
| **型別推導** | 顯式 | C, Java |
|  | 隱式 | Haskell, OCaml, Rust（部分）|

---

## 學習路線圖總結

```
階段 1: 基礎理論（2-4 週）
├─ 自動機理論與形式語言
├─ 正規表達式與 DFA/NFA
└─ 上下文無關文法

階段 2: 前端開發（4-8 週）
├─ 詞彙分析器實作
├─ 語法分析器實作（遞迴下降）
├─ AST 設計與走訪
└─ 符號表與作用域

階段 3: 語意與型別（4-6 週）
├─ 型別檢查
├─ 型別推導（Hindley-Milner）
└─ 錯誤恢復與報告

階段 4: 中端技術（6-8 週）
├─ IR 設計（三地址碼、SSA）
├─ 控制流圖（CFG）
├─ 資料流分析
└─ 基礎最佳化

階段 5: 後端開發（8-12 週）
├─ 指令選擇
├─ 暫存器分配（圖著色）
├─ 指令調度
└─ 代碼發射

階段 6: 進階主題（持續學習）
├─ JIT 編譯
├─ 垃圾回收
├─ 並行編譯
└─ 特定領域最佳化
``
