# Spec-Driven Development (SDD) 深度分析整理

## 什麼是 SDD？

Spec-Driven Development (SDD) 是在用 AI 寫程式之前，先讓 LLM 生成一系列規格文件的開發方法：

**流程**：產品需求 → 技術設計 → 任務清單 → 交給 coding agent 執行

**代表工具**：
- GitHub Spec-Kit
- AWS Kiro
- Tessl

---

## 社群意見兩極化

### 支持方觀點
- 遠比 vibe coding 可靠
- 適合要上線維護的真實專案
- 開發速度中期來看其實更快

### 反對方觀點
- 這就是 Waterfall 2.0
- 過度工程化
- 扼殺創造力

---

## 四篇深度分析文章

### 📄 第一篇：Spec-Driven Development: The Waterfall Strikes Back
**作者**：François Zaninotto

**核心論點**：SDD 試圖解決一個錯誤的問題——「如何把開發者從軟體開發中移除」

**實際使用痛點**：

1. **脈絡盲區**
   - SDD agent 跟 coding agent 一樣透過文字搜尋來理解脈絡
   - 常常漏掉需要更新的既有功能

2. **Markdown 地獄**
   - 產出太多文字
   - 開發者花大部分時間讀冗長的文件
   - 從看似專業的文字海中找出基本錯誤

3. **雙倍 Code Review**
   - 技術規格裡已經有程式碼
   - 要先審查規格再審查實作
   - 審查時間直接翻倍

4. **虛假的安全感**
   - Agent 不一定照規格走
   - 看到 agent 把「驗證實作」標記完成，卻只寫了手動測試說明而非單元測試

5. **邊際效益遞減**
   - 專案越大，規格越容易失準
   - 對大型既有程式碼庫幾乎無法使用

**建議做法**：用自然語言小步迭代，像 Lean Startup 那樣識別風險假設、設計最小實驗、快速驗證

---

### 📄 第二篇：Spec Driven Development - revenge of Waterfall or BDD taken to new level?
**作者**：Gojko Adzic（BDD 大師）

**核心觀察**：

1. **規格太高層次**
   - 產出的驗收條件用 Given-When-Then 格式
   - 需求用 must/should/could 分級
   - 但都太抽象，比較像工作範圍而非真正的規格

2. **文件是給工具用的**
   - 過程中產生大量文字
   - 大部分是讓工具追蹤自己進度用的，不是給人讀的
   - 最後都只是快速掃過或直接跳過

3. **缺少範圍定義階段**
   - 沒有明確的 scoping 步驟
   - 導致工具想做太多事然後失控
   - 產出大量測試和程式碼
   - Human in the loop 變得不可行

4. **所謂可執行規格其實是測試**
   - 真正的規格最後都變成單元測試和整合測試
   - 只有開發者看得懂

**結論**：有潛力值得關注，但目前離可執行規格的承諾還很遠，需要更明確的範圍定義階段來促進迭代交付

---

### 📄 第三篇：Understanding Spec-Driven-Development: Kiro, spec-kit, and Tessl
**作者**：Birgitta Böckeler (Thoughtworks)  
**發表於**：Martin Fowler 的 blog

**SDD 的三個層次**：

1. **Spec-first**：先寫好規格，用於當下的開發任務
2. **Spec-anchored**：任務完成後規格保留下來，持續用於功能的演進和維護
3. **Spec-as-source**：規格成為主要的原始檔，人類只編輯規格、不碰程式碼

**現實狀況**：理想上第 2 和第 3 層才是 SDD 的終極願景，但目前的工具大多只停在第 1 層

**實際觀察**：

1. **一套流程打天下？**
   - 用 Kiro 修一個小 bug
   - 結果被拆成 4 個 user story、16 條驗收條件
   - 完全是殺雞用牛刀

2. **寧願審查程式碼**
   - Spec-kit 產出大量重複冗長的 Markdown
   - 與其讀這些文件不如直接看程式碼

3. **虛假的控制感**
   - 即使有模板和檢查清單，agent 還是經常忽略指示或執行過頭
   - 例如：研究步驟收集了既有類別的資訊，結果 agent 當成新規格重新生成一遍，產生重複程式碼

