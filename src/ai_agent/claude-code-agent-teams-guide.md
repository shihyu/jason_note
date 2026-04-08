# 派三個 AI 同時做事，為什麼反而更慢？

**TL;DR**
掌握 Agent Teams 的三個關鍵：什麼時候不該用（線性流程）、怎麼開啟與關閉，以及遇到不確定時直接問 Claude。用對地方可以並行提速，用錯地方反而加重複雜度。

**這篇文章適合：**

- 已用過 Claude Code 基礎功能，想進一步提升效率的 PM 或設計師
- 不確定自己的任務適不適合用 Teams，每次都要猜的人
- 想了解 Teams 完整操作流程（從建立到關閉）的人

---

假設你是做 SaaS 產品的 PM。某天你盯著 Notion 上的 sprint 清單發呆：使用者訪談稿要整理、功能需求文件要更新、下一版的優先排序還沒做。

你一直都是一件件丟給 Claude Code 做，一項做完換下一項。這天你突然想到：「有沒有辦法讓多個 Claude 同時幫我處理這些？」

你查到了 Agent Teams 這個功能，興奮地建了 Team，派了三個 AI 同時出發。

結果花了更多時間重工。

**Agent Teams 不是加速鍵，是路線的改變。** 用之前，你必須先搞清楚一件事。

---

## 1. Agent Teams 是什麼？

**Agent Teams 是 Claude Code 的多 Agent 協作功能，讓你同時召喚多個 AI 並行工作、互相協調。**

想像你在帶一個三人小組。你是組長，負責分配工作、整合成果；其他三個人各自做自己的部分，做完回來跟你報告。Agent Teams 的概念完全一樣——只不過這些「隊員」不是真人，**而是同時運作的多個 Claude AI**。你是 Team Lead，它們是 Teammates，各自獨立工作，完成後自動通知你。

這些 Teammates 全部透過以下工具控制，直接在 Claude Code 的對話框輸入，不需要額外安裝任何東西：

| 工具 | 用途 |
| --- | --- |
| `TeamCreate` | 建立一個 Team（同時初始化共享 Task List） |
| `Task`（帶 `team_name`） | 召喚一個 Teammate AI 加入 Team |
| `TaskCreate / TaskUpdate / TaskList` | 管理共享的任務清單 |
| `SendMessage` | 你與 Teammates 之間的溝通 |
| `TeamDelete` | 解散 Team、清理資源 |

溝通是**自動投遞**的——Teammates 完成任務後，訊息會直接出現在你的對話中，你不需要主動去查看。

> 「你負責決策，AI Teammates 負責執行——各司其職，互不等待。」

---

## 2. 最重要的事：什麼時候不適合用 Teams

**線性流程、小任務，需要逐步審查的工作——這三種情境不適合用 Agent Teams。**

這也是你可能踩到的坑。你的三件事是：訪談稿整理 → 需求文件更新 → 功能優先排序。三個 Agents 一起出發後，第二個 Agent 拿到的訪談稿還沒整理好，寫出了一堆無法對照真實用戶需求的文件；第三個 Agent 排序時用的是上一版功能列表，因為新文件還沒出來。

問題出在哪裡？你的任務是**線性的**——訪談稿整理完才能更新文件，文件更新完才能做排序。這不是三條平行的線，而是一條環環相扣的鏈。

### 2-1. 線性流程（最常見的誤用）

```
整理訪談稿
  → 需要訪談稿的輸出
更新需求文件
  → 需要文件的輸出
功能優先排序
```

同時派多個 Agent 去做，它們只會互相等待，或用錯誤的前提開始工作。一個 Claude 按順序做完，反而更快更穩。

套用到廚房就一目瞭然：切菜要等食材準備好，炒菜要等切完，裝盤要等炒完。這條流水線有嚴格的先後順序，同時派三個廚師站在不同位置等待，比一個廚師連貫做完還要慢。

**差別不是人數多不多，而是任務能不能真的同時進行。**

### 2-2. 任務太小，太短

建立 Team、召喚 Teammates、分配任務、等待結果、整合、關閉——這些 overhead 加起來需要幾個額外的 API 來回。如果你的任務本身只要幾分鐘，Teams 的成本比任務本身還高。

這些任務直接叫一個 Claude 做就好：

- 改一個措辭
- 修一個錯誤
- 補一段說明文字
- 整理一份短文件

### 2-3. 每一步都需要你審查決策

如果每個小步驟你都要介入、判斷，再給下一步指示，Teams 的並行優勢就消失了。Teams 最適合「交代清楚方向後，讓 Agents 自主完成」的任務。

---

## 3. 什麼時候適合用 Teams

**任務互不依賴，工作量夠大，能清楚整合結果——符合這三個條件就適合。**

假設你是 UI 設計師，接了一個 side project：做一個活動報名 landing page。設計稿定稿後，你需要同步搞定兩件事：**文案撰寫**和 **HTML/CSS 切版**。

這兩件事互不干擾——文案不需要等 HTML 切好才能寫，HTML 也不需要等文案確定才能動。你事先定好頁面區塊，然後各自開工。

```
Agent A → 寫文案
Agent B → 寫 HTML/CSS
你 → 整合
```

一個 Agent 負責文案，一個負責切版，你只需要在最後整合。原本需要兩個小時的工作，並行之後省下了一半。

**差別在哪裡？任務真的獨立，才能真的並行。**

### 3-1. 真正可並行的獨立任務

