# 2026 AI 術語詞典｜最新技術名詞完整解析

> 資料來源：網路爬梳 2026 最新資訊

## AI 名詞分層地圖

```
基礎 → 模型 → 知識 → 工具 → 執行 → 管理（Harness）
```

## 完整術語表

| 名詞 | 中文 | 核心作用 | 白話理解 | 層級 |
|---|---|---|---|---|
| **AI** | 人工智慧 | 模擬人類智能 | 聰明的電腦 | 基礎 |
| **ML** | 機器學習 | 從資料學習 | 自己找規律 | 基礎 |
| **DL** | 深度學習 | 多層神經網路 | 大腦神經元 | 基礎 |
| **NLP** | 自然語言處理 | 理解人類語言 | 電腦聽懂人話 | 基礎 |
| **CV** | 電腦視覺 | 理解圖像 | 電腦看懂照片 | 基礎 |
| **LLM** | 大型語言模型 | 文字理解生成 | 超強聊天機器人 | 模型層 |
| **Multimodal** | 多模態模型 | 文字+圖片+聲音 | 全能型 AI | 模型層 |
| **GenAI** | 生成式 AI | 產生新內容 | 會創作的 AI | 生成層 |
| **Prompt** | 提示詞 | 給模型指令 | 你怎麼問它 | 互動層 |
| **Prompt Eng** | 提示工程 | 優化問法 | 問對問題 | 互動層 |
| **RAG** | 檢索增強生成 | 先查資料再答 | 查書再回答 | 知識層 |
| **Embedding** | 向量表示 | 文字變數學 | 文字座標 | 知識層 |
| **Vector DB** | 向量資料庫 | 語意搜尋 | 聰明資料庫 | 知識層 |
| **Fine-tuning** | 微調 | 專業再訓練 | 教特定技能 | 模型調整 |
| **RLHF** | 強化學習人類回饋 | 用好評訓練 | 按讚越多越好 | 模型調整 |
| **Tool** | 工具 | 外部能力 | AI 用的器具 | 工具層 |
| **Function Calling** | 函式調用 | 呼叫 API | AI 按鈕 | 工具層 |
| **MCP** | 模型上下文協議 | 標準工具連接 | 通用插頭 | 工具層 |
| **Skill** | 技能模組 | 任務 SOP | 工作手冊 | 方法層 |
| **Plugin** | 外掛 | 功能擴充 | 安裝新功能 | 方法層 |
| **Workflow** | 工作流 | 固定流程 | 自動化流程 | 執行層 |
| **Agent** | 智能代理 | 自主執行任務 | 自動助理 | 執行層 |
| **Memory** | 記憶 | 保存狀態 | AI 的筆記本 | 狀態層 |
| **Context Window** | 上下文窗口 | 一次能讀多少 | 短期記憶容量 | 狀態層 |
| **Harness** | 駕馭工程 | **生產管理系統** | **安全駕駛** | **管理層** |

## Harness Engineering 細分

| Harness 支柱 | 功能 | 台股 Agent 例子 |
|---|---|---|
| **資源管理** | Token/成本控制 | 每月上限 $500 |
| **狀態管理** | 記憶持久化 | 記住你的格式偏好 |
| **上下文工程** | 動態 Context | 只給最新 10 筆新聞 |
| **安全邊界** | 權限控制 | 不能改生產資料 |
| **可觀測性** | 監控追蹤 | 失敗自動重試 3 次 |

## 完整關係鏈

```
Prompt（問）→ LLM（答）→ RAG/MCP（查/連）→ Skill（方法）→ Agent（執行）→ Harness（管理）
```

## 2026 生產 Checklist

```
✅ LLM：GPT-4.5 / Claude 3.7 / Gemini 2.0
✅ RAG：內部文件 + 權威新聞
✅ MCP：標準 API 連接
✅ Skill：10+ 台股分析模板
✅ Agent：研究+寫作+審核協作
✅ Harness：五大支柱全到位
→ 每天自動 50 份研究報告
```

