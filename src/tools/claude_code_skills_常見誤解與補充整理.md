# Claude Code Skills：常見誤解與補充整理

> 本文件整理 **Claude Code 的 skill（技能）機制**中，最常被誤解、混淆或不知道的重點，並補充正確的工程觀點。

---

## 一、最常見的誤解（Misconceptions）

### 誤解 1：skill = plugin / 外掛

❌ **錯誤理解**：
> skill 就是某種要安裝的插件

✅ **正確觀念**：
- skill 是 **Claude Code 內建能力**
- plugin 是 **第三方擴充**

skill 是「本體能力」，plugin 只是加分。

---

### 誤解 2：要手動指定 skill 才會用

❌ 錯誤：
```text
請使用 file skill 幫我改檔
```

✅ 正確：
- **skill 不需要、也不能手動指定**
- Claude 會根據你的指令自動選擇

你只要描述「想完成什麼事」，不是「怎麼做」。

---

### 誤解 3：Claude Code 只是在幫我寫文字版 diff

❌ 錯誤：
> Claude 只是產生 patch，實際還是我來改

✅ 正確：
- Claude Code 會 **直接修改實體檔案**
- 會新增、刪除、同步修改多個檔案
- 行為等級接近真人工程師在操作 repo

---

### 誤解 4：skill 很危險，會亂刪檔 / 亂跑指令

❌ 想像：
> AI 會不會 `rm -rf /`？

✅ 實際：
- 所有 shell / file 行為都有 **安全 guardrail**
- 需要你給權限
- destructive command 會被阻擋或要求確認

Claude Code 預設是 **保守型 agent**。

---

### 誤解 5：skill = tool calling（function calling）

❌ 錯誤：
> skill 只是換個名字的 function call

✅ 正確：
- tool calling：一次性、原子操作
- skill：**多步驟、狀態感知、可回饋的 agent 行為**

skill 是「流程能力」，不是單一 API。

---

## 二、常被忽略但很重要的事實

### 事實 1：skill 是「可組合的」

一個指令可能同時用到：

- repo analysis
- file edit
- shell execution
- error reasoning

你只看到輸入輸出，中間是 agent pipeline。

---

### 事實 2：Claude 會根據專案自動調整 skill 行為

例如：
- 偵測是 C / C++ 專案 → 找 Makefile / CMake
- Python 專案 → 看 pyproject / setup.cfg
- Node.js → 找 package.json

skill 行為 **context-aware**。

---

### 事實 3：skill 並不是「全能 root 權限」

限制包含：
- sandbox
- working directory scope
- 無法任意裝 system package（除非允許）

這是刻意設計的安全邊界。

---

### 事實 4：skill 是 Claude Code 與一般 Chat UI 最大差異

| 項目 | Chat UI | Claude Code |
|----|----|----|
| 改檔 | ❌ | ✅ |
| 跑指令 | ❌ | ✅ |
| 看 repo | ❌ | ✅ |
| Agent loop | ❌ | ✅ |

Claude Code = **AI 工程助理**，不是聊天機器人。

---

## 三、skill vs plugin vs MCP（心智模型）

```text
Claude Code
 ├─ Reasoning（想）
 ├─ Skills（動手，內建）
 │   ├─ File system
 │   ├─ Shell
 │   ├─ Repo analysis
 │   └─ Code editing
 └─ Plugins / MCP（外援）
```

- **skill**：日常工程操作
- **plugin**：特定領域能力（ex: finance, DB）
- **MCP**：對外服務整合

---

## 四、工程師常踩的使用誤區

### ❌ 指令太細
> 幫我打開 A 檔 → 找 B → 改第 32 行

✅ 建議：
> build 失敗，幫我修

讓 agent 自己規劃流程。

---

### ❌ 不敢讓 Claude 跑 command

實務上：
- build / test / lint 反而是 skill 最大價值
- 人工複製錯誤訊息效率更低

---

### ❌ 把 Claude 當 Copilot

Copilot：
- 補程式碼

Claude Code：
- **完成任務**

---

## 五、正確使用心法（總結）

- 描述「目標」，不是「操作步驟」
- 把它當成 junior → mid engineer
- skill 是預設能力，不是 feature toggle
- plugin 是補充，不是核心

---

## 六、適合用 Claude Code skill 的情境

- refactor
- build failure debug
- cross-file 修改
- legacy 專案理解
- test 修復

---

## 七、Claude Code skill 實戰範例（C / Linux 專案：重構 skill）

本章用一個 **典型 Linux / C 專案**，說明 Claude Code 在「重構（refactor）」時，**skill 實際是怎麼運作的**。

### 範例背景

假設你有一個舊專案：

- C 語言
- 多個 `.c / .h`
- 使用 `qsort`
- 有效能瓶頸與可讀性問題

目標：
> 將排序邏輯重構為 `std::sort`（或自寫排序模組），並保持行為一致

---

### 你給 Claude 的指令（關鍵示範）

```text
這個專案排序效能不好，請幫我重構排序相關程式碼，保持行為不變，並跑測試確認
```

👉 **你沒有指定檔名、行號、步驟**

---

### Claude Code 背後實際發生的 skill 行為

#### Step 1：Repo Analysis Skill
Claude 會先：
- 掃描目錄結構
- 找出與排序相關的 `.c / .h`
- 分析 `qsort` 的使用位置

> 這一步等同於工程師的「快速 code reading」

---

#### Step 2：Refactor / Code Editing Skill
Claude 會：
- 建立新的排序 helper（或模組）
- 調整 function signature
- 同步修改 header 與 implementation
- 修正 include / forward declaration

**重點：**
- 不是單點替換
- 是跨檔一致性修改

---

#### Step 3：Build / Shell Skill
Claude 會主動：

```bash
make
make test
```

- 讀取 compiler error / warning
- 回頭修正型別、include、link 問題

這是一個 **agent loop**，不是一次性產生 patch。

---

#### Step 4：行為驗證（Reasoning + Skill）

Claude 會：
- 比對重構前後邏輯
- 確認排序結果一致
- 必要時補測試案例

這一步是「工程判斷」，不是純文字生成。

---

### 為什麼這叫「重構 skill」？

因為它同時具備：

- **結構理解**（不是 regex 取代）
- **跨檔修改能力**
- **build 驗證能力**
- **失敗回饋再修正**

本質上：
> Claude Code 正在做「工程師在 terminal 裡會做的事」

---

### 與一般 Chat / Copilot 的本質差異

| 能力 | 一般 Chat | Copilot | Claude Code |
|----|----|----|----|
| 理解專案 | ❌ | 部分 | ✅ |
| 跨檔重構 | ❌ | ⚠️ | ✅ |
| 跑 build | ❌ | ❌ | ✅ |
| 自動修錯 | ❌ | ❌ | ✅ |

---

### 重構 skill 的使用心法（很重要）

✅ **好的指令方式**
- 描述「目標與限制」
- 讓 Claude 自己決定步驟

❌ **不好的方式**
- 指定每一行怎麼改
- 把它當成 text editor

---

### 什麼時候不適合用重構 skill？

- 架構完全未知、需求未定
- 極度 performance-critical（需人工 micro-opt）
- 安全 / cryptography 核心邏輯

---

### 本章總結

- 重構 skill = 多個 skill 的組合行為
- 強項在 **中大型、可 build 的 C / Linux 專案**
- 最適合用在：
  - legacy code 清理
  - 重複性重構
  - refactor + build 驗證

---

> 這一章可以直接拿去當「工程師 Claude Code 實戰教學」。