工作拆成兩份以上、彼此不依賴彼此的輸出，就適合 Teams。前後端同步開發、文案和設計同步進行、多份獨立研究報告——都是這個模式。

### 3-2. 大範圍掃描與研究

同時探索多個市場資料、搜尋多個競品分析、整理多份用戶訪談摘要——這些任務互不干擾，完全可以並行，比序列執行快上好幾倍。

### 3-3. 大規模重構（多個獨立模組）

把多個互不依賴的模組交給不同 Agent 同時處理，安全並行，最後整合。

---

## 4. 不確定要不要用？直接問 Claude

判斷原則是參考用的，但真實情況往往更複雜。當你拿到一個任務不確定時，最直接的方式是把任務描述給 Claude，然後問他：

> 「你覺得我們這個案例，需不需要用 team agent？」

假設你是產品設計師，剛接到一個需求：幫用戶建立一套週報範本系統。你直覺覺得這個任務「感覺有點大」，但說不清楚到底要不要開 Teams。

你把需求描述給 Claude，問了上面那句話。Claude 分析後回答：「這個任務的核心是先設計範本結構，再根據結構產出內容——是序列的，不適合 Teams。一個 Claude 按順序做就夠了。」

你省去了建立 Team 的麻煩，直接開始工作。

Claude 知道 Teams 的成本與收益，會根據你的具體情況給建議。如果不適合，他會直接說不用；如果適合，他也能順帶幫你規劃怎麼拆分任務。

---

## 5. 實戰：完整操作流程

以前面的「文案 + 切版並行開發」為例，走完完整的 Teams 生命週期。

### 5-1. Step 1：建立 Team

```
TeamCreate
  team_name: "landing-page"
  description: "活動報名頁文案 + HTML 切版（並行開發）"
```

### 5-2. Step 2：建立任務清單

```
TaskCreate
  title: "撰寫活動報名頁文案"
  description: "包含 Hero、Feature、CTA 三個區塊，語氣輕鬆、行動導向"

TaskCreate
  title: "HTML/CSS 切版"
  description: "依據設計稿切出三個區塊，RWD，暗色主題"
```

### 5-3. Step 3：召喚 Teammates

```
Task（subagent_type: general-purpose）
  team_name: "landing-page"
  name: "copywriter"
  prompt: "你負責活動頁文案。看 TaskList 找到你的任務，
           完成後用 TaskUpdate 標記 completed，
           再用 SendMessage 通知 team-lead。"

Task（subagent_type: general-purpose）
  team_name: "landing-page"
  name: "frontend-dev"
  prompt: "你負責 HTML/CSS 切版。看 TaskList 找到你的任務，
           頁面區塊設計參考 TaskList 說明，
           完成後通知 team-lead。"
```

兩個 Agents 同時開始工作，不需要等一個完成才召喚另一個。

### 5-4. Step 4：協調進行中的工作

Teammates 工作時會進入 **idle 狀態**。

**idle 不等於出錯**：idle 表示 Agent 在等你的下一步指示，或等其他 Agent 的輸出。這是完全正常的等待狀態。

當他們完成任務，訊息會自動出現在你的對話：

```
[copywriter] → team-lead
Hero 文案：「讓你的活動，被更多人看見」
Feature 區塊三點完成、CTA 完成。
```

如果 frontend-dev 需要文案才能繼續，你可以直接轉發：

```
SendMessage
  type: "message"
  recipient: "frontend-dev"
  content: "文案已確認，Hero 標題：「讓你的活動，被更多人看見」
            三個 Feature 區塊文案已完成，可以開始填入了。"
```

### 5-5. Step 5：關閉 Team

所有任務完成後，**先關閉 Teammates，再刪除 Team**。

> **注意順序**：必須先讓所有 Teammates 回應 shutdown，才能執行 TeamDelete。若順序顛倒，TeamDelete 會失敗。如果沒有收到回應，重新發送一次 shutdown_request 即可。

```
# 1. 向每個 Teammate 送出關閉請求
SendMessage
  type: "shutdown_request"
  recipient: "copywriter"

SendMessage
  type: "shutdown_request"
  recipient: "frontend-dev"

# 2. 等 Teammates 各自回應 approve: true

# 3. 刪除 Team
TeamDelete
```

---

## 6. 快速判斷表

| 問題 | YES | NO |
| --- | --- | --- |
| 任務可以拆成 2 個以上互不依賴的部分嗎？ | 繼續看 | 用單一 Claude |
| 每個部分的工作量夠大嗎（幾分鐘以上）？ | 繼續看 | overhead 不划算 |
| 各部分完成後，你能清楚整合結果嗎？ | 適合用 Teams | 先釐清整合方式 |

三個 YES 才值得建 Team。拿不準的話，直接問 Claude。

> **試試看**：把你手上一個任務描述給 Claude，問他「你覺得這個案例需不需要用 team agent？」答案可能比你預期的更精準。

---

## 7. 總結

回到開頭的場景。後來你搞清楚了——那三件事（訪談稿 → 文件 → 排序）是線性的，一個個做才是對的。但下個月你有另一個任務：同時做三份完全獨立的市場研究分析。這次你建了 Team，三個 Agents 並行處理，省了大半時間。

> **Teams 是為了並行而生的。如果你的任務本質上是序列的，加再多 AI 也只是讓複雜度上升，不會讓速度提升。**

**用對地方**：大範圍研究、多模組重構、互不依賴的任務同步開發。
**用錯地方**：線性流程、小修改、每步都需要你審查。

_本文基於 Claude Code Agent SDK（2026）規格撰寫。_
