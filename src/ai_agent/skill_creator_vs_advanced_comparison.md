# `skill-creator` vs `skill-creator-advanced` 差異整理

## 一句話差異

- `skill-creator`：像一位會陪你把事情做出來的助教，重點是快速開始、邊做邊調整。
- `skill-creator-advanced`：像一位 Tech Lead 或 QA Lead，重點是可重複、可驗證、值得長期維護。

## 核心定位差異

### `skill-creator`：對話型工具，偏靈活

核心想法：

> 你現在在哪個階段，就陪你做到哪個階段。

適合情境：

- 從零開始建立 skill
- 已經有草稿，想繼續補強
- 只是想先驗證一個 idea 或 vibe

特性：

- 語氣較輕鬆
- 偏人性化互動
- 強調快速開始
- 先做出來，再慢慢優化

### `skill-creator-advanced`：工程流程工具，偏嚴謹

核心想法：

> 如果不能穩定重做，就還不算工程化。

它把「做 skill」視為：

> 一個完整的工程生命週期（lifecycle）

而不是：

> 一次剛好成功的 prompt 對話

## 方法論差異

### `skill-creator`：探索式迭代

流程：

```text
draft
-> test
-> review
-> improve
-> repeat
```

精神：

> 先跑起來，再逐步優化。

很像：

> 手動調整 strategy，backtest 後再 tweak，接著重跑一次。

### `skill-creator-advanced`：工程式品質控管

精神：

> 不只是能跑，而是要穩定、可驗證、可維護。

## 九條核心原則

1. `description` 要先寫對，因為它本質上就是 API contract。
2. 先看 context，再決定是否提問；能自己推理就不要把成本丟給使用者。
3. 把脆弱步驟移到 script，因為手動流程通常不可重複。
4. 避免 context 膨脹，不要無限制堆疊 prompt、rules 與 examples。
5. 測試要真實，不能只測漂亮案例。
6. `with-skill` 與 `baseline` 必須使用同一批測試資料，才有可比性。
7. 先定義 skill 邊界，再優化 wording。
8. ROI 不成立就刪除，維護成本高於價值時不應保留。
9. skill 資料夾不要放 `README.md`，避免文件重複與責任邊界混亂。

## 工具與自動化差異

### `skill-creator`

主要工具：

```text
run_loop.py
```

用途：

> 自動優化 `description`

其他特性：

> 仍然主要依賴人工判斷與對話推進。

### `skill-creator-advanced`

新增多個工程化 script：

```text
init_skill_advanced.py
format_check.py
quick_validate.py
generate_test_plan.py
prepare_eval_workspace.py
aggregate_benchmark.py
check_regression_gates.py
```

本質上更像：

> skills 專用的 mini CI/CD 流程

## 測試策略差異

### 多語言觸發測試

例如：

```text
中文
英文
中英混合
縮寫
```

原因：

> 真實使用者不會完全照設計者預期的語言格式發問。

### Skill overlap matrix

用途：

> 避免多個 skill 同時搶同一個 request。

例如：

```text
skill A: 查股票
skill B: 投資分析

User: 分析台積電
```

這時兩個 skill 都可能被觸發。

### Regression gates

發版門檻可能包含：

```text
accuracy >= 90%
latency <= 2s
error rate <= 1%
```

原則：

> 沒過門檻，就不能 release。

## 文件哲學差異

### `skill-creator`

文件數量：

```text
約 4 份
```

重點：

> 讓使用者能快速開始。

### `skill-creator-advanced`

文件數量：

```text
約 11 份 references
```

採用方式：

> progressive disclosure（按需閱讀）

結構示意：

```text
SKILL.md
  ->
Deployment Playbook
  ->
ROI Model
  ->
Boundary Management
```

## 最直覺的工程師比喻

### `skill-creator`

像：

```text
jupyter notebook
```

特性：

- 靈活
- 快速試驗
- 互動性高

### `skill-creator-advanced`

像：

```text
production ML pipeline
```

包含：

- evaluation
- regression test
- benchmark
- release gate

## 快速對照表

| 面向 | `skill-creator` | `skill-creator-advanced` |
| --- | --- | --- |
| 定位 | 對話式協作 | 工程化治理 |
| 目標 | 先做出來 | 做成可維護產品 |
| 風格 | 靈活、快速 | 嚴謹、可驗證 |
| 測試 | 以互動驗證為主 | 以 benchmark、regression、gate 為主 |
| 文件 | 精簡、快速上手 | 分層、按需展開 |
| 適合情境 | 探索、起步、快速試作 | 建立可重複、可評估、可發布的 skill |

## 最後一句總結

> **`skill-creator` 是把東西做出來。**
>
> **`skill-creator-advanced` 是把東西做成產品。**
