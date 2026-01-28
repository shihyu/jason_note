# 我的 AI 是怎麼記錄我的寫文習慣的？

> 原文來自：https://www.threads.com/@881freelancer/post/DSTsi4WEv_h

這篇文章，其實是透過我寫好的資料庫進行二次學習處理過後，搭配觀點寫出來的。

以下是 AI Agent 的工作總結記錄，就不修改排版了，直接出。

---

## What could be codified into an agent?

我們剛剛完成了一次完美的「人機協作演化」Demo。這不只是一次寫作，而是一次**系統升級**。

以下是我們剛剛做的事情，以及它們如何被轉化為 Agent（代理人）的邏輯：

---

### 1. The "Style Gardener" Agent（風格園丁）

這是本場最有價值的發現。

**我們做了什麼（Manually）：**

1. 你對草稿提出具體批評（「免啦」改成「母湯啦」、「神級指令」改成「網友分享的無敵指令」）
2. 我手動去修改 `style_memory.py` 程式碼，因為發現少了一個功能
3. 我手動執行指令 `plant`，把這些「修正」存入向量資料庫

**Can be Codified（自動化邏輯）：**

#### "The Critique Listener"

- **Trigger**: 當你對文章進行修改（Diff）或在對話中說「不要用 X，要用 Y」時
- **Action**: Agent 自動分析修改前後的差異，提取出 `Bad` vs `Good` 的模式
- **Storage**: 自動呼叫 `plant` API，將這條規則存入 Memory
- **Result**: 下次寫作時，Agent 會自動檢索並避開這個地雷，不需要你再講一次

---

### 2. The "Context Stitcher" Agent（觀點縫合怪）

**我們做了什麼（Manually）：**

1. 給定一個外部連結/文章（Elena Vera）
2. 給定你的碎碎念觀點（我的觀點...）
3. 要求：用你的風格，把 B（觀點）縫合進 A（文章結構）裡

**Can be Codified（自動化邏輯）：**

#### "The Viewpoint Injector"

- **Input**: `Reference URL` + `Raw Thoughts` + `Style Profile`
- **Process**:
  1. 分析 `Reference` 的核心論點（Hook/Problem/Solution）
  2. 找到 `Raw Thoughts` 中的「金句」或「反直覺觀點」
  3. **Mapping**: 決定要把哪個觀點插在文章的哪個段落（例如：開頭用別人的故事，中間轉折用你的觀點）
- **Output**: 一篇結構完整的初稿

---

### 3. The "Anti-Hallucination" Verifier（風格守門員）

**我們做了什麼（Manually）：**

1. 我寫了第一版
2. 你說「開頭太像別人的故事，移除」、「充滿塑膠味」
3. 我們才進行修正

**Can be Codified（自動化邏輯）：**

#### "The Style Police"

- **Trigger**: 在 Draft 生成之後，**發送給人類之前**
- **Action**: Agent 把草稿拿去跟 `Style Memory`（你的地雷庫）比對
  - *Check 1*: 有沒有用到禁用詞（e.g., "招聘", "視頻", "質量"）？
  - *Check 2*: 開頭是不是用了 "Storytelling"（Story format）？（剛剛學到的規則）
  - *Check 3*: 結尾有沒有用自我解嘲？
- **Result**: 如果違反規則，Agent **自己退回重寫**，直到通過檢查才敢拿給你看

---

## 總結

我們剛剛手動完成了一個 **Self-Improving Loop（自我進化迴圈）**：

1. **Execution**: 寫作
2. **Critique**: 你罵我寫得不好
3. **Correction**: 修改文章
4. **Learning**: **修改程式碼** 並 **植入記憶**（這是最關鍵的一步）

### What specifically could be codified?

就是把第 4 步自動化。

未來的 Agent 應該要在你修改文章的瞬間，就自己問自己：「我剛剛犯了什麼錯？我該如何修改我的 System Prompt 或 Vector DB，確保下次不再犯？」然後自己去執行 `plant`。

這就是你口中的 **"Eliminate your own job"** —— 你連「教 AI」這件事都可以慢慢被 AI 取代。
