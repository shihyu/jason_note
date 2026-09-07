# CRAP 指標工具地圖：crap4clj 與跨語言生態

> 整理自與 Claude Code 的討論，起因是研究 [crap4clj](https://github.com/unclebob/crap4clj) 這個 Robert C. Martin（Uncle Bob）維護的 Clojure 專案。內容涵蓋 crap4clj 的定位、它是否為「通用 agent skill」，以及 CRAP 指標在其他語言生態的實作現況。CRAP 分數的計算公式與應用原則另見〈[Uncle Bob 的 Agent 工作流操作層：CRAP、Mutation 與 Prompt Template](uncle-bob-agent-workflow-crap-mutation-prompt-template.md)〉。

## crap4clj 是什麼

**crap4clj** 是一個為 Clojure 專案計算 **CRAP（Change Risk Anti-Pattern）指標**的分析工具，結合「循環複雜度」與「測試覆蓋率」（來自 Cloverage），找出既複雜又缺乏測試的高風險函式。

- 支援兩種啟動方式：Babashka（`bb crap`，推薦，啟動快）與 Clojure CLI（`clj -M:crap`，除錯用備援）
- 原始碼發現範圍：`.clj`、`.cljc`、`.bb`（可分析獨立的 Babashka 腳本）
- 架構（`src/crap4clj/`）：`core.cljc`（進入點）、`complexity.cljc`（複雜度計算）、`coverage.cljc`（覆蓋率解析）、`bb_coverage.cljc`（Babashka 覆蓋率蒐集）、`crap.cljc`（分數計算與報告）、`cli.cljc`（命令列參數）
- 附有 `SKILL.md`，可作為 Claude Code skill 使用

## 它是「通用 agent skill」嗎——不是

crap4clj 的 `SKILL.md` frontmatter 只在使用者要求「CRAP report」「cyclomatic complexity analysis」「code quality metrics」時觸發，屬於**領域/工具特化型 skill**，而非跨語言、跨任務類型的通用流程（對照 `superpowers:systematic-debugging` 這類真正通用的方法論 skill）。

限制原因：

| 限制點 | 說明 |
|--------|------|
| 語言解析 | `complexity.cljc` 是針對 Clojure 語法（`if`/`when`/`cond`/`and`/`or`/`loop`/`catch` 等）寫死的複雜度規則，不理解其他語言的語法樹 |
| 覆蓋率工具綁定 | 依賴 Cloverage，讀取的是 Cloverage 專屬的 HTML/LCOV 報告格式 |
| 專案設定綁定 | 需要 `deps.edn`（Clojure CLI）或 `bb.edn`（Babashka）並設好 `:cov`/`:crap` alias |

## CRAP 指標在其他語言的實作

CRAP 這個「複雜度 × (1-覆蓋率)³ + 複雜度」的公式本身語言中立，但因為覆蓋率工具本身就綁定各語言生態（Cloverage 只懂 Clojure、Istanbul 只懂 JS、JaCoCo 只懂 JVM），所以沒有單一工具能真正跨語言自動算覆蓋率這塊。實際生態是「一個公式、多個各語言獨立實作」：

| 語言 | 工具 | 特色 |
|------|------|------|
| Java（原始版本） | [crap4j](http://www.crap4j.org/) | Alberto Savoia 提出 CRAP 概念的原始實作 |
| Go | [crap4go](https://github.com/unclebob/crap4go) | Uncle Bob 維護，跟 crap4clj 系出同源 |
| .NET/C# | [crap4dotnet](https://github.com/7Factor/crap4dotnet) | JSON 輸出、CI 友善 |
| Rust | [cargo-crap](https://github.com/minikin/cargo-crap) | Cargo 子指令形式 |
| TypeScript/JS | [crap4ts](https://github.com/sebassdc/crap4ts) | 支援 Istanbul 覆蓋率格式，附帶跨 agent 的 AI skill |
| PHP | [codecept-coverage-reporter](https://github.com/nebbia-fitness/codecept-coverage-reporter) | 整合 Codeception |
| Groovy | [GMetrics（CrapMetric）](https://dx42.github.io/gmetrics/metrics/CrapMetric.html) | 內建於 GMetrics 工具集 |

### 較接近「多語言」的輔助工具

| 工具 | 說明 | 限制 |
|------|------|------|
| [Lizard](https://github.com/terryyin/lizard) | 支援 C/C++、Java、JS、Python、Go、Rust 等十幾種語言的複雜度計算 | 只算複雜度，不算覆蓋率也不算 CRAP 分數，需自行接覆蓋率再套公式 |
| SciTools Understand | 商業工具，支援多語言的程式碼度量 | 付費，非專門的 CRAP 工具，需自訂 metric |

## 結論

沒有一個真正「單一工具、原生支援任意語言」的 CRAP 分析工具存在，主因是覆蓋率工具天生綁定語言/測試框架。若專案橫跨多個語言（例如同時有 Clojure、Go、TypeScript），比較實際的做法是：

1. 各語言用各自的 CRAP 工具（上表列出的那些），統一輸出格式（例如都轉成同一份 JSON schema）方便彙總比較
2. 或自建 pipeline：Lizard 算複雜度 + 各語言原生覆蓋率工具 + 自己實作公式，但需要額外開發維護成本
