# 別再打造 Agent 了，打造 Skills 吧 — Anthropic 演講重點整理

看了一場 Anthropic 的演講 [Don’t Build Agents, Build Skills Instead](https://www.youtube.com/watch?v=CEvIs9y1uog)，由 Barry Zhang 和 Mahesh Murag 兩位 Anthropic 工程師主講。這是我將影片轉成逐字稿的全文： [ihower.tw/watch/dont_build_agents_build_skills_instead](https://ihower.tw/watch/dont_build_agents_build_skills_instead_barry_zhang_mahesh_murag_anthropic/)

以下是重點整理：

## 1. 以前怎麼看 Agent: 每個領域一個 Agent

過去大家以為不同領域的 Agent 會長得很不一樣 — Coding Agent、Research Agent、Finance Agent、Marketing Agent，各自需要各自的工具和鷹架(scaffolding)。

![](images/dont-build-agents-build-skills/frame_17.jpg)

## 2. 程式碼是通用介面: Code is All You Need

但做了 Claude Code 之後，他們發現 Agent 的底層架構比想像中更通用。程式碼就是 Agent 與數位世界互動的通用介面。

![](images/dont-build-agents-build-skills/frame_20.jpg)

一個 Coding Agent 透過程式碼就能處理各種任務: 呼叫 API 拉資料、用檔案系統組織資料、用 Python 分析、再輸出成任何格式。核心的鷹架程式碼可以薄到只剩 bash 和檔案系統。

## 3. 但問題來了: Agent 缺乏領域專業知識

Agent 很聰明，但缺乏專業知識。演講者用了一個有趣的比喻: 你要報稅，會選一個 IQ 300 的數學天才，還是一個經驗豐富的稅務專家？

![](images/dont-build-agents-build-skills/frame_28.jpg)

答案很明顯 — 你要的是領域專家的一致性執行，不是讓天才從第一原理推導稅法。今天的 Agent 就像那個天才: 很厲害，但缺乏前置的專業脈絡，也不會隨時間學習。這就是為什麼他們做了 Agent Skills。

![](images/dont-build-agents-build-skills/frame_36.jpg)

## 4. Skills 就是資料夾

Skills 的定義很簡單: 「組織好的檔案集合，打包了可組合的程序性知識(procedural knowledge)。」

![](images/dont-build-agents-build-skills/frame_37.jpg)

白話講，就是資料夾。這個簡單設計是刻意的 — 任何人只要有電腦就能建立和使用。可以用 Git 版控、丟 Google Drive、壓成 zip 分享給團隊。

![](images/dont-build-agents-build-skills/frame_38.jpg)

## 5. Scripts as Tools: 比傳統 Tools 更好

Skills 裡面可以包含腳本(scripts)作為工具。傳統的 function calling tools 有幾個問題: 說明可能寫得很爛又模糊，模型卡住時也改不了工具本身。

![](images/dont-build-agents-build-skills/frame_45.jpg)

而腳本作為工具有天然優勢: 程式碼本身就是文件(self-documenting)、可以被修改、而且平時放在檔案系統不佔 context window，需要時才載入。

例如他們發現 Claude 一直重複寫同樣的 Python 腳本來套用投影片樣式，就讓 Claude 把腳本存進 Skill 裡，下次直接跑就好，更一致也更有效率。

## 6. 漸進式載入: Progressive Disclosure

Skills 的設計是漸進式披露的。在 runtime 時，模型一開始只看到最精簡的 metadata (name + description) 來知道「我有這個技能」:

![](images/dont-build-agents-build-skills/frame_55.jpg)

當 Agent 真的需要用某個 Skill 時，才讀入完整的 SKILL.md:

![](images/dont-build-agents-build-skills/frame_57.jpg)

SKILL.md 裡面再指向更細節的檔案，例如 slide-decks.md 和 docs.md:

![](images/dont-build-agents-build-skills/frame_58.jpg)

這讓你可以裝載上百甚至上千個 Skills 而不會撐爆 context window，達到真正的可組合性。

## 7. Skills 生態系

推出五週就形成了快速成長的生態系，分成三類:

![](images/dont-build-agents-build-skills/frame_60.jpg)

**基礎 Skills**: 給 Agent 新的通用或領域能力，例如 Anthropic 自己做的 Document Skills 讓 Claude 能建立和編輯專業的 Office 文件，還有 Cadence 做的科學研究 Skills。

![](images/dont-build-agents-build-skills/frame_65.jpg)

**第三方夥伴 Skills**: 例如 Browserbase 做了瀏覽器自動化的 Skill (Stagehand)、Notion 做了深度研究 workspace 的 Skill。

![](images/dont-build-agents-build-skills/frame_72.jpg)

**企業內部 Skills**: Fortune 100 公司用 Skills 來教 Agent 組織內部的最佳實踐和內部軟體的使用方式，大型開發團隊用來部署程式碼風格規範給上千名工程師。

![](images/dont-build-agents-build-skills/frame_79.jpg)

## 8. 生態系趨勢

他們觀察到三個趨勢:

![](images/dont-build-agents-build-skills/frame_105.jpg)

1.  **Skills 越來越複雜**: 從簡單的 markdown 指引，到包含軟體、執行檔、資源檔，未來可能需要數週甚至數月來建構和維護
2.  **Skills 和 MCP 互補**: MCP 提供與外部世界的連接，Skills 提供專業知識。開發者用 Skills 來串接多個 MCP 工具的工作流
3.  **非技術人員也在建 Skills**: 財務、招募、法務等，驗證了 Skills 讓非工程師也能擴展 Agent 能力

## 9. 完整架構: Agent + MCP + Skills

![](images/dont-build-agents-build-skills/frame_117.jpg)

通用 Agent 架構正在收斂: 一個 Agent 迴圈(模型 + 程式碼工具)管理 context，左邊接 MCP servers 連接外部資料和工具，右邊接檔案系統裡的 Skills 庫讓 Agent 在 runtime 按需載入。

![](images/dont-build-agents-build-skills/frame_118.jpg)

Anthropic 推出 Skills 五週後，就用這個模式發佈了金融服務和生命科學的垂直方案 — 每個都是一組 MCP servers + 一組 Skills，直接讓 Claude 對該領域的專業人士更有用。

![](images/dont-build-agents-build-skills/frame_123.jpg)

## 10. 未來方向: 測試、版控、組合

隨著 Skills 越來越複雜，他們想把 Skills 當軟體來對待:

![](images/dont-build-agents-build-skills/frame_128.jpg)

-   **評估(Evaluation)**: 測試 Agent 是否在正確時機載入正確的 Skill，輸出品質是否達標
-   **版控(Versioning)**: 追蹤 Skill 的演進和 Agent 行為的變化
-   **可組合性(Composability)**: Skills 之間可以互相依賴，也能依賴 MCP servers 和其他 packages

## 11. 集體知識庫的願景

![](images/dont-build-agents-build-skills/frame_145.jpg)

他們最興奮的願景是: Skills 形成一個由人和 Agent 共同策展的、持續演進的集體知識庫。當你跟 Agent 互動給回饋，它變好了，你團隊裡所有人的 Agent 也跟著變好。新人加入團隊，Claude 已經知道團隊的脈絡和工作方式。

就像別人在社群建了一個 MCP server 讓你的 Agent 更有用，別人建的 Skill 也能讓你的 Agent 更強。

## 12. 邁向持續學習

![](images/dont-build-agents-build-skills/frame_173.jpg)

Skills 是邁向持續學習(continuous learning)的具體一步。這個標準化格式保證了: Agent 寫下的任何東西，未來的自己都能有效使用。

目標是第 30 天的 Claude 比第 1 天好很多 — 從「聰明但什麼都不會」到「擁有大量 Skills 的實用專家」。

## 13. 類比計算史: Models → Agents → Skills

最後他們用一個漂亮的類比收尾:

![](images/dont-build-agents-build-skills/frame_184.jpg)

-   **Models = 處理器(Processors)**: 需要大量投資、潛力巨大但單獨沒那麼有用
-   **Agents = 作業系統(OS)**: 負責編排資源讓處理器發揮價值
-   **Skills = 應用程式(Applications)**: 少數公司做處理器和 OS，但百萬開發者建構了編碼領域專業知識的軟體

Skills 就是要開放這一層讓所有人參與 — 把東西放進資料夾，就能解決具體問題。

![](images/dont-build-agents-build-skills/frame_190.jpg)

---

蠻精煉的一場演講。對我來說最大的啟發是: 與其花時間在 Agent 架構上，不如把領域知識好好整理成 Skills，這才是真正能累積和複利的東西。所以別再從零打造 Agent 了 — 把精力花在打造 Skills 上吧。
