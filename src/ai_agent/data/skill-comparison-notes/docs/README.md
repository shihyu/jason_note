# Skill 比較筆記

這份文件整併 `skill-creator`、`skill-creator-advanced`、`spec-organizer` 三者的差異，重點放在定位、交付物、路由邊界，以及 `skill-creator-advanced` 如何處理 `互搶`。

## 一句話定位

- `skill-creator`：把 skill 寫出來並做基本迭代。
- `skill-creator-advanced`：把 skill 做成可安裝、可測、可發佈的正式資產。
- `spec-organizer`：把模糊想法整理成可開發、可驗收的 spec。

## 快速結論

`skill-creator-advanced` 之所以是進階版，不是因為它「寫得比較長」，而是它額外處理了普通版本沒有完整覆蓋的工程問題：

- skill 邊界是否清楚
- description 是否能穩定路由
- output contract 是否固定
- with-skill 與 baseline 是否有 benchmark
- 是否能打包、發佈與長期維護

## 這份比較回答的核心問題

- `skill-creator-advanced` 為什麼算進階
- `互搶` 是什麼，會造成什麼結果
- `skill-creator-advanced` 怎麼避免和別的 skill 互搶
- 哪些 prompt 應該進哪一個 skill

## 系統架構

```text
┌──────────────────────┐
│ 原始定義來源         │
│ SKILL.md / references│
└──────────┬───────────┘
           │ 讀取
           v
┌──────────────────────┐
│ 邊界分析層           │
│ - 核心工作           │
│ - trigger phrases    │
│ - negative triggers  │
│ - output contract    │
│ - handoff            │
└──────────┬───────────┘
           │ 比對
           v
┌──────────────────────┐
│ 路由決策層           │
│ 誰該接、誰不該接     │
└──────────┬───────────┘
           │ 交付
           v
┌──────────────────────┐
│ 最終產物             │
│ spec / skill draft   │
│ publish-ready skill  │
└──────────────────────┘
```

## skill 路由示意圖

```text
使用者需求
    │
    ├─「整理模糊需求成規格」──────────────> spec-organizer
    │                                      輸出：技術 spec / 白話 spec / stage plan
    │
    ├─「先做一個 skill 草案」────────────> skill-creator
    │                                      輸出：SKILL.md 草案 / eval 初稿
    │
    └─「做成可發布 skill 資產」──────────> skill-creator-advanced
                                           輸出：可安裝 skill / overlap 規則 / benchmark
```

## 三者比較表

| Skill | 核心工作 | 該接 | 不該接 | 主要交付物 |
|---|---|---|---|---|
| `skill-creator` | 把 skill 做出來並迭代 | 新建 skill、修改 skill、補測試案例、調整 description | 不要求正式發版治理、registry readiness、完整 overlap 與 ROI 分析 | `SKILL.md` 草案、測試 prompts、迭代建議 |
| `skill-creator-advanced` | 把 skill 做成正式資產 | 建立、改版、評估、benchmark、打包、發佈可重複使用的 skill | 一次性 prompt、單純潤稿說明、只做單一 tool 或 function schema | 可安裝 skill、evals、overlap 規則、benchmark、package |
| `spec-organizer` | 把模糊需求整理成可開發 spec | 整理 PRD、補 acceptance criteria、拆 stage plan、先研究再寫 spec | 不直接產出 skill 資產、不負責 skill registry readiness | 技術 spec、白話 spec、Codex / Claude Code 分階段計畫 |

## `互搶` 的定義

`互搶` 是指多個 skill 對同一類 query 都判定「這應該由我接」，造成路由重疊。

常見條件：

- description 都寫得太寬
- 核心工作沒有切成單一主要工作
- 沒有寫 negative triggers
- 沒有定義 handoff
- 交付物名稱太像，例如都叫「整理流程」或「規劃文件」

## `互搶` 發生時的資料流

```text
同一句 prompt
    │
    ├─ skill A：認為自己該接
    ├─ skill B：也認為自己該接
    │
    v
路由不穩定
    │
    ├─ 有時進 A，有時進 B
    ├─ 交付物格式不一致
    ├─ 回覆策略不一致
    └─ 使用者必須反覆修正方向
```

