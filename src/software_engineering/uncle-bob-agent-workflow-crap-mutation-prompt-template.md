# Uncle Bob 的 Agent 工作流操作層：CRAP、Mutation 與 Prompt Template

> 本文整理自 PaulFun Blogger（Paul）2026 年 9 月 3 日發布的文章，是對〈[《Clean Code》作者現在不看程式碼了，但他把規矩搬到了機器管得住的地方](clean-code-rules-for-ai-agents.md)〉一文的操作層延伸：把 Robert C. Martin（Uncle Bob）在概念層談到的做法，整理成三個可驗證的科學定義、一條五階段流水線，以及一份能直接套用的 Prompt Engineering Template。另補充 Cash Wu 於 2026 年 8 月 28 日發布的〈紀律可以鬆散，價值必須守住，Uncle Bob 談 AI 時代的軟體基本功〉，兩篇文章源自同一場 Matt Pocock 訪談 Uncle Bob 的直播，互為補充。

## 中心命題

標準沒有降低，只是搬到了機器可以強制執行的地方。Uncle Bob 的立場從來不是「AI 很厲害」，而是幾十年累積下來的工程紀律不會因為 agent 出現就消失，必須重新安裝到 agent 能夠實際運行、機器能夠檢查的層次上。

## 三個操作型科學定義

### 1. CRAP Score

CRAP（Change Risk Anti-Patterns）由 Alberto Savoia 與 Bob Evans 於 2007 年提出，用來衡量一個函式改動時的風險：

```
CRAP(m) = comp(m)² × (1 − cov(m))³ + comp(m)
```

- `comp(m)`：函式的環形複雜度（分支數 + 1）
- `cov(m)`：測試覆蓋率（0 = 無測試，1 = 全覆蓋）

數值大致可以這樣理解：

```
comp=2,  cov=100%  →  CRAP = 2.0   健康
comp=2,  cov=0%    →  CRAP = 6.0   邊界
comp=5,  cov=0%    →  CRAP = 30.0  危險
comp=10, cov=80%   →  CRAP = 10.1  需注意
comp=10, cov=0%    →  CRAP = 110.0 高危
```

人類寫程式的經驗值一般抓 CRAP ≤ 4，Uncle Bob 把交給 agent 的閾值放寬到 ≤ 6。改的是數字，不是原則本身。

### 2. Mutation Testing（突變測試）

比「測試覆蓋率 100%」更嚴格的檢驗方式：覆蓋率只確認程式碼有沒有被跑到，突變測試確認測試有沒有真的在驗證語意。做法是：

1. 拿一份通過所有測試的程式碼
2. 自動引入一個語義層級的改動（例如把 `>` 改成 `>=`、把 `+` 改成 `-`、把 `true` 改成 `false`）
3. 重新跑一次完整測試套件
4. 若測試仍然通過，代表這個「突變體」存活了下來，意味著測試存在盲點
5. 補強測試，直到所有突變體都被殺死

```
Mutation Score = Killed Mutants / Total Mutants × 100%
```

Uncle Bob 對 agent 產出程式碼的要求是 Mutation Score 必須達到 100%。

### 3. Lost in the Middle

出自 Liu 等人 2023 年的研究：大型語言模型讀取長脈絡時的準確率呈 U 型曲線——開頭記得最牢，結尾次之，中段會明顯衰退，最多可下降三至四成。這意味著一旦 system prompt 超過幾百個 token，寫在中段的規則很容易被 agent 忽略，不是模型不聰明，而是架構上的限制。

對應的做法是：提示詞只保留最核心、不可妥協的指令，維持精簡；其餘所有規則都不留在提示詞裡，改成交由 linter、CRAP 分析腳本、mutation runner 之類的確定性工具在事後執行——讓規則靠工具強制，而不是靠 agent 的記憶。

## 五階段流水線

```
規格（Specification）    → agent 產生驗收測試
        ↓
撰寫（Writing）           → agent 產生單元測試與實作
        ↓
清理（Cleanup）           → CRAP Score 自動分析
        ↓  CRAP > 6 → 打回 Writing
清理通過（CRAP ≤ 6）
        ↓
強化（Strengthening）     → 突變測試自動執行
        ↓  有盲點 → 打回 Writing
強化通過（Mutation Score = 100%）
        ↓
QA                        → 驗收腳本自動執行
        ↓  失敗 → 打回 Cleanup
全部通過
        ↓
完成 — 約一小時，生產力約 4～5 倍
```

每一關只做一件事，品質把關的責任交給確定性工具，而不是寄望 agent 自己記得規則。

