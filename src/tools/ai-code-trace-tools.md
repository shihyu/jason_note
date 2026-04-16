# AI 時代的程式碼結構 / Trace 工具整理

本文整理幾個能在「AI 時代」幫你 trace code、理解程式架構的開源專案，重點放在：

- 能為 LLM／AI 助手建立持久的 code graph 或語意索引
- 能自動產生架構圖、互動視覺化或 Wiki / 文件
- 盡量是 GitHub 上可自架的專案

> 已知工具：`code-review-graph`、DeepWiki（SaaS）就不再重複介紹，只列出與之相關或可替代／互補的開源專案。

---

## 快速選擇建議

- **如果你已經大量用 Claude / Cursor 做 code review，且想把 token 花在真正相關的檔案上：**
  - 用 `better-code-review-graph`（code-review-graph 的強化版）。[web:12]
- **如果你想要「一鍵把整個 repo 變成可查詢的 Wiki + Mermaid 架構圖」：**
  - 用 `deepwiki-open`。
- **如果你只想快速把任一 GitHub repo 變成互動架構圖（適合看 OSS 或 onboarding）：**
  - 用 `GitDiagram` 或 `CodeBoarding`。
- **如果你要的是「架構文件 + 多種層級的圖」並能做靜態分析 + AI 混合：**
  - 用 `code-architecture-mapper`。
- **如果你想在 VS Code 裡直接從程式碼自動生出架構圖：**
  - 用 `Swark`。
- **如果你更關心長期的 code metrics / 熱點分析：**
  - 用 `CodeCharta` 搭配 SonarQube 等工具。
- **如果你只想在 README 裡自動放一張 repo 結構圖：**
  - 用 `githubocto/repo-visualizer`。

---

## 工具概觀表

| 專案 | 主要定位 | AI 整合方式 | 適用情境 | 語言／平台 | GitHub 連結 |
| --- | --- | --- | --- | --- | --- |
| better-code-review-graph | 為 AI 助手建立本地 code graph，讓 review 只看相關檔案[web:12] | 用作 Claude / Cursor 等工具的 MCP server，讓 LLM 查圖而不是掃全 repo[web:9][web:12] | Code review、影響範圍分析、減少 token 消耗 | 多語言（Tree-sitter 支援的主流語言）[web:1][web:4] | https://github.com/n24q02m/better-code-review-graph[web:12] |
| deepwiki-open | 把任意 GitHub/GitLab/Bitbucket repo 變成可對話的 Wiki，含 Mermaid 圖[web:35] | 用 Gemini / OpenAI 等模型做 RAG，產生文件與回答問題[web:32][web:35] | 快速理解陌生 repo、團隊 onboarding、為 AI agent 準備 context | 任何能被 Git 提取的程式碼，後端自己 clone repo[web:32][web:35] | https://github.com/AsyncFuncAI/deepwiki-open[web:13][web:35] |
| GitDiagram | 將任一 GitHub repo 轉成可點擊的架構圖，直接連回原始碼[web:16][web:19] | 以 GPT 家族模型分析檔案樹與 README，輸出 Mermaid 圖並可下載 PNG[web:19][web:16] | 想快速看 OSS 專案架構、教學示意、初次閱讀大型專案 | 只要是 public GitHub repo 即可，支援自架與瀏覽器使用[web:16][web:19][web:25] | https://github.com/ahmedkhaleel2004/gitdiagram[web:19] |
| CodeBoarding | 將 codebase 變成可互動的多層級圖，結合靜態分析與 LLM[web:11][web:17][web:26] | 先做 Control Flow Graph / 靜態分析，再用 LLM 產生成熟的 onboarding 圖與文件[web:11][web:17] | 想看 AI 在寫什麼／改什麼、團隊 onboarding、長期維護大型專案 | 目前以 Python 為主，透過 LSP / 靜態分析，支援 web 與 VS Code 整合[web:11][web:17][web:26] | https://github.com/CodeBoarding/CodeBoarding[web:26] |
| code-architecture-mapper | 對 GitHub repo 做靜態分析 + LangGraph agent，產生架構說明與多種圖表[web:8] | 利用 LangGraph agent 解讀靜態分析結果，寫 Markdown 架構說明與 Mermaid 圖，並自動修正圖錯誤[web:8] | 想產出「正式一點」的架構文件（MD + 圖）、分析核心檔案與 centrality | 目前重點在 Python、JS/TS（Grimp + Tree-sitter）[web:8] | https://github.com/shikhar1verma/code-architecture-mapper[web:8] |
| Swark | VS Code extension，從程式碼自動產生架構圖，與 GitHub Copilot 整合[web:21] | 透過 LLM 從檔案抽象出 architecture diagram，邏輯放在 LLM 而非硬編碼 parser[web:21] | 想在編輯器內直接看架構圖，不想自己維護解析器 | 任意語言（理論上，只要 Copilot 能看懂）[web:21] | https://github.com/swark-io/swark[web:21] |
| CodeCharta | 將軟體架構與 code metrics 視覺化成「城市地圖」[web:31][web:34] | 本身較偏靜態分析與 metrics，AI 可另外疊在其產生的資料上 | 想看複雜度、修改頻率、coverage 熱點等，協助重構與架構治理[web:34] | 透過 SonarQube 等取得 metrics，支援 C/C++/C#/Java 等多種語言[web:34] | https://github.com/maibornwolff/codecharta[web:31][web:40] |
| githubocto/repo-visualizer | GitHub Action，自動產生 repo 檔案結構的 SVG 圖[web:30][web:20] | 本身不含 LLM，但可作為 AI agent 的「基礎視覺化輸入」 | 想在 README 裡自動附上專案結構圖，或做最基礎的結構可視化[web:30][web:37] | 任何在 GitHub 上的 repo，透過 Action 執行[web:30][web:33] | https://github.com/githubocto/repo-visualizer[web:30] |