## 為什麼 `skill-creator-advanced` 是進階版

它補強的是工程治理，不只是內容長度。

### 補強點 1：把 description 當 decision boundary

普通版會教你把 description 寫得能觸發；進階版要求它同時回答：

- 做什麼
- 何時用
- 何時不用
- 成功輸出是什麼

### 補強點 2：把 output contract 寫死

進階版要求固定段落、欄位、格式、長度與完成條件，避免 skill 載入後輸出漂移。

### 補強點 3：把相鄰 skill 衝突納入設計

進階版會先列 neighboring skills、negative triggers、handoff，而不是等互搶發生後才補救。

### 補強點 4：把測試升級成 benchmark

不只測能不能跑，還比較：

- with-skill 對 baseline
- hit@1、hit@3
- false positive
- confusion matrix
- ROI 是否值得

### 補強點 5：把發佈與信任訊號納入流程

進階版會檢查：

- frontmatter
- homepage
- license
- references 路徑
- package 與 registry readiness

## 避免互搶的方法

1. 先定義單一主要工作，不讓一個 skill 同時做太多事。
2. 先寫 negative triggers，把不該接的句子明講。
3. 先列 neighboring skills，知道自己在和誰切邊界。
4. 寫 handoff 規則，讓相鄰 skill 可以明確交接。
5. 用 overlap evals 驗證，不靠感覺判斷。

## `skill-creator-advanced` 如何避免互搶

### 1. 先切 single primary job

每個 skill 先定義只有一個主要工作，避免同時承擔研究、整理、寫作、發佈等多種交付物。

### 2. 先列 neighboring skills

先找出最容易混淆的相鄰 skill，例如：

- `spec-organizer`
- `skill-creator`

這樣 description 就不是抽象介紹，而是有實際競爭對象的邊界說明。

### 3. 補 negative triggers

除了寫「何時用」，還要寫「何時不要用」。這會直接縮小誤觸發面積。

### 4. 寫 handoff 規則

當需求還在 spec 階段時，先交給 `spec-organizer`；當需求已確定要做成正式 skill 資產時，再 handoff 到 `skill-creator-advanced`。

### 5. 做 overlap evals

不是只靠人工直覺，而是測：

- 應觸發
- 不應觸發
- near-miss
- 中英混合改寫
- 鄰近 skill confusion matrix

## prompt 分流示例

提示語句 1：幫我把這個產品想法整理成可開發 spec，還要補驗收條件。  
判斷：`spec-organizer`  
原因：最終交付物是 spec，不是 skill。

提示語句 2：幫我把這套流程整理成一個 skill，先有可用初稿就好。  
判斷：`skill-creator`  
原因：目標是先做出 skill 草稿，不要求完整發版治理。

提示語句 3：幫我把這個 skill 做到可以 benchmark、避免跟別的 skill 撞，最後能打包發佈。  
判斷：`skill-creator-advanced`  
原因：需求明確包含 overlap、benchmark、package 與發佈面。

## 容易混淆的邊界

### `spec-organizer` vs `skill-creator`

- 前者交付的是可開發 spec
- 後者交付的是 skill 初稿

### `skill-creator` vs `skill-creator-advanced`

- 前者重點是寫出來、跑起來、迭代
- 後者重點是邊界、驗證、benchmark、package、發佈

### `spec-organizer` vs `skill-creator-advanced`

- 前者處理需求成形
- 後者處理 skill 資產成形

## 資料流範例

1. 輸入：`幫我把這套 agent workflow 做成可以重複安裝與發佈的 skill。`
2. 判斷：需求不是單純 spec，也不是只是 skill 草案，而是正式資產。
3. 路由：進 `skill-creator-advanced`。
4. 輸出：skill 邊界、evals、benchmark、package 與 registry readiness 檢查。

## 最短判斷規則

只問三件事：

1. 最終交付物是不是 spec？
2. 如果不是 spec，是 skill 草稿還是正式 skill 資產？
3. 這個需求有沒有明確要求 overlap、benchmark、registry readiness？

如果第 3 題答案是有，通常就不是 `skill-creator`，而是 `skill-creator-advanced`。