## 最重要洞見

**企業贏家公式**：
```
成功 = 85% Harness + 15% 模型
```

**開發者必記**：
```
沒有 Harness 的 Agent = 危險玩具
有完整 Harness 的 Agent = 生產武器
```

---

## 進階術語補充

### 模型訓練與優化

| 名詞 | 中文 | 核心作用 | 白話理解 | 層級 |
|---|---|---|---|---|
| **Pre-training** | 預訓練 | 大量通用資料訓練 | 基礎教育 | 模型訓練 |
| **Transfer Learning** | 遷移學習 | 把A技能用在B任務 | 觸類旁通 | 模型訓練 |
| **Continual Learning** | 持續學習 | 持續更新知識 | 終身學習 | 模型訓練 |
| **LoRA** | 低秩適配 | 輕量微調技術 | 省資源微調 | 模型訓練 |
| **QLoRA** | 量化+LoRA | 更省資源微調 | 極簡省資源 | 模型訓練 |
| **ColBERT** | 上下文向量檢索 | 更快的語意搜尋 | 精準快速 | 知識層 |

### Agent 進階概念

| 名詞 | 中文 | 核心作用 | 白話理解 | 層級 |
|---|---|---|---|---|
| **ReAct** | 推理+行動 | 思考然後行動 | 先想再做 | 執行層 |
| **Chain of Thought** | 思維鏈 | 逐步推理 | 解題步驟 | 執行層 |
| **Self-Reflection** | 自我反思 | 檢討改進 | 做錯了檢討 | 執行層 |
| **Planning** | 規劃能力 | 任務分解 | 列出步驟 | 執行層 |
| **Short-term** | 短期記憶 | 對話內記住 | 聊完就忘 | 狀態層 |
| **Long-term** | 長期記憶 | 持久化存儲 | 永遠記得 | 狀態層 |
| **Entity Memory** | 實體記憶 | 記住特定人事物 | 認識你 | 狀態層 |
| **System Prompt** | 系統提示詞 | 定義角色行為 | 給AI設人設 | 配置層 |
| **Temperature** | 溫度參數 | 控制創意程度 | 保守vs創意 | 配置層 |
| **Top-p** | 機率採樣 | 多樣性控制 | 答案多樣度 | 配置層 |

### 工具與框架（2026 最新版）

| 名詞 | 中文 | 核心作用 | 白話理解 | 層級 |
|---|---|---|---|---|
| **LangChain** | LangChain框架 | 建立Agent的工具 | 搭建Agent框架 | 工具層 |
| **LangGraph** | LangGraph框架 | 複雜工作流/狀態機 | 圖形化多步Agent | 工具層 |
| **AutoGen** | AutoGen框架 | 微軟多Agent協作 | 多Agent對話 | 工具層 |
| **CrewAI** | CrewAI框架 | 多Agent角色分工 | 團隊分工協作 | 工具層 |
| **Semantic Kernel** | 微軟語意核心 | 企業AI集成 | 微軟生態AI | 工具層 |
| **LlamaIndex** | LlamaIndex框架 | 知識增強檢索 | RAG專用框架 | 工具層 |
| **Mastra** | Mastra框架 | 新興AI框架 | 下一代開發框架 | 工具層 |
| **DeerFlow** | DeerFlow框架 | 新興AI框架 | 下一代開發框架 | 工具層 |
| **Dify** | Dify平臺 | 視覺化Agent平臺 | 拖拽建Agent | 平臺層 |
| **Coze** | Coze平臺 | 位元組Agent平臺 | 快速建Bot | 平臺層 |

### 安全與治理