4. **讓人想起 MDD**
   - Model-Driven Development 當年也想用規格生成程式碼，最後沒成功
   - LLM 解決了一些限制，但也帶來非確定性的新問題

**德文詞彙**：Verschlimmbesserung——在試圖改善的過程中反而把事情搞得更糟

---

### 📄 第四篇：Vibe Engineering
**作者**：Simon Willison（Python Django 共同發明者）

**核心理念**：不是隨便亂寫的 vibe coding，而是資深工程師運用 LLM 加速工作，同時對產出的軟體品質負責

**與 SDD 的對比**：

| 面向 | SDD | Vibe Engineering |
|------|-----|------------------|
| **文件份量** | 大量結構化 Markdown（requirements.md → design.md → tasks.md） | 輕量計畫，強調可以快速迭代 |
| **流程僵固度** | 固定的多階段流程 | 更強調靈活組合各種工程實踐 |
| **核心理念** | 想用規格文件來「控制」AI | 靠工程師的判斷力和既有的工程實踐來確保品質 |
| **責任歸屬** | 傾向讓流程和文件來保證品質 | 工程師要對產出的軟體「proudly and confidently accountable」 |

**LLM 會獎勵的頂級軟體工程實踐**：

1. **自動化測試**
   - 有完整測試套件的專案，coding agent 可以放心跑
   - 沒測試的話 agent 可能宣稱完成但根本沒驗證

2. **事前規劃**
   - 先有高層次計畫再交給 agent
   - 而且可以先迭代計畫本身

3. **完善文件**
   - 好的文件讓模型能直接使用 API 而不用先讀完所有程式碼

4. **良好的版本控制習慣**
   - LLM 很擅長 Git
   - 能自己翻歷史追 bug，善用 git bisect

5. **有效的自動化流程**
   - CI/CD、自動格式化、linting
   - Agent 也能受益

6. **Code Review 文化**
   - 擅長審查程式碼的人，跟 LLM 協作會順暢很多

7. **手動 QA 能力**
   - 除了自動測試，還要能預測和挖掘邊緣案例

**核心洞察**：AI 工具會放大既有的專業能力，軟體工程技能越強，從 LLM 得到的結果就越好越快

---

## 其他專家意見

### 宝玉（AI 大 V）
> 我個人是不喜歡用 spec-kit，不是好的上下文工程：
> - 小項目沒必要
> - 大項目描述不清楚
> - 一大坨文檔反而占用上下文影響生成
> - 文檔不保持及時更新反而會誤導 Agent

### swyx（AI Engineer Summit 大會主辦人）
> Spec Driven Development is Wishful Thinking
> 
> 「SDD 只是一廂情願」

---

## SDD 小結

### 終極願景
人類只維護規格、AI 負責生成程式碼，規格成為長期維護的 source of truth

### 殘酷現實
- 目前這些工具都只停在 **Spec-first** 的層次
- 規格寫完用完就丟，跟傳統的需求文件沒什麼兩樣
- 只是多了一堆 Markdown 要讀

### 核心問題
SDD 的初衷是想讓 AI 更受控，但目前實際上是：

**用更多文件換來更多負擔，卻沒有換到相應的品質保證**

---

## 總結：正確的方向

與其想要全靠文件控制 AI，不如：

1. **強化既有的工程實踐**
   - 測試
   - 版本控制
   - Code review

2. **讓 AI 放大開發者的專業能力**
   - 而不是試圖取代開發者

3. **保持靈活性和快速迭代**
   - 而不是陷入僵化的文件流程

**關鍵認知**：軟體工程技能越強，從 LLM 得到的結果就越好越快

---

## 參考資料

1. [Spec-Driven Development: The Waterfall Strikes Back](文章連結)
2. [Spec Driven Development - revenge of Waterfall or BDD taken to new level?](文章連結)
3. [Understanding Spec-Driven-Development: Kiro, spec-kit, and Tessl](文章連結) - Martin Fowler's blog
4. 宝玉的評論
5. swyx 的 tweet

---

*整理日期：2025年12月*