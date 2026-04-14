# Harness / MCP / Skills / CLI 重點整理

---

# 一句話總結

> **高效的 Agent 架構關鍵，不是更強的模型，而是把「確定答案」的工作從 LLM 移到 CLI / CPU。**

也就是：

```text
LLM 負責思考
CLI 負責執行
```

---

# 這篇文章的核心主軸

## 1. Context Window 是最珍貴的資源

```text
Token = Memory
Memory = Cost
Cost = Latency
```

如果沒有良好管理 Context：

- Agent 會變慢
- 成本會變高
- 幻覺會變多

因此：

> **不要把所有事情都交給 LLM。**

---

# 三個核心元件定位（MCP / Skills / CLI）

這三者不是互相取代，而是：

```text
三層責任分工
```

---

# 1️⃣ MCP（Model Context Protocol）

## 定位

```text
Production / Security / Standard Interface
```

## 特點

- 官方支援
- 有權限管理
- 有 schema
- 安全性高
- 適合企業環境

## 缺點

- 啟動成本高
- Context 使用量大
- 較重

## 適用情境

```text
需要安全
需要權限控管
需要穩定 production 系統
```

例如：

- GitHub API
- Database access
- Cloud service
- Payment system

---

# 2️⃣ Agent Skills

## 定位

```text
Custom Tool / Internal Workflow
```

本質：

```text
Markdown + Instruction
```

## 特點

- 可封裝流程
- 可封裝知識
- 彈性高
- 開發成本低

## 缺點

- 還是依賴 LLM 解讀
- non-deterministic

## 適用情境

```text
沒有現成 MCP
沒有 CLI
內部專用工具
```

例如：

```text
deploy_service
backup_database
analyze_log
release_pipeline
```

---

# 3️⃣ CLI（Command Line Interface）

## 定位

```text
Deterministic Execution Engine
```

## 這篇最重要的觀點

> **CLI 是 Token Efficiency 的核心工具。**

## 特點

```text
CPU
fast
cheap
deterministic
```

## 為什麼 CLI 很強

因為它：

```text
有真實輸出
沒有幻覺
結果可驗證
```

例如：

```bash
gh issue create
docker build
pytest
ffmpeg
curl
```

LLM 只需要：

```text
read stdout
```

而不是：

```text
guess result
```

---

# 核心概念：Execution Offloading

## 傳統 Agent

```text
LLM:
  read file
  parse
  calculate
  summarize
  decide
```

全部用 GPU。

---

## 新一代 Agent（Harness 思維）

```text
LLM:
  decide

CLI:
  execute
  calculate
  fetch
  validate
```

這叫：

```text
Execution Offloading
```

或：

```text
Deterministic Pipeline
```

---

# Progressive Disclosure（Skills 的關鍵技術）

## 問題：MCP 很吃 Context

```text
一次載入整個工具說明
```

例如：

```text
OpenAPI schema
function spec
documentation
```

---

## Skills 的解法

```text
Progressive Disclosure
```

流程：

```text
先載入 metadata
需要時才載入 SKILL.md
```

結果：

```text
節省 context
提升速度
降低成本
```

---

# 為什麼 CLI 正在崛起

不是因為 CLI 新。

而是因為：

```text
LLM 太貴
```

---

# CLI 的三個關鍵優勢

## 1. Deterministic

```text
成功 或 失敗
沒有模糊地帶
```

---

## 2. Token Free

```text
不消耗 context
```

---

## 3. CPU Cheap

```text
成本遠低於 GPU
```

---

# Tool Absorption（工具被模型內化）

這是一個長期趨勢：

```text
工具 → 模型能力
```

例如：

## 過去

```text
GitHub MCP
```

## 現在

```text
gh CLI
```

## 未來

```text
model 直接會 Git
```

---

# 正確的實務策略（作者建議）

```text
不是選一個
而是三個並行
```

---

# Decision Table（實戰決策表）

| 情境 | 使用工具 |
|------|----------|
需要安全 / 權限 / production | MCP
沒有現成工具 / 自訂流程 | Skill
標準操作 / 基礎任務 | CLI

---

# 最佳實務架構（推薦）

```text
                LLM
                 │
        ┌────────┼────────┐
        │        │        │
       MCP      Skill     CLI
        │        │        │
   secure API   custom    execution
                logic      engine
```

---

# Harness Engineering 的真正本質

不是：

```text
用更多工具
```

而是：

```text
減少 LLM 的工作量
```

---

# 最重要的工程原則

```text
If the answer is deterministic
→ use CLI

If the answer needs reasoning
→ use LLM
```

---

# 一句話收斂（Final Takeaway）

> **真正高效的 Agent，不是更聰明，而是更少用腦。**

