# Output Patterns

這份文件聚焦在「怎麼把輸出格式鎖到夠穩」，特別是 `output contract`、模板與 few-shot 的寫法。

## 1) 先決定你要的是 strict contract 還是 flexible default

不是所有 skill 都需要同樣嚴格的格式。

適合 strict contract：
- API / MCP 回傳
- 固定欄位 JSON
- SQL / regex / YAML
- 必須逐欄驗證的報表

適合 flexible default：
- 一般分析備忘錄
- 可依情境調整段落的長文
- 探索型摘要

## 2) Strict output contract 範本

當你需要固定格式時，直接寫死：

```md
<output_contract>
Return exactly these sections in order:
1. Decision
2. Why now
3. Key evidence
4. Risks
5. Recommended next step

Formatting rules:
- Use Markdown headings exactly as written above.
- Do not add extra sections.
- Keep each section under 120 words.
- If evidence is missing, say "Insufficient evidence" instead of guessing.
</output_contract>
```

這類 contract 至少要回答：
- 段落順序
- 標題文字是否固定
- 每段長度
- 可否新增額外段落
- 缺資料時如何處理

## 3) Flexible default 範本

當你要的是穩定但保留調整空間，可以這樣寫：

```md
<output_contract>
Use this default structure unless the request explicitly requires another format:
1. Summary
2. Findings
3. Risks
4. Next actions

You may merge or rename sections only if doing so improves clarity for the user.
</output_contract>
```

關鍵不是完全放手，而是把可調整範圍講清楚。

## 4) 用 few-shot 鎖定風格與判準

當任務的難點不是格式，而是：
- 語氣
- 詳略程度
- 判讀標準
- 欄位內容的好壞

請補 worked examples。

範例：

```md
<examples>
Example 1
Input:
- notes from customer interview
- audience: product manager

Output:
## Key problem
Users cannot tell whether sync has finished.

## Evidence
- 4/5 interviewees waited for a confirmation state
- 2 users retried upload and created duplicates

## Recommendation
Add a visible sync-complete state before promoting bulk upload.

Example 2
Input:
- incident log excerpt
- audience: engineering manager

Output:
## Incident summary
The outage lasted 14 minutes and affected checkout retries only.

## Root cause
A cache invalidation race left stale pricing rules in one region.
</examples>
```

few-shot 的重點：
- 讓範例看起來像真實任務，不要像課本答案
- 優先展示你最在意的判準
- 如果有常見錯誤，補一組 bad vs good 對照更有效

## 5) 常見搭配方式

### Contract-only

適合：
- 結構已很明確
- 不太需要風格示範

### Contract + one ideal example

適合：
- 要求固定格式
- 也希望風格一致

### Contract + good/bad comparison

適合：
- 評分標準容易混淆
- 容易出現形式正確但內容空洞的結果

## 6) 失敗訊號

看到下列現象，代表該補 `output contract` 或 few-shot：
- 每次段落順序都不一樣
- 標題常被模型自行改寫
- 格式看似正確，但內容深度忽高忽低
- 只有作者知道什麼叫做好輸出，文件本身卻沒寫清楚
- 明明要 JSON，卻偶爾混出說明文字

## 7) 快速檢查表

- 有沒有明寫段落順序或欄位順序
- 有沒有定義缺資料時的輸出
- 有沒有說可不可以自由加段
- 如果風格重要，有沒有 few-shot
- 範例是否貼近真實輸入
- contract 是否能被機械檢查