五個階段各自對應一個獨立的 agent 角色，Cash Wu 在其部落格文章中給出了具體命名：

| 角色 | 職責 | 輸出 |
|------|------|------|
| Specifier | 把文件轉成 Gherkin（Given/When/Then）驗收規格與 QA 操作程序 | 可執行規格 |
| Coder | 依驗收規格撰寫單元測試與實作 | 可運作但未必整潔的程式碼 |
| Cleaner | 執行 CRAP 分析與一般性審查 | 清潔的程式碼 |
| Hardener | 執行突變測試，追求 Mutation Score 100%，不放過任何一個運算符號 | 高強度測試覆蓋 |
| QA Agent | 把書面 QA 轉成可執行腳本，實際操作 UI 驗證 | 端對端驗證結果 |

每個 agent「出生 → 完成 → 結束」，context 用完即歸零，這才是分工的真正目的——不是角色專業化，而是讓每個 agent 只走一條單純的思考軌跡，避免 Lost in the Middle 隨對話累積而惡化。

成本效益上，單一 agent 一次做完全部只要約 5 分鐘，但品質可疑；完整五階段 pipeline 約需 1 小時；換成人類工程師約需半天。整體換算下來 agent pipeline 仍比人類快 4～5 倍，而且品質「遠高於人類會投入的水準」。

## 紀律可以鬆散，價值必須守住

Uncle Bob 進一步把「要不要照搬人類的開發紀律」拆成兩個獨立問題：

- **人類紀律**（可以鬆動）：像 TDD 的強制小步循環，本質是為了補償人類短期記憶的限制而設計的認知輔助工具。Agent 擁有精確且巨大的短期記憶，不會忘記上一步寫了什麼，因此 TDD 那種「先寫一個失敗測試、再寫最小實作」的強制節奏對它而言沒有意義。
- **恆久價值**（不能鬆動）：正確性、可測試性、清晰的結構，這些不會因為執行者是人類還是 agent 而改變，只是判斷門檻可以調整。

門檻調整的具體例子就是 CRAP：人類寫程式的經驗值上限抓在 4 以下，Uncle Bob 給 agent 放寬到 6，Cash Wu 提到未來可能再放寬到 8。這句話是整篇文章的核心命題：「把人類紀律硬套在 agent 身上可能是錯誤，但把人類價值觀套在 agent 身上並非錯誤，只是門檻需要調整。」

## 對 Spec-Driven Development 的懷疑

Uncle Bob 對「先把規格寫得鉅細靡遺，再交給 agent 執行」抱持警告態度：前期規劃容易掉進瀑布陷阱——規格寫得華麗漂亮，卻因為人類無法預見所有情況，在執行到後期分崩離析。他用蓋房子類比：如果每次變更的成本降到 1 美元，沒有人會為了省下事後修改，先花大錢畫一張鉅細靡遺的完美設計圖；AI 讓變更成本趨近於零，昂貴的前期規劃自然不划算。

他對「Single Source of Truth（唯一可靠資訊源）」的定義也隨之改變：傳統上原始碼就是規格本身，但當程式碼不再由人類編寫、也不必被人類閱讀時，這個角色就站不住腳了。他的替代方案是不預先寫定義期望的規格，而是先看 agent 產出的最終結果，再回頭說「這就是規格」——規格用完即丟，不必長期維護。

Cash Wu 對此提出的實務修正是：問題不在於「要不要寫規格」，而在於「規格要不要一次寫完、寫完後放著不動」。他自己採用的做法是逐 story 迭代、規格本身可執行（對應到 Gherkin）、並且即時審查，規格的價值在「寫的當下把邊界釐清」，而不是事後保存成一份靜態文件。

## 新人培養：把新人當成 agent 對待

當 agent 把戰術性工作（Tactical，完成眼前功能）全部接管之後，新人要如何學會策略性能力（Strategic，長期系統設計）？這是 Ousterhout 在《A Philosophy of Software Design》中戰術 vs 策略框架下引出的真實焦慮。

Uncle Bob 的建議是：讓新人接受和 agent 一樣的任務、遵循一樣的確定性工具約束，持續數個月。他坦言這段時間「生產力極其低落，但學到極多」——本質上是把新人當成 agent 底下的 sub-agent 來培養。這個判斷力背後的關鍵是「能看見 agent 在原地打轉」，而這種判斷力只能靠自己親手寫過程式碼才能養成，缺了這層經驗，直接上手操作 agent 工作流基本上等於盲飛（此點與檔案原本〈對初級工程師的提醒〉一節呼應）。