| 名詞 | 中文 | 核心作用 | 白話理解 | 層級 |
|---|---|---|---|---|
| **Guardrail** | 安全護欄 | 防止錯誤輸出 | AI紅綠燈 | 安全層 |
| **Hallucination** | 幻覺 | 錯誤事實生成 | AI胡說八道 | 安全層 |
| **Jailbreak** | 越獄 | 繞過安全限制 | 破解AI限制 | 安全層 |
| **Alignment** | 對齊 | 讓AI符合人類價值 | 教AI做對 | 安全層 |
| **Prompt Shield** | 提示盾 | 防止注入攻擊 | 抵御Prompt攻擊 | 安全層 |
| **PII Detection** | 個資偵測 | 識別敏感資料 | 保護隱私 | 安全層 |
| **AI Act** | AI法規 | 歐盟AI規範 | AI法律 | 治理層 |
| **Transparency** | 可解釋性 | 知道AI怎麼想 | 透明化 | 治理層 |

### 2026 新興概念

| 名詞 | 中文 | 核心作用 | 白話理解 | 層級 |
|---|---|---|---|---|
| **MCP Server** | MCP伺服器 | 標準化工具伺服器 | 工具供應商 | 工具層 |
| **MCP Client** | MCP客戶端 | 連接工具的客戶端 | 工具消費者 | 工具層 |
| **Skill Registry** | 技能註冊中心 | 集中管理Skill | 技能商店 | 管理層 |
| **Agent Marketplace** | Agent市集 | 買賣Agent | Agent超市 | 管理層 |
| **AI Gateway** | AI閘道器 | 統一接入管理 | AI總機 | 管理層 |
| **Token Pooling** | Token池 | 共享配額控制 | 共用額度 | 管理層 |
| **Fallback LLM** | 備援模型 | 主模型失敗時替補 | 備用AI | 安全層 |
| **Human-in-loop** | 人機回饋 | 人類審核把關 | 人工複核 | 安全層 |
| **Multi-Agent** | 多智能體 | 多個Agent協作 | Agent團隊 | 執行層 |
| **Long-running Agent** | 長時運行Agent | 持久執行任務 | 持久助理 | 執行層 |

### 評估與優化

| 名詞 | 中文 | 核心作用 | 白話理解 | 層級 |
|---|---|---|---|---|
| **BLEU** | BLEU分數 | 文字品質評估 | 翻譯品質 | 評估層 |
| **ROUGE** | ROUGE分數 | 摘要品質評估 | 摘要品質 | 評估層 |
| **Perplexity** | 困惑度 | 模型好壞指標 | 越低越好 | 評估層 |
| **Latency** | 延遲 | 回應速度快慢 | 反應時間 | 效能層 |
| **Throughput** | 吞吐量 | 處理能力 | 同時多少 | 效能層 |
| **Cost per Token** | 每Token成本 | 費用控制 | 省錢指標 | 商業層 |

---

## 2026 AI Agent Framework 完整比較

### 主流框架總覽

| 框架 | 開發者 | 擅長場景 | 生產就緒 | 學習曲線 |
|---|---|---|---|---|
| **LangGraph** | LangChain | 狀態機/複雜工作流 | ⭐⭐⭐⭐⭐ | 中 |
| **CrewAI** | CrewAI | 角色分工/團隊自動化 | ⭐⭐⭐ | 低 |
| **AutoGen** | Microsoft | 多Agent對話 | ⭐⭐⭐⭐ | 中 |
| **Semantic Kernel** | Microsoft | 企業應用/微軟生態 | ⭐⭐⭐⭐ | 中 |
| **LlamaIndex** | LlamaIndex | RAG/知識檢索 | ⭐⭐⭐⭐ | 低 |
| **OpenAI Swarm** | OpenAI | 輕量多Agent | ⭐⭐ | 低 |
| **Anthropic SDK** | Anthropic | Claude原生集成 | ⭐⭐⭐⭐ | 低 |
| **Google ADK** | Google | Gemini原生集成 | ⭐⭐⭐ | 中 |
| **Mastra** | 新興 | 下一代框架 | ⭐⭐⭐ | 中 |