---

## 個別專案簡介與使用情境

### better-code-review-graph

- **定位**：`code-review-graph` 的加強版 fork，針對原專案修正了關鍵 bug，加入可配置的 embeddings 與更完整的 CI/CD。[web:12]
- **核心想法**：利用 Tree-sitter 建立函式、類別、import、呼叫關係等結構圖，存到本地 SQLite，讓 AI coding assistant 只讀「與這次改動有關」的檔案。[web:1][web:4][web:9]
- **適合情境**：
  - 你已經在用 Claude Code / Cursor / Windsurf 等工具，覺得「整 repo 掃太貴、太吵」。[web:9]
  - 想做 impact analysis（改這支 function 會炸到哪些 call site / test）。[web:1][web:4]
- **優點**：
  - 完全本地、無雲端、無 telemetry，對公司 code 也較安心。[web:1][web:4]
  - 透過 MCP，可以很自然地接到多種 IDE / agent 流程。[web:9][web:12]
- **可能缺點**：
  - 需要先建好 graph 並與你的 AI 工作流整合，初期要花點時間調教。

---

### deepwiki-open

- **定位**：DeepWiki 的開源後端／自架版，接 GitHub / GitLab / Bitbucket repo，自動產生 Wiki + 圖表 + 問答介面。[web:35]
- **功能重點**：
  - 解析程式碼結構，為每個 repo 建立 Wiki 章節與文件層級。[web:35][web:38]
  - 自動產生 Mermaid 架構與資料流圖，搭配互動式文件頁面。[web:35][web:10]
  - 內建 RAG API，支援 Google Gemini、OpenAI、OpenRouter、Ollama 等模型，提供串流回答。[web:32][web:35]
  - 支援私有 repo（個人 access token）、多語系 README 等。[web:35]
- **適合情境**：
  - 團隊 onboarding：新人可以直接在 DeepWiki 問「認證流程怎麼走」、「這個 service 負責什麼」。[web:2][web:5]
  - 你在做 AI agent（例如 Sidekick、Cursor rules generator）時，想要一個穩定的「架構摘要 + 圖」來源。[web:5]
- **優點**：
  - 完整的 API + 自架能力，方便整合到現有內部平台。[web:32][web:35]
  - 文件、架構圖、QA 一次到位，對「理解陌生大型 repo」很有效。[web:2][web:35][web:38]