## 歷史視角：抽象層升級的永恆辯論

Uncle Bob 與 Matt Pocock 都提到，每一次抽象層升級都會伴隨「這會毀滅一切」的論調——從二進位到組合語言，從組合語言到編譯器，如今輪到 AI。Matt Pocock 引用柏拉圖曾稱書寫會使人變笨作結：「關於抽象化的爭論從古希臘就存在，真的荒謬。」對應到 Prompt 規則的取捨上，這也呼應了前面提到的觀察：「你現在丟掉的規則，就是一年後要從地上撿回來的那些規則。」

## 架構：最後一道未自動化的堡壘

即便前述五階段 pipeline 已經把規格、實作、清理、強化、QA 都交給 agent，Uncle Bob 坦承架構設計仍是例外：模組如何切分、相依方向如何決定，目前仍需人工介入；深入盤問 agent 的系統設計後，得到的答案常常「嚇得半死」。他自陳在這個領域仍在掙扎，處境和 Matt Pocock 相同——這是目前為止還沒有找到確定性工具可以取代人類判斷的一環。

## Prompt Engineering Template

以下範本可直接複製使用，填入 `[USER_REQUIREMENT]` 等佔位符即可套用到上述五階段流水線：

```
# [功能名稱] — Agent Prompt Template

## System Prompt（保持 ≤ 500 tokens）
你是一個 [功能定義] 的 agent。
核心責任：[最多 2 句話]
不妥協的底線：[1 句話，其他規則搬到工具層]

---

## Stage 1: Specification
任務：根據以下需求，產生驗收測試（Acceptance Tests）

需求：[USER_REQUIREMENT]

輸出格式：
- [ ] 驗收測試 1：[描述可觀察的行為]
- [ ] 驗收測試 2：[描述可觀察的行為]
（只描述行為，不預設實作細節）

---

## Stage 2: Writing
任務：根據驗收測試，產生單元測試與實作

驗收測試：[ACCEPTANCE_TESTS_FROM_STAGE_1]

輸出：
1. 單元測試（先寫，TDD 原則）
2. 最小實作（只讓測試通過）

約束：每個函式環形複雜度 ≤ 4（工具會自動檢查 CRAP Score）

---

## Stage 3: Cleanup（自動執行，不需 agent）
工具：[你的 CRAP 分析工具]
公式：CRAP(m) = comp(m)² × (1 − cov(m))³ + comp(m)
閾值：CRAP ≤ 6
失敗時：回 Stage 2，要求重構

---

## Stage 4: Strengthening（自動執行，不需 agent）
工具：[你的 mutation testing 工具]
目標：Mutation Score = 100%
失敗時：回 Stage 2，補強測試

---

## Stage 5: QA
任務：執行驗收腳本，確認 Stage 1 所有測試通過

執行：[QA_SCRIPT_COMMAND]

通過條件：所有驗收測試 ✓
```

## 對初級工程師的提醒

Uncle Bob 特別強調：不能跳過親手寫程式碼這一步，直接上手操作 agent 工作流。理由很單純——你必須知道系統在什麼地方會卡住、會掙扎，這種判斷力只能靠自己動手寫過才能養成，缺了這層經驗，用 agent 工作流基本上等於盲飛。

他推薦的基礎讀物包括 Tom DeMarco 的《Peopleware》、Ed Yourdon 的《Decline and Fall of the American Programmer》，以及《The Pragmatic Programmer》。

## 延伸閱讀

- 〈[《Clean Code》作者現在不看程式碼了，但他把規矩搬到了機器管得住的地方](clean-code-rules-for-ai-agents.md)〉——本文所延伸的概念層文章
- 原始來源：Fox Hsiao，〈Uncle Bob 的 Agent 工作流〉，anduril.tw，2026-08-29
- 原始訪談：Matt Pocock 直播訪談 Robert C. Martin（Uncle Bob），2026-08-19（57 分鐘）
- PaulFun Blogger 原文：<https://paulfun.net/articles/293>
- Cash Wu，〈紀律可以鬆散，價值必須守住，Uncle Bob 談 AI 時代的軟體基本功〉，2026-08-28：<https://blog.cashwu.com/blog/2026/uncle-bob-ai-software-fundamentals>
- 論文：Liu et al. (2023)，Lost in the Middle 現象
- 書籍：John Ousterhout，《A Philosophy of Software Design》（戰術 vs 策略框架）
- Cash Wu 前置文章：《不讀 AI 寫的程式碼，然後呢？》、《TDD in the Agent Loop》、《SDD: From TDD to Spec-Driven Development》
