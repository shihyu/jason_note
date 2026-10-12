# Ghidra 與 REA：逆向工程框架與 AI Agent 逆向 MCP

> 資料查核日期：2026-10-12（版本號以各 repo 最新 release 為準）

| 專案 | 定位 | 語言 / 授權 | 最新版本 |
|------|------|-------------|----------|
| [NationalSecurityAgency/ghidra](https://github.com/NationalSecurityAgency/ghidra) | 軟體逆向工程（SRE）框架 | Java / Apache-2.0 | Ghidra 12.1.4 |
| [morluto/rea](https://github.com/morluto/rea) | 讓 AI Agent 透過 MCP 做逆向分析 | TypeScript / MIT | rea-agents 6.4.0 |

兩者的關係：**Ghidra 是分析引擎，REA 是把 Ghidra（或 Hopper、IDA）接給 AI Agent 的橋樑**。

---

## Ghidra

美國國家安全局（NSA）開源的軟體逆向工程框架。

- **反組譯 / 反編譯**：支援 x86、ARM、MIPS、PowerPC、RISC-V 等多種處理器架構，可把機器碼還原成類 C 的偽代碼（pseudocode）。
- **GUI + Headless**：除了 GUI 互動分析，也能用 `analyzeHeadless` 做批次自動化分析。
- **腳本擴充**：可以用 Java 或 Python 撰寫腳本與 plugin。
- **協作**：Ghidra Server 支援多人共用專案。

```bash
# 安裝：從 Releases 下載 zip，解壓後執行（需 JDK 21+）
./ghidraRun

# Headless 批次分析
./support/analyzeHeadless /tmp/proj MyProj -import ./a.out
```

相關筆記：[用 AI Agent 與 Ghidra MCP 做基礎逆向工程](reverse-engineering-with-ai-ghidra-mcp.md)

---

## REA（Reverse Engineer Anything）

官網：<https://rea.tools>

**一個 MCP server，讓 Agent 逆向分析二進位檔、應用程式與執行期行為。** 典型用法是：「看到某個 App 的功能 → 讓 Agent 在沒有原始碼的情況下分析它怎麼運作 → 附上證據 → 在自己的專案實作類似功能」。

### 運作方式

Agent 透過 MCP 呼叫 REA 檢查目標，REA 回傳發現與其證據（程式碼、參照、未知處），Agent 再據此追問、解釋或實作。分析在本機執行，CLI 也走相同的流程。

### 可分析的目標（節錄）

| 目標 | 回傳內容 | 需求 |
|------|----------|------|
| Native binaries | 偽代碼、組合語言、strings、symbols、呼叫與參照 | Hopper、Ghidra 或 IDA |
| Go binaries | 編譯器版本、modules、build settings | 內建，不需安裝 Go |
| JavaScript / Electron | modules、imports、source maps、IPC | Node.js、npm |
| Websites | 頁面結構、scripts、網路觀察、截圖 | Chrome 系瀏覽器 |
| .NET assemblies | metadata、CIL 指令、native 相依 | 無（純靜態） |
| Android APK | manifest、classes、反編譯 method | JADX + JDK |
| Firmware | 區段、解包結果 | Binwalk / Unblob（Linux） |
| WASM / EVM bytecode | 區段、WAT、dispatch selectors | WABT / 本地檔案 |

### 快速開始

需要 Node.js 22.x（>=22.19）、24.x（>=24.11）或 26 以上版本。

```bash
# 註冊到 Agent（支援 Claude Code、Codex、Cursor、Gemini CLI 等）
npx rea-agents setup

# 直接在終端機分析 Electron app 目錄或 ASAR
npx -y rea-agents@latest analyze-javascript-application /abs/path/to/app --json

# 全域安裝 CLI
npm install --global rea-agents
rea --help
rea update
```

對 Agent 的提問範例：

```text
Understand how search works in the Notes app, show me the evidence, and build a
similar feature for my project.
```

---

## 兩者差異

| 面向 | Ghidra | REA |
|------|--------|-----|
| 本質 | 逆向工程**分析引擎**（反組譯、反編譯） | **MCP 橋接層**：把各種分析工具接給 AI Agent |
| 操作者 | 人（GUI 點選、寫腳本） | AI Agent（自然語言提問），也可用 CLI |
| 分析範圍 | 以 native binary 為主（ELF、PE、Mach-O、firmware 映像） | native binary 之外，還支援 JS/Electron、網站、.NET、APK、WASM、EVM 等 |
| 是否自帶反編譯器 | 有 | 沒有，native 分析要呼叫 Ghidra、Hopper 或 IDA |
| 輸出 | 偽代碼、函式圖、交叉參照，由人自己解讀 | 結論 + 證據（程式碼位置、參照）+ 未知處，Agent 可以接著實作 |
| 深度與控制 | 高：可手動改型別、重新命名、patch、寫 plugin | 由 Agent 決定追蹤路徑，深度受模型能力與 context 限制 |
| 安裝需求 | JDK | Node.js（native 分析另外需要 Ghidra/Hopper/IDA） |

一句話：**Ghidra 負責「看懂機器碼」，REA 負責「讓 Agent 去問 Ghidra 等工具並整理出答案」。**

---

## 使用場景

### 適合用 Ghidra

1. **CTF / 漏洞研究**：需要逐條指令看控制流程、手動修正型別與結構，找 buffer overflow 等漏洞。
2. **惡意程式分析**：樣本不能交給雲端模型，或需要精確掌握每個分支行為。
3. **韌體 / 嵌入式**：沒有符號的 ARM、MIPS 映像，需要手動設定記憶體映射（memory map）與載入位址。
4. **大量批次分析**：用 `analyzeHeadless` 加上腳本，對上百個 binary 抽取函式或特徵。

```bash
# 例：批次匯入並執行自訂腳本，輸出所有函式名稱
./support/analyzeHeadless /tmp/proj Batch \
  -import ./samples/*.elf \
  -postScript ListFunctions.java \
  -deleteProject
```

### 適合用 REA

1. **看到某個 App 的功能想抄概念**：讓 Agent 追出功能的實作方式，並在自己的專案寫出類似版本。
2. **Electron / JS 桌面 App**：不需要反編譯器，直接分析 ASAR 的 modules、IPC、source maps。
3. **跨格式的目標**：同一個產品裡混著 JS、native add-on、.NET，由 REA 統一用一套 MCP 介面處理。
4. **快速了解陌生 binary**：先讓 Agent 掃一遍 strings、symbols、關鍵函式，產出摘要，再決定要不要進 Ghidra 深挖。

```bash
# 例：分析某個 Electron App 的結構（JSON 輸出，可以交給腳本處理）
rea analyze-javascript-application /opt/SomeApp/resources/app.asar --json
```

```text
# 例：在 Claude Code 對 Agent 提問（native 分析會透過已安裝的 Ghidra 進行）
分析 /usr/bin/xxx 的 license 檢查流程，列出相關函式與證據，標出不確定的地方。
```

### 搭配使用（建議流程）

1. **REA 先探路**：讓 Agent 定位關鍵函式、整理呼叫關係與證據。
2. **Ghidra 深挖**：根據 REA 給的函式位址，在 Ghidra GUI 裡修正型別、重新命名、確認細節。
3. **回到 Agent 實作**：把確認過的邏輯交給 Agent，在自己的專案重寫並測試。

> 注意：只分析你有權分析的軟體，並遵守授權條款（EULA）與當地法規。

- 只需要 CLI 工具鏈 → 參考 [Reverse Engineering CLI Tools](reverse-engineering-tools-linux.md)。
