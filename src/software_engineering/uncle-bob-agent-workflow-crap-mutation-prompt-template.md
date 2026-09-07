# Uncle Bob 的 Agent 工作流操作層：CRAP、Mutation 與 Prompt Template

> 本文整理自 PaulFun Blogger（Paul）2026 年 9 月 3 日發布的文章，是對〈[《Clean Code》作者現在不看程式碼了，但他把規矩搬到了機器管得住的地方](clean-code-rules-for-ai-agents.md)〉一文的操作層延伸：把 Robert C. Martin（Uncle Bob）在概念層談到的做法，整理成三個可驗證的科學定義、一條五階段流水線，以及一份能直接套用的 Prompt Engineering Template。

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
- 原始訪談：Matt Pocock 直播訪談 Robert C. Martin（Uncle Bob），2026-08-19
- PaulFun Blogger 原文：<https://paulfun.net/articles/293>