---

### GitDiagram

- **定位**：一個「把 GitHub repo 轉成互動架構圖」的專案，支援直接把網址中的 `github.com` 改成 `gitdiagram.com` 來生成圖表。[web:16][web:19][web:25]
- **功能重點**：
  - 即時把 repo 檔案結構轉成系統設計／架構圖，可點擊節點回到原始碼位置。[web:16][web:19]
  - 使用 GPT-5 系列模型（或相容 API）分析檔案樹與 README，產出 Mermaid.js 圖，並可匯出 PNG 或複製 Mermaid 原始碼。[web:19][web:16]
  - 支援自架部署與未來的 CLI / MCP / 瀏覽器擴充等整合（issue 中已有相關討論）。[web:19]
- **適合情境**：
  - 快速理解開源專案結構、寫部落格或投影片時需要簡單清楚的架構示意圖。[web:16]
  - 搭配 LLM：先用 GitDiagram 產生架構圖，再把 Mermaid 丟給模型當「高階 context」。
- **優點與限制**：
  - 上手極快，新手也容易懂。[web:16]
  - 目前主要支援 GitHub repo，對私有 repo / 其他 git 提供者需要依照專案 roadmap 追蹤。[web:19]

---

### CodeBoarding

- **定位**：從靜態分析與 Control Flow Graph 出發，用 LLM 生成多層級互動圖與 onboarding 文件的工具。[web:11][web:17][web:23]
- **功能重點**：
  - 先透過 LSP / 靜態分析建立 CFG，再用 LLM 生成功能區塊、架構圖與步驟說明，而不是單純 prompt 要模型「隨便畫圖」。[web:11][web:17]
  - 產出的圖可以多層 drill-down：先看 20 個左右的高階 cluster，再往下展開內部結構。[web:11]
  - 已公開多個範例 onboarding（例如 opencv-python），並已完全開源。[web:17][web:23][web:26]
- **適合情境**：
  - 你想要一套「能長期維護」的 codebase onboarding 文件，而不只是一次性的圖。[web:17][web:23]
  - 想搭配 AI 開發：在讓 agent 大改程式前，可以先看 CodeBoarding 產生的視覺化來確認方向。[web:23][web:29]
- **優點**：
  - 靜態分析先行，可以避免 LLM 完全憑想像亂畫架構圖的問題。[web:11]
  - 本身就是為「人類 + AI」共用而設計，適合你的 agent pipeline。

---

### code-architecture-mapper

- **定位**：透過「靜態分析 + AI agent」的 hybrid 模式，從 GitHub repo 自動產出：架構說明 Markdown、Mermaid 圖、多種視角的架構視圖與 centrality 分析。[web:8]
- **功能重點**：
  - clone 公開 GitHub repo，對 Python 使用 Grimp，對 JS/TS 使用 Tree-sitter 做依賴分析。[web:8]
  - 用 LangGraph agent 產生可讀性高的 Architecture Overview（Markdown），並產出多種模式的 Mermaid 圖：Overview / Grouped / Detailed / Structure。[web:8]
  - 自動修正模型產生的圖錯誤（例如 Mermaid 語法錯誤），並提供檔案 centrality（fan-in / fan-out）來找熱點。[web:8]
- **適合情境**：
  - 想一次拿到「文字＋圖＋指標」的架構文件，用於設計 review 或 refactor 規劃。
  - 想為開源專案補齊 architecture.md 類型的文檔。
- **優點**：
  - 挺適合作為內部「一鍵產出架構說明」的基礎服務，結果可以再進一步編輯。
  - 已經把「圖語法修正」這類瑣事包起來，減少你自己反覆 prompt 的工夫。[web:8]

---

### Swark

- **定位**：VS Code extension，利用 LLM 從程式碼自動產生架構圖，與 GitHub Copilot 深度整合。[web:21]
- **功能重點**：
  - 預設與 GitHub Copilot 整合，使用者不需另外設定 API key。[web:21]
  - 把「如何解析語言／框架」的邏輯交給 LLM，因此理論上可支援任何語言，不必逐一實作 parser。[web:21]
  - 完全開源，可以檢查實作細節或自行擴充。[web:21]