### 框架選擇決策樹

```
你需要什麼？
│
├─ 快速原型 / 低程式碼 → CrewAI / Dify / Coze
│
├─ 複雜狀態機 / 多步流程 → LangGraph
│
├─ 多Agent對話 / 協商 → AutoGen / OpenAI Swarm
│
├─ 企業級 / 微軟生態 → Semantic Kernel
│
├─ RAG 專用 → LlamaIndex
│
└─ 生產級 / 高可控性 → LangGraph + 自建 Harness
```

### Microsoft Agent Framework（新趨勢！）

Microsoft 將 **AutoGen + Semantic Kernel** 合併為 **Microsoft Agent Framework**：
- 1.0 GA 目標：2026 Q1
- 特色功能：
  - Task Adherence：保持Agent在軌道上
  - PII Detection：敏感資料偵測
  - Prompt Shields：防注入攻擊

---

## Harness Engineering 完整解析（2026 核心！）

### 進化三階段

```
Phase 1: Prompt Engineering（提示工程）
         → 問對問題

Phase 2: Context Engineering（上下文工程）
         → 給對資訊

Phase 3: Harness Engineering（駕馭工程）
         → 控制執行
```

### Harness 三層架構

```
┌─────────────────────────────────────────────────┐
│              Layer 3: Orchestration             │
│         (Workflow邏輯 / Agent協調 / 路由)         │
├─────────────────────────────────────────────────┤
│              Layer 2: Runtime Environment        │
│        (工具 / 記憶 / Guardrail / I/O處理)        │
├─────────────────────────────────────────────────┤
│              Layer 1: Model Interface            │
│          (API呼叫 / Prompt組裝 / 回應解析)         │
└─────────────────────────────────────────────────┘
```

### Harness 核心元件

| 元件 | 功能 | 實際範例 |
|---|---|---|
| **Input Validation** | 輸入驗證 | 過濾無效請求 |
| **Context Retrieval** | 上下文檢索 | RAG / 歷史記憶 |
| **Guardrails** | 安全護欄 | 防止幻覺/攻擊 |
| **Tool Integration** | 工具集成 | MCP / Function Call |
| **Retry Logic** | 重試邏輯 | 失敗自動重試 |
| **Output Validation** | 輸出驗證 | 格式/安全性檢查 |
| **Observability** | 可觀測性 | 日誌/監控/追蹤 |

### Harness Engineering 關鍵洞見

**OpenAI 團隊發現**：
> Agent 的瓶頸從來不是寫程式能力，而是周圍系統的結構化、工具和回饋機制

**Anthropic 實踐**：
> 讓 Agent 使用瀏覽器自動化工具做端到端測試，大幅提升準確度和完整性

**核心公式**：
```
Agent = Model + Harness
Harness = Agent - Model
```

---

## 完整關係鏈（更新版）

```
用戶輸入 → Prompt（問）→ 上下文工程 → LLM（推理）→ RAG/MCP（查/連）
     ↓
Skill（方法）→ Agent（執行）→ Memory（記憶）→ Harness（管理）
     ↓
評估（BLEU/Perplexity）→ 安全（Guardrail）→ 輸出給用戶
```

### 生產級系統架構圖

