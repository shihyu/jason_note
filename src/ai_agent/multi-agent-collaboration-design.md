# Agent Teams：從 16 個 Claude 造編譯器看多 Agent 架構設計

這個功能本身還在 research preview 階段，但 [Anthropic](https://zhida.zhihu.com/search?content_id=270271276&content_type=Article&match_order=1&q=Anthropic&zd_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJ6aGlkYV9zZXJ2ZXIiLCJleHAiOjE3NzYwMTY0ODIsInEiOiJBbnRocm9waCIsInpoaWRhX3NvdXJjZSI6ImVudGl0eSIsImNvbnRlbnRfaWQiOjI3MDI3MTI3NiwiY29udGVudF90eXBlIjoiQXJ0aWNsZSIsIm1hdGNoX29yZGVyIjoxLCJ6ZF90b2tlbiI6bnVsbH0.je8mRxtcUU7wYEjI4t9IP9g6awDjPQO30-mnuyx9lWo&zhida_source=entity) 同時放出了一個更有說服力的東西：研究 Ian [Nicholas Carlini](https://zhida.zhihu.com/search?content_id=270271276&content_type=Article&match_order=1&q=Nicholas+Carlini&zd_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJ6aGlkYV9zZXJ2ZXIiLCJleHAiOjE3NzYwMTY0ODIsInEiOiJOaWNob2xhcyBDYXJsaW5pIiwiemhpZGFfc291cmNlIjoiZW50aXR5IiwiY29udGVudF9pZCI6MjcwMjcxMjc2LCJjb250ZW50X3R5cGUiOiJBcnRpY2xlIiwibWF0Y2hfb3JkZXIiOjEsInpkX3Rva2VuIjpudWxsfQ.llENd0bX80KQU8oTpdIDmqM8X7TcCFSpc7AH4HNSB34&zhida_source=entity) 用 16 個 [Claude](https://zhida.zhihu.com/search?content_id=270271276&content_type=Article&match_order=1&q=Claude&zd_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJ6aGlkYV9zZXJ2ZXIiLCJleHAiOjE3NzYwMTY0ODIsInEiOiJDbGF1ZGUiLCJ6aGlkYV9zb3VyY2UiOiJlbnRpdHkiLCJjb250bnRfaWQiOjI3MDI3MTI3NiwiY29udGVudF90eXBlIjoiQXJ0aWNsZSIsIm1hdGNoX29yZGVyIjoxLCJ6ZF90b2tlbiI6bnVsbH0.O-Gn-XNNrButcsna50nW3SmfT3L2QzszKeQm_3t82ew&zhida_source=entity) 實例從零寫了一個能編譯 [Linux Kernel](https://zhida.zhihu.com/search?content_id=270271276&content_type=Article&match_order=1&q=Linux+Kernel&zd_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJ6aGlkYV9zZXJ2ZXIiLCJleHAiOjE3NzYwMTY0ODIsInEiOiJMaW51eCBLZXJuZWwiLCJ6aGlkYV9zb3VyY2UiOiJlbnRpdHkiLCJjb250ZW50X2lkIjoyNzAyNzEyNzYsImNvbnRlbnRfdHlwZSI6IkFydGljbGUiLCJtYXRjaF9vcmRlciI6MSwiemRfdG9rZW4iOm51bGx9.elJAvvWQPEQv3rRSK7xidG5cKcngBG8fDEMVhVFIMRQ&zhida_source=entity) 的 C 編譯器。10 萬行 [Rust](https://zhida.zhihu.com/search?content_id=270271276&content_type=Article&match_order=1&q=Rust&zd_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJ6aGlkYV9zZXJ2ZXIiLCJleHAiOjE3NzYwMTY0ODIsInEiOiJSdXN0IiwiemhpZGFfc291cmNlIjoiZW50aXR5IiwiY29udGVudF9pZCI6MjcwMjcxMjc2LCJjb250ZW50X3R5cGUiOiJBcnRpY2xlIiwibWF0Y2hfb3JkZXIiOjEsInpkX3Rva2VuIjpudWxsfQ.XnFsdGXiVHn6zkF-5kVeLh8cNvY0qV5eJ2mWqJmL7vA&zhida_source=entity) 程式碼。

編譯器本身是個有意思的工程產物，但更值得關注的是背後那套多 Agent 協作的架構設計——它可能是目前最好的一份「如何讓多個 AI Agent 一起幹活」的實戰手冊。

---

## 0. 資料說話 — 先看看這個實驗到底幹了什麼

簡單交代一下背景。

Anthropic 研究 Ian Nicholas Carlini（之前在 Google Brain 和 DeepMind 待了七年）搞了個實驗：讓 16 個 Claude Opus 4.6 實例平行工作，目標是從零實現一個 C 編譯器。

幾個關鍵數字：

- 16 個 Agent 平行，跑了將近 2000 個 Claude Code session
- 兩週時間，花了大約 20,000 美元 API 費用
- 吃掉 20 億 input token，生成 1.4 億 output token
- 產出 10 萬行 Rust 程式碼
- 能編譯 Linux 6.9（x86、ARM、RISC-V 三個架構）
- 還能編譯 PostgreSQL、SQLite、Redis、FFmpeg、QEMU
- [GCC torture test suite](https://zhida.zhihu.com/search?content_id=270271276&content_type=Article&match_order=1&q=GCC+torture+test+suite&zd_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJ6aGlkYV9zZXJ2ZXIiLCJleHAiOjE3NzYwMTY0ODIsInEiOiJHQ0MgdG9ydHVyZSB0ZXN0IHN1aXRlIiwiemhpZGFfc291cmNlIjoiZW50aXR5IiwiY29udGVudF9pZCI6MjcwMjcxMjc2LCJjb250ZW50X3R5cGUiOiJBcnRpY2xlIiwibWF0Y2hfb3JkZXIiOjEsInpkX3Rva2VuIjpudWxsfQ.wU6dHTjlNhrK8hwE2SvyARDLEpHNpAgJ-OhyPrIwbPg&zhida_source=entity) 通過率 99%
- 以及——能編譯並運行 Doom

這些數字確實挺震撼的。但如果你只看到這些，那就錯過了這個項目最精華的部分。

---

## 1. 解剖架構 — 簡單到讓人意外的協作機制

直覺上，多 Agent 協作應該需要一個複雜的框架——orchestrator、message bus、task queue 之類的。

但 Carlini 的方案簡單得出乎意料。

整個架構就三樣東西：

**Docker 隔離**：每個 Agent 跑在自己的 Docker 容器裡，有一個共享的 bare git repo 掛載到 `/upstream`。每個 Agent clone 一份到本地 `/workspace`，幹完活 push 回去。

**Git 檔案鎖**：Agent 要干某個任務之前，先在 `current_tasks/` 目錄下建立一個文字檔「佔坑」。比如一個 Agent 鎖了 `current_tasks/parse_if_statement.txt`，另一個鎖了 `current_tasks/codegen_function_definition.txt`。如果兩個 Agent 搶同一個任務，git 的同步機制會讓後來的那個自動換一個。

**無限循環 harness**：一個極其簡單的 bash 腳本，Claude 完成一個任務後立刻開始下一個，永不停歇。

```bash
#!/bin/bash
while true; do
    COMMIT=$(git rev-parse --short=6 HEAD)
    LOGFILE="agent_logs/agent_${COMMIT}.log"
    claude --dangerously-skip-permissions \
           -p "$(cat AGENT_PROMPT.md)" \
           --model claude-opus-X-Y &> "$LOGFILE"
done
```

沒有 orchestrator。沒有中央調度。沒有 Agent 之間的通訊協議。

每個 Agent 自己決定幹什麼——通常是「下一個最明顯的問題」。遇到 merge conflict？Claude 自己解決。有個 Agent 甚至不小心 `pkill -9 bash` 把自己殺了。

這跟主流 multi-agent 框架的理念完全不一樣。

對比一下 [CrewAI](https://zhida.zhihu.com/search?content_id=270271276&content_type=Article&match_order=1&q=CrewAI&zd_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJ6aGlkYV9zZXJ2ZXIiLCJleHAiOjE3NzYwMTY0ODIsInEiOiJDcmV3QUkiLCJ6aGlkYV9zb3VyY2UiOiJlbnRpdHkiLCJjb250ZW50X2lkIjoyNzAyNzEyNzYsImNvbnRlbnRfdHlwZSI6IkFydGljbGUiLCJtYXRjaF9vcmRlciI6MSwiemRfdG9rZW4iOm51bGx9.mGKsrwNAzP7KgXcdsYJ_ZmYMAqlyuFwLCuZJAhjXsqU&zhida_source=entity)、[AutoGen](https://zhida.zhihu.com/search?content_id=270271276&content_type=Article&match_order=1&q=AutoGen&zd_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJ6aGlkYV9zZXJ2ZXIiLCJleHAiOjE3NzYwMTY0ODIsInEiOiJBdXRvR2VuIiwiemhpZGFfc291cmNlIjoiZW50aXR5IiwiY29udGVudF9pZCI6MjcwMjcxMjc2LCJjb250ZW50X3R5cGUiOiJBcnRpY2xlIiwibWF0Y2hfb3JkZXIiOjEsInpkX3Rva2VuIjpudWxsfQ.XqdegM9rFqEfNcBtTusxWdFOsIhBywU9BGe2kxcP4oQ&zhida_source=entity)、[LangGraph](https://zhida.zhihu.com/search?content_id=270271276&content_type=Article&match_order=1&q=LangGraph&zd_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJ6aGlkYV9zZXJ2ZXIiLCJleHAiOjE3NzYwMTY0ODIsInEiOiJMYW5nR3JhcGgiLCJ6aGlkYV9zb3VyY2UiOiJlbnRpdHkiLCJjb250ZW50X2lkIjoyNzAyNzEyNzYsImNvbnRlbnRfdHlwZSI6IkFydGljbGUiLCJtYXRjaF9vcmRlciI6MSwiemRfdG9rZW4iOm51bGx9.eIqyT7hqSphEV9HJ-4mg-Xee5zkVG2VmuNIS9ib3HSA&zhida_source=entity) 這些框架，它們都在做一件事：設計精巧的通訊和調度機制。但 Carlini 的實驗揭示了一個反直覺的事實：**對於當前的 LLM 能力水平，最簡單的協調機制可能就是最好的。**

Git 本身就是一個分佈式協作協議。檔案鎖就是最原始的任務分配。Docker 就是最天然的隔離。這些東西已經被軟體工程驗證了幾十年，拿來給 Agent 用，居然也 work。

---

## 2. 五條法則 — 從實驗中提煉的工程方法論

Carlini 在部落格裡分享了大量踩坑經驗，提煉一下，有幾條值得關注。

首先是最重要的一條：**測試質量遠比 Prompt 質量重要。** Carlini 原話是：「Claude will work autonomously to solve whatever problem I give it. So it's important that the task verifier is nearly perfect, otherwise Claude will solve the wrong problem.」 Agent 會拚命幹活，但如果你的測試寫得不好，它就會拚命幹錯事。Carlini 自己幾乎沒寫編譯器程式碼，他寫的全是測試和 harness。這意味著人類的角色正在發生根本性轉變——從「寫程式碼的人」變成「設計驗證環境的人」。

然後是一個特別有意思的發現：**你得為 AI 的認知局限做設計。** 這話聽起來有點抽象，舉幾個具體的例子。Context 污染——測試輸出不能太多，如果一次性列印幾千行 log，Agent 的 context window 就被垃圾資訊淹沒了，正確做法是只列印幾行摘要，詳細資訊寫到檔案裡，而且 log 格式要方便 grep。時間盲區——Claude 不知道時間在流逝，不加限制的話它會開心地跑幾個小時的測試而不做任何實際進展，所以 harness 要有一個 `--fast` 模式只跑 1%-10% 的隨機採樣。冷啟動問題——每個 Agent 被扔進一個全新的容器沒有任何上下文，所以要讓 Agent 維護詳細的 README 和進度檔案。這些經驗在任何 Agent 開發場景裡都適用，不只是編譯器。

第三，也是整個項目最精彩的工程技巧：**用 Oracle 做二分，把不可平行變成可平行。** 當 Agent 們開始編譯 Linux Kernel 的時候遇到了大問題——編譯核心是一個巨大的整體任務，不像測試套件那樣可以一人一個，結果 16 個 Agent 全卡在同一個 bug 上，互相覆蓋對方的修改，16 個 Agent 跟 1 個沒區別。Carlini 的解決方案是用 GCC 作為「Oracle」（已知正確的參考實現），隨機選大部分核心檔案用 GCC 編譯，只讓少量檔案用 Claude 的編譯器。如果核心能跑，說明問題不在 Claude 編譯的那些檔案裡；如果掛了，就進一步縮小範圍。這樣每個 Agent 就可以平行地在不同檔案裡找 bug 了。

還有兩點值得一提。**角色分工**——Carlini 不是讓 16 個 Agent 都干同樣的事，有的專門合併重複程式碼（LLM 寫程式碼特別愛重複造輪子），有的專門最佳化性能，有的從 Rust 開發者視角做 code review，有的專門寫文件。這種分工方式其實很像人類團隊。以及**簡單協調就夠了**——Carlini 明確說了不用 orchestrator，不用複雜框架，git + 檔案鎖 + Docker 就搞定了。換句話說：**當前階段，與其花精力設計複雜的 Agent 通訊協議，不如把精力花在設計更好的測試和反饋環境上。**

---

## 3. 冷靜一下 — 被忽略的另一面

說了這麼多好的，該潑點冷水了。

首先，這個編譯器有不少硬傷。缺少 16-bit x86 後端，啟動 Linux 的 real mode 階段還得靠 GCC。自帶的 assembler 和 linker 還有 bug，demo 視訊其實用的是 GCC 的。開了全部最佳化，生成的程式碼效率還不如 GCC 關掉所有最佳化。Rust 程式碼質量「reasonable」，但離專家水平差得遠。新功能和 bug fix 經常破壞已有功能，regression 頻發。

Ars Technica 的報導提了一個特別關鍵的點：**C 編譯器是一個「近乎理想的 AI 任務」。** 規範成熟了幾十年，測試套件現成的，有 GCC 這個參考實現可以對比。大多數真實世界的軟體項目，這三個條件一個都不具備。

用他們的原話說：「The hard part of most development isn't writing code that passes tests; it's figuring out what the tests should be in the first place.」

這句話值得反覆品味。

然後是「clean-room」的爭議。Carlini 說 Agent 在開發過程中沒有聯網，所以是 clean-room 實現。但 Hacker News 上很多人不買賬——模型訓練資料裡大機率包含了 GCC、Clang 等編譯器的原始碼。傳統軟體工程裡的 clean-room 是指實現者從未看過原始程式碼，按這個標準，這算不上。

GitHub issue 區的評論也值得看看。有人說：「如果我去超市偷了每種麵包的一點，拼在一起，沒人會說我從零做了麵包。」

還有 20,000 美元 這個數字。它只是 API token 的費用，不包括訓練模型花的幾十億美元、Carlini 本人搭建 harness 的人力成本、以及幾十年來編譯器工程師們建立的測試套件和參考實現。

不一定對，但這個實驗的價值可能不在於「AI 能寫編譯器」，而在於它展示了一種新的工作方式。

---

## 4. 四種模式 — 多 Agent 協作的架構圖譜

跳出這個實驗本身，聊聊多 Agent 協作的幾種主流架構模式。理解這些模式，能幫你判斷什麼場景該用什麼方案。

**Orchestrator 模式**就像一個項目經理——一個中央 Agent 負責分解任務、分配給 worker Agent、彙總結果。優點是控制力強，缺點是 orchestrator 本身成為瓶頸，它需要理解整個項目的全貌，這對 LLM 的 context window 是個巨大挑戰。CrewAI 和早期的 AutoGen 基本是這個思路。

**Pipeline 模式**像流水線，Agent 按順序接力，前一個的輸出是後一個的輸入。適合有明確階段的任務，比如「分析需求 → 設計架構 → 寫程式碼 → 寫測試 → code review」。缺點是不能平行，一個環節卡住全鏈路等。

**Swarm 模式**就是 Carlini 這個實驗用的。沒有中央調度，每個 Agent 自主決策，通過共享狀態（git repo）間接協調。像一群蜜蜂，沒有誰指揮誰，但整體湧現出秩序。優點是簡單、可擴展；缺點是缺乏全域視野，容易出現重複勞動。

**Hierarchical Teams 模式**是在 Swarm 基礎上加入適度的層級管理——有 team lead Agent 管理一組 worker Agent，team lead 之間再由更高層協調。這其實就是 Anthropic 後來正式發佈的 Agent Teams 產品的方向。Claude 的 Agent Teams 功能、Cursor 的 Background Agents、Codex 的多 Agent 模式，都在往這個方向走。

結論很明確：**沒有最好的架構，只有最適合的架構。** 任務可以清晰拆分、有明確驗證標準的，Swarm 就夠了。需要全域一致性的（比如設計一個 API），可能需要 Orchestrator。大型項目可能需要 Hierarchical。

但有一點是確定的：2026 年，我們正在從「一個 Agent 幹活」快速過渡到「一群 Agent 協作」。

---

## 5. 趨勢判斷 — 為什麼 2026 是多 Agent 元年

其實回頭看，多 Agent 協作的基礎設施在 2025 年底就開始成熟了。

協議層面，MCP（Model Context Protocol）讓 Agent 能連接外部工具和資料來源，Google 的 A2A（Agent-to-Agent）協議定義了 Agent 之間的通訊標準，還有 ACP 等新協議在湧現。這些協議解決的是「Agent 之間怎麼說話」的問題。

產品層面，Anthropic 的 Agent Teams 把 Carlini 的實驗產品化了，各家 IDE 都在推 multi-agent 功能，連 GitHub Copilot 都開始支援多 Agent 協作。

但更深層的變化是認知層面的。

過去一年，大家對 Agent 的理解經歷了一個轉變：從「一個超級 Agent 搞定一切」到「多個專業 Agent 各司其職」。這跟人類社會的分工邏輯是一樣的——沒有一個人能精通所有事情，但一個團隊可以。

Carlini 的實驗恰好證明了這一點。單個 Claude 寫不出能編譯 Linux 的編譯器，但 16 個 Claude 分工協作，加上精心設計的驗證環境，就可以。

**多 Agent 的能力上限 = 單 Agent 能力 × 協作架構質量 × 驗證環境質量**

這個公式裡，單 Agent 能力是模型廠商的事，我們能做的是後面兩項。

---

## 6. 給開發者 — 幾條實操建議

最後聊點實際的。如果你想在自己的項目裡嘗試多 Agent 協作，幾點建議。

先從小處開始，不需要一上來就搞 16 個 Agent。兩三個就夠了——一個寫程式碼，一個寫測試，一個做 review。先感受一下協作的節奏。

然後把精力投在測試基礎設施上。這是 Carlini 最大的教訓——你給 Agent 的測試質量，直接決定了產出質量。與其花時間寫更好的 prompt，不如花時間寫更好的測試。用最簡單的協調機制，Git 就是天然的多 Agent 協作平台，不要一開始就引入複雜框架。

還有就是為 LLM 的局限做設計。控制輸出量、提供摘要、維護進度文件、設定超時機制。這些看起來是小事，但決定了 Agent 能不能持續有效地工作。

最後，保持人在回路中。Carlini 自己也說了，完全自主開發有真實的風險。他以前做滲透測試的，對「程式設計師部署自己從未親自驗證過的軟體」這件事有本能的警覺。當前階段，人的角色是設計驗證環境、監控質量、在關鍵節點做決策。

回到最初的問題：這個實驗到底說明了什麼？**多 Agent 協作不是一個技術問題，而是一個工程管理問題。** 技術上讓多個 Agent 平行跑起來並不難，難的是設計一個環境，讓它們的工作成果能匯聚成一個有質量的整體。

這跟管理人類團隊，其實是一回事。

---

## 參考連結

- Building a C compiler with a team of parallel Claudes: [https://www.anthropic.com/engineering/building-c-compiler](https://link.zhihu.com/?target=https%3A//www.anthropic.com/engineering/building-c-compiler)
- GitHub - anthropics/claudes-c-compiler: [https://github.com/anthropics/claudes-c-compiler](https://link.zhihu.com/?target=https%3A//github.com/anthropics/claudes-c-compiler)
- Sixteen Claude AI agents working together created a new C compiler (Ars Technica): [https://arstechnica.com/ai/2026/02/sixteen-claude-ai-agents-working-together-created-a-new-c-compiler/](https://link.zhihu.com/?target=https%3A//arstechnica.com/ai/2026/02/sixteen-claude-ai-agents-working-together-created-a-new-c-compiler/)
- Claude Opus 4.6 spends 20K trying to write a C compiler (The Register): [https://www.theregister.com/2026/02/09/claude_opus_46_compiler/](https://link.zhihu.com/?target=https%3A//www.theregister.com/2026/02/09/claude_opus_46_compiler/)

如果你對 Agent 開發方法論感興趣，推薦看看我之前寫的這篇：[Agent Engineering，LangChain 最新總結的 Agent 開發方法論](https://zhuanlan.zhihu.com/p/1987525859482047326)

如果你對 AI 程式設計工具的演進感興趣，也可以看看這個系列：[程式碼編輯器進化論（上）——神之編輯器與編輯器之神](https://zhuanlan.zhihu.com/p/1991935850150372387)