- **適合情境**：
  - 你以 VS Code 為主力 IDE，又已經在用 Copilot，希望一鍵從現有專案生出架構圖。
  - 想要「隨開即用」的架構圖，而不是跑一堆 CLI 或額外服務。

---

### CodeCharta

- **定位**：專注在「軟體城市」視覺化的工具，把複雜度、變更頻率、測試覆蓋等 metrics 視覺化，輔助架構與重構決策。[web:31][web:34]
- **功能重點**：
  - 利用 SonarQube、SourceMonitor 等工具匯入 metrics，然後把專案畫成 city map，每個 building 代表檔案或模組，大小與顏色對應不同指標。[web:34]
  - 可以比較不同時間點的「城市」，看出哪些區域變得更複雜或改動頻繁。[web:34]
  - 提供桌面版、線上版與 Docker 部署方式，維護方便。[web:31][web:34]
- **適合情境**：
  - 架構審查、技術債盤點、決定 refactor / rewrite 優先順序。[web:34]
  - 作為 AI agent 的輔助輸入：例如告訴 agent「先從這些複雜度最高的 building 開始看」。
- **補充**：
  - 本身不是 LLM 工具，但非常適合作為 AI pipeline 的「可視化與指標層」，在 AI 時代仍然很有價值。[web:34][web:36]

---

### githubocto/repo-visualizer

- **定位**：GitHub Next 的實驗性專案，以 GitHub Action 產生 repo 檔案結構的 SVG 圖，常見做法是直接嵌在 README 裡。[web:30][web:20][web:37]
- **功能重點**：
  - 作為 Action 跑在 CI 中，每次 push 時更新 diagram.svg。[web:30][web:37]
  - 可以透過 `excluded_paths`、`excluded_globs` 等參數排除 node_modules、build 產物等雜訊。[web:30][web:33]
  - 產出的只是一張靜態 SVG，沒有 LLM 參與，但可以讓 AI 更容易理解 repo 結構（把圖餵給多模態模型）。
- **適合情境**：
  - 想要「零互動」的簡單可視化，把專案結構直接展示在 README 或文件裡。[web:30][web:37]
  - 當作其他工具（例如 DeepWiki、GitDiagram）的輕量補充。

---

## 與你現有流程的搭配建議

- **搭配 Claude / Cursor 這種 IDE 內 AI 助手**：
  - 用 `better-code-review-graph` 建立本地 graph，讓 assistant 查圖再決定要載入哪些檔案，減少 token 消耗與噪音。[web:1][web:4][web:9][web:12]
- **搭配你自己寫的 multi-agent／RAG 系統**：
  - 用 `deepwiki-open` 提供「架構 Wiki + 圖」層，讓其他 agent 直接 query；Sidekick 這類工具就是這樣用 DeepWiki 來產生 claude.md / cursorrules.md 等摘要。[web:5][web:32][web:35]
  - `code-architecture-mapper` 可以當成一個「一次性產生架構文件」的離線步驟，把結果存到 repo 或 knowledge base 裡。[web:8]
- **作為人類開發者的「視覺輔助」**：
  - Onboarding 新人或看 OSS：優先考慮 `GitDiagram`、`CodeBoarding`，視覺化程度高、成本低。[web:16][web:19][web:17][web:23]
  - 做 refactor / 架構治理：先用 `CodeCharta` 看熱點，再搭配 AI 工具寫實際 refactor 計畫。[web:34][web:31]
- **IDE 內即時查看**：
  - 如果你主力是 VS Code + Copilot，可以試 Swark，把架構圖生成流程塞回到編輯器體驗裡。[web:21]

這幾個專案大多可以互補而不是互斥：你可以先用 `CodeCharta`、`code-architecture-mapper` 與 `deepwiki-open` 打好「架構與文件地基」，再讓 `better-code-review-graph`、`GitDiagram`、`CodeBoarding` 等工具服務日常 AI coding／review 流程。