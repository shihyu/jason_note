# LLM 常用工具整理

更新：2026-04-07  
原則：優先收官方網站與官方 GitHub Repo，避免二手整理。

## 本地模型 / 推理

- [Ollama](https://ollama.com/)
  - 本地跑開源模型最常見的入門工具，CLI 體驗成熟，適合開發、測試、桌面環境。
- [llama.cpp](https://github.com/ggml-org/llama.cpp)
  - 很多本地模型工具的底層核心，主打 C/C++ 推理，GGUF 生態幾乎都會碰到。
- [vLLM](https://www.vllm.ai/)
  - 偏伺服器端部署，高吞吐量推理服務，常拿來做 OpenAI-compatible API。
- [LM Studio](https://lmstudio.ai/)
  - 本地模型 GUI 工具，對非 CLI 使用者很友善，也支援 SDK、CLI、OpenAI compatibility API。

## API Proxy / Router

- [LiteLLM](https://www.litellm.ai/)
  - 把多家模型供應商包成 OpenAI 格式，常用在統一路由、fallback、成本控管、觀測。

## Agent / Workflow / RAG Framework

- [LangGraph](https://www.langchain.com/langgraph)
  - 做 agent workflow、stateful graph、multi-step orchestration 很常見。
- [LlamaIndex](https://www.llamaindex.ai/)
  - 偏資料連接、RAG、文件索引與 agent workflow，知識庫型應用很常見。
- [AutoGen](https://github.com/microsoft/autogen)
  - 微軟系多 agent framework，適合研究 agent 協作與自動化流程。
- [Flowise](https://flowiseai.com/)
  - 視覺化拖拉式 LLM/Agent/RAG workflow，原型驗證很快。
- [Dify](https://github.com/langgenius/dify)
  - 偏產品化的 LLM app / workflow 平台，適合內部工具、知識庫、簡易 SaaS。
- [CrewAI](https://crewai.com/)
  - 角色分工清晰的多 agent 框架，適合快速建立研究者、开發者、審查者等協作流程。
- [smolagents](https://github.com/huggingface/smolagents)
  - Hugging Face 出的輕量 agent 框架，簡潔易擴展，適合想擺脫 LangChain 複雜度的開發者。
- [Haystack](https://haystack.deepset.com/)
  - deepset 出的開源 RAG / agent 框架，production-grade，適合企業級知識庫建置。
- [mem0](https://github.com/mem0ai/mem0)
  - LLM 的持久記憶層，專為 AI agent 設計跨對話記憶管理，支援使用者、session、agent 層級的記憶存取。

## UI / 知識庫 / Agent 操作層

- [Open WebUI](https://openwebui.com/)
  - 自架 AI 介面常見方案，可接 Ollama 與多種模型服務。
- [AnythingLLM](https://anythingllm.com/)
  - 文件聊天、workspace、RAG、agent 功能整合度高，適合快速做知識助理。
- [browser-use](https://github.com/browser-use/browser-use)
  - 讓 agent 直接操作瀏覽器，適合網頁任務自動化。
- [agent-browser](https://github.com/vercel-labs/agent-browser)
  - Vercel Labs 的 browser agent 實驗專案，適合參考 web agent 互動設計。

## 評測 / Tracing / Observability

- [Langfuse](https://langfuse.com/docs)
  - 開源 LLM engineering 平台，常用來看 traces、prompts、成本、評分。
- [Promptfoo](https://www.promptfoo.dev/)
  - 做 prompt / model eval、regression test、red team 很常見。
- [Phoenix](https://phoenix.arize.com/)
  - 開源 LLM tracing 與 evaluation 工具，常拿來看 RAG / agent 執行品質。

## Coding Agent / 開發輔助

- [Aider](https://github.com/Aider-AI/aider)
  - 終端機內做 AI pair programming 的代表工具之一。
- [OpenHands](https://openhands.dev/)
  - 開源 coding agent 平台，偏自動解 issue、跑流程、操作 repo。
- [Continue](https://github.com/continuedev/continue)
  - 開源 AI coding assistant 生態，適合接 IDE / 本地模型 / 團隊配置。
- [RTK](https://github.com/rtk-ai/rtk)
  - 針對 agent/coding CLI 場景做 token 節省與代理執行。
- [Cursor](https://cursor.com/)
  - AI-first IDE，人氣快速成長，適合日常開發、程式碼生成、重構、debug。

## Agent Protocol

- [MCP (Model Context Protocol)](https://modelcontextprotocol.io/)
  - Agent 與工具之間的標準通訊協定，讓 agent 可以安全地调用外部工具，生態快速成長中。

## Search / Research

- [Tavily](https://tavily.com/)
  - AI 搜尋 API，專為 agent / RAG 設計，可抓取即時網頁與結構化搜尋結果。

## Workflow Orchestration

- [n8n](https://n8n.io/)
  - 視覺化 workflow 工具，可串接 LLM、API、資料庫，適合輕量商務流程自動化。
- [Temporal](https://temporal.io/)
  - 長期執行任務的 workflow engine，強調 fault-tolerant，適合需要長期等待、人工作業摻入的複雜流程。

## Prompt / Design / Skill 類補充

- [ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill)
  - 偏 UI/UX 設計導向的 AI skill 資源，適合拿來補 agent 的設計能力。

## 快速選型

- 想在本地快速跑模型：`Ollama`、`LM Studio`
- 想上正式 API service：`vLLM`、`LiteLLM`
- 想做 RAG / 知識庫：`LlamaIndex`、`Dify`、`AnythingLLM`、`Tavily`、`Haystack`
- 想做 agent workflow：`LangGraph`、`AutoGen`、`Flowise`、`CrewAI`、`smolagents`、`mem0`
- 想做 workflow 自動化：`n8n`、`Temporal`
- 想做瀏覽器任務 agent：`browser-use`、`agent-browser`
- 想做品質追蹤與評測：`Langfuse`、`Promptfoo`、`Phoenix`
- 想做 AI coding：`Aider`、`OpenHands`、`Continue`、`Cursor`
- 想做即時網頁搜尋：`Tavily`
- 想接標準 agent 通訊協定：`MCP`

## 常用組合建議

| 工具名稱 | 類型 / 定位 | 主要功能 | 你適合用在什麼場景 |
| --- | --- | --- | --- |
| LangChain / LangGraph | 多步驟 agent 編排框架 | 串起多個 tool，如搜尋、程式生成、UI、瀏覽器、本地 LLM，做多步驟、條件分支、loop 流程。 | 把 Tavily（Research）、Claude + RTK（Code）、UI-UX-Pro-Max（UI）、agent-browser（瀏覽器）自動編排成 pipeline。 |
| CrewAI / AutoGen | 多 agent（multi-agent）協作框架 | 定義多個角色，如 Researcher、Coder、Reviewer、Designer，自動分工溝通完成任務。 | 後端出身者做全棧原型，自動分工搜尋、寫 code、檢查 UI、生成文件。 |
| mem0 | LLM 持久記憶層 | 跨對話記憶管理，支援使用者、session、agent 層級的記憶存取，讓 agent 具備長期記憶能力。 | 讓 agent 記住使用者偏好、跨 session 上下文，避免每次對話都是全新的 start。 |
| Ollama | 本地 LLM Runtime | 在 Mac / Linux 上本地跑各種開源模型，如 Llama、Qwen、DeepSeek，可當 backup 或敏感資料專用模型。 | 本地測試、重複 query、敏感資料不外洩，再搭配 Tavily 做 hybrid。 |
| Promptfoo | LLM / Agent 測試工具 | 用測試集評估不同 prompt、不同模型、不同 skills 的輸出品質，做 regression test。 | 改完 RTK / Tavily / UI-UX-Pro-Max workflow 後，自動檢查是否變好還是變差。 |
| Sentry（或自建 tracing + SQLite） | 日誌與監控 | 記錄每次 agent call 的輸入、輸出、token、時間、錯誤，方便 debug 與效能分析。 | 把整套 agent 工作流變成可量化的生產系統，方便優化與 debug。 |
| Tavily | AI 搜尋 API | 結構化即時網頁搜尋結果，專為 agent / RAG 設計。 | 做 research 任務、快速抓取事實、給 agent 提供最新資訊。 |
| Cursor | AI-first IDE | 整合 LLM 的程式開發環境，支援智慧補完、重構、debug、聊天。 | 日常開發主力 IDE，想用 LLM 輔助開發但不離開編輯器。 |
| MCP | Agent 通訊協定 | 標準化 agent 與外部工具的溝通方式，生態正在快速擴展。 | 想讓 agent 安全地调用多種外部工具，建立可擴展的工具鏈。 |
| n8n | Workflow 自動化 | 視覺化 workflow 引擎，可串接 LLM、HTTP、資料庫、Slack 等。 | 需要自動化商務流程（如資料同步、通知、報表生成）又想用 LLM 處理自然語言。 |
| Temporal | Workflow engine | 長期任務編排，強調 fault-tolerance，可摻入人工作業。 | 複雜的 long-running 流程，如審批鏈、資料處理 pipeline、需要長期等待的自動化。 |