```
┌─────────────────────────────────────────────────────────────┐
│                        使用者介面                            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      AI Gateway（閘道器）                    │
│                  統一接入 / 負載平衡 / 監控                    │
└─────────────────────────────────────────────────────────────┘
          │                    │                    │
          ▼                    ▼                    ▼
   ┌────────────┐       ┌────────────┐       ┌────────────┐
   │  主模型    │       │  備援模型  │       │  專家模型  │
   │ GPT-4.5   │       │ Claude 3.7 │       │ FinBERT   │
   └────────────┘       └────────────┘       └────────────┘
          │                    │                    │
          └──────────┬──────────┴──────────┬─────────┘
                     │                     │
                     ▼                     ▼
          ┌──────────────────┐   ┌──────────────────┐
          │   MCP Server     │   │   RAG 系統        │
          │  (工具連接)      │   │  (知識檢索)       │
          └──────────────────┘   └──────────────────┘
                     │                     │
                     └──────────┬──────────┘
                                │
                     ┌──────────▼──────────┐
                     │     Agent 引擎      │
                     │  (規劃/執行/反思)   │
                     └──────────┬──────────┘
                                │
          ┌─────────────────────┼─────────────────────┐
          │                     │                     │
          ▼                     ▼                     ▼
   ┌────────────┐       ┌────────────┐       ┌────────────┐
   │  記憶系統   │       │   技能系統   │       │  安全系統   │
   │ 短期/長期   │       │   10+ 模板   │       │ Guardrail  │
   └────────────┘       └────────────┘       └────────────┘
                                │
                                ▼
                     ┌──────────────────┐
                     │   Harness 層     │
                     │  資源/監控/治理   │
                     └──────────────────┘
```

---

## 核心觀念速記

### 模型選擇策略

```
簡單任務 → 小模型（快/省）
複雜推理 → 大模型（準）
特定領域 → 微調模型（專）
即時天氣 → Function Call（查）
靜態知識 → RAG（檢索）
```

### 好 Prompt 黃金法則

```
1. 清楚定義角色（你是誰）
2. 明確說明任務（要做什麼）
3. 給出範例（像這樣做）
4. 指定輸出格式（產出長這樣）
5. 限制範圍（不要做X）
```

### Context Assembly 最佳實踐

```
1. Priority Ordering    → 最重要資訊放前面
2. Token Budget        → 控制總長度
3. Compression         → 、必要時壓縮
4. Dynamic Retrieval   → 根據問題取相關
5. Freshness Filter   → 過濾過時資訊
```

### Agent 失敗模式

```
❌ 忘記目標     → 加 System Prompt
❌ 重複執行     → 加 Memory 去重
❌ 胡說八道     → 加 RAG 核查
❌ 過度行動     → 加 Guardrail
❌ 無法停止     → 加 回合限制
❌ 偏離任務     → 加 Task Adherence
❌ 隱私外洩     → 加 PII Detection
❌ Prompt注入   → 加 Prompt Shield
```

---

## 2026 生產級標準

```
✅ 高可用：99.9% 正常運行
✅ 低延遲：< 2 秒回應
✅ 可追蹤：每步有日誌
✅ 可回滾：失敗可恢復
✅ 成本可控：Token 預算
✅ 安全合規：數據不外洩
✅ Prompt 安全：注入防護
✅ 個資保護：PII 偵測
✅ 多模型備援：Fallback LLM
✅ 人機協作：Human-in-loop
```

---

## 必備參考資源

### 官方文件
- [Anthropic Harness Design](https://www.anthropic.com/engineering/harness-design-long-running-apps)
- [Microsoft Agent Framework](https://www.microsoft.com/en-us/research/blog/autogen-v0-4-reimagining-the-foundation-of-agentic-ai-for-scale-extensibility-and-robustness/)
- [LangGraph Documentation](https://langchain.com/langgraph)
- [CrewAI Documentation](https://crewai.com/)

### 開源資源
- [awesome-harness-engineering](https://github.com/ai-boost/awesome-harness-engineering)
- [awesome-cli-coding-agents](https://github.com/bradAGI/awesome-cli-coding-agents)
- [awesome-ai-agent-papers](https://github.com/VoltAgent/awesome-ai-agent-papers)

### 2026 技術趨勢預測
- Gartner：2026 年 40% 企業應用將有任務特定 AI Agent（2025 年 <5%）
- Gartner：2027 年 1/3 Agentic AI 部署將使用多Agent架構

---

這就是 2026 年所有 AI 用詞的**完整生態圖**。現在你手握全圖，要開始打造生產級台股 Agent 了嗎？
