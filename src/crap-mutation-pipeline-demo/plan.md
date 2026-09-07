# plan.md — CRAP + Mutation Testing 五階段流水線示範工具

## 任務目標

依據 `uncle-bob-agent-workflow-crap-mutation-prompt-template.md` 描述的五階段流水線
（Specification → Writing → Cleanup(CRAP) → Strengthening(Mutation) → QA），
做出一個**可實際執行**的示範工具：

- 真的會計算 CRAP Score（不是紙上公式）
- 真的會做 Mutation Testing 並算出 Mutation Score
- Stage 1/2（Specification/Writing）真的呼叫 `claude -p` headless CLI 產生驗收測試與程式碼，
  Stage 3/4（Cleanup/Strengthening）用確定性工具/腳本把關，不合格會自動打回 Stage 2 重寫
- 支援語言：Python、Go、Rust、JavaScript、C/C++

## 專案資料夾

`crap-mutation-pipeline-demo/`（本目錄，kebab-case）

## 架構決策（請確認）

1. **複雜度計算：不用 5 種不同語言的第三方複雜度工具**（radon/gocyclo/…），
   改寫**一個通用的正規表示式分支計數器**（數 `if/else/while/for/case/&&/||/and/or/catch` 等關鍵字 +1），
   五個語言共用同一份邏輯，只是關鍵字表不同。
   理由：五套工具輸出格式不同、部分語言（Rust）沒有成熟對應工具，維護五套 parser 不划算，
   而 CRAP 公式本來就只需要「一個整數」，通用計數器已經夠用。
2. **Mutation Testing：不依賴每個語言的第三方 mutation 工具**
   （mutmut/Stryker/go-mutesting 版本新舊不一，C/C++ 的 Mull 需要 LLVM 環境，設定複雜），
   改寫**一個通用的文字替換 mutation engine**（`>`↔`>=`、`+`↔`-`、`true`↔`false`、`&&`↔`||`…），
   對原始檔套用單一變異、重新編譯/執行測試指令、記錄 killed/survived。
   已知限制：純文字替換對複雜語法（巢狀泛型、字串常數內剛好有運算子符號）可能誤判，
   非工業級精度，僅供示範五階段流程用。
3. **Coverage（覆蓋率）維持用各語言原生工具**（這塊各語言本來就有標準做法，不用自己重寫）：
   - Python：`coverage.py`（已安裝）
   - Go：`go test -cover`（內建，已有 go）
   - Rust：`cargo-tarpaulin` 或 `cargo llvm-cov`（**未安裝**，做到 Rust 子任務時會問是否安裝）
   - JavaScript：`c8` 或 `nyc`（**未安裝**，做到 JS 子任務時會問是否安裝）
   - C：`gcov`（已安裝）
4. **Stage 1/2 呼叫真的 `claude -p`**：會消耗你帳號的 token/額度，且輸出非決定性。
   單元測試預設 **mock 掉這個呼叫**，只有明確要求跑「真的端對端」時才會真的花 token。

## 目錄結構（預期產出）

```
crap-mutation-pipeline-demo/
├── plan.md
├── Makefile
├── test.sh
├── requirements.txt
├── _doc/
│   └── v0.1.md
├── pipeline/
│   ├── __init__.py
│   ├── cli.py               # 入口：spec/write/cleanup/strengthen/qa/run 子指令
│   ├── crap.py              # 通用複雜度計數器 + CRAP 公式
│   ├── mutation.py          # 通用 mutation engine
│   ├── claude_agent.py      # 呼叫 `claude -p` 的 wrapper（Stage 1/2 用）
│   ├── state.py             # 每個 task 的階段狀態追蹤（JSON），含 retry 上限
│   └── languages/
│       ├── __init__.py
│       ├── base.py          # LanguageConfig 介面：test_cmd/coverage_cmd/coverage_parser/complexity_keywords
│       ├── python_lang.py
│       ├── go_lang.py
│       ├── rust_lang.py
│       ├── javascript_lang.py
│       └── c_lang.py
├── templates/
│   └── prompt_template.md   # 沿用文章附的 template，填入五階段各自 prompt
├── examples/                 # 每語言一個最小示範函式，供 pipeline 端對端跑
│   ├── python/
│   ├── go/
│   ├── rust/
│   ├── javascript/
│   └── c/
└── tests/
    ├── unit/                # 覆蓋 crap.py / mutation.py / languages/* 的純函式邏輯（mock 掉外部指令與 claude CLI）
    └── system/              # 對 examples/ 實際跑 cleanup/strengthen/qa 階段（真的呼叫 coverage 工具）
```

## build / debug / test 指令

- `make build`：`pip install -r requirements.txt`（僅裝 pytest 等 pipeline 自身依賴，
  **不會**自動安裝跨語言第三方工具；缺什麼工具會印警告）
- `make run`：對 `examples/python` 示範函式跑一次完整五階段（預設語言 python，
  因為工具鏈最完整、不需額外安裝）
- `make test`：呼叫 `./test.sh`
- `make clean`：清除 `.pipeline_state/`、coverage 產物、mutation 暫存檔、`__pycache__`

`test.sh`：
```bash
#!/usr/bin/env bash
set -euo pipefail
echo "==> unit tests"
python3 -m pytest tests/unit -v
echo "==> system tests"
python3 -m pytest tests/system -v
echo "==> all tests passed"
```

## 驗收標準

1. `crap.py` 的 CRAP 公式對文章表格 5 組數值（comp=2/cov=100%→2.0 … comp=10/cov=0%→110.0）算出完全一致的結果
2. 通用複雜度計數器對每個語言各一段人工寫好、已知分支數的小片段，算出正確的環形複雜度
3. 每個語言的 coverage parser 對該語言原生工具**真實的報表輸出格式**能正確解析出覆蓋率百分比
4. `mutation.py` 對「弱測試」（例如只檢查回傳型別、不檢查值）能正確判定 Mutation Score < 100% 並指出存活的變異位置；對「強測試」判定 100%
5. `pipeline.py run --lang python` 端對端跑完五階段（含真的呼叫 `claude -p` 產生驗收測試與實作），
   最終報告顯示 CRAP ≤ 6、Mutation Score = 100%，且 Cleanup/Strengthening 不合格時真的會打回 Stage 2 重寫（設 max_retries=3 避免無限迴圈）
6. 至少 Python 以外再驗證 1～2 個語言的 Cleanup + Strengthening + QA 三階段可對該語言 examples 正確運作
7. `./test.sh` 全綠、exit code 0
8. `make clean && make build` 可重複執行不出錯

## 風險 / 需要之後再確認的事項

- Rust／JavaScript 的 coverage 工具目前未安裝，做到對應子任務時會先問是否要 `cargo install cargo-tarpaulin` / `npm install -g c8`
- Stage 1/2 呼叫真實 `claude -p` 屬於會消耗使用者 token 的動作，預設測試走 mock，真的端對端驗證需你明確同意才執行
- 正規表示式式的 mutation engine 對特殊語法可能有誤判，已在架構決策中說明為已知限制

## 子任務拆解（一次只做一步，每步完成後回報 + 詢問是否更新 plan.md）

依 `/goal 繼續到完成` 指示，全部子任務已連續執行完成，未逐步暫停確認；細節與驗收結果見 `_doc/v0.1.md`。

1. [x] Bootstrap：建立目錄骨架、Makefile、test.sh、`requirements.txt`
2. [x] `pipeline/crap.py`：CRAP 公式 + 通用複雜度計數器（五語言關鍵字表）+ 單元測試（發現原文表格一筆筆誤，已記錄）
3. [x] `pipeline/languages/*`：五個語言的 coverage 指令與 parser，且五語言（含 Rust/JS，已安裝 cargo-tarpaulin/c8）都用真實工具端對端驗證過
4. [x] `pipeline/mutation.py`：通用 mutation engine + 單元測試；額外用 Python/Go 真實工具（pytest/go test）端對端驗證 Mutation Score
5. [x] `pipeline/state.py` + Stage 3/4/5 orchestration（`pipeline/cli.py`）：CRAP/Mutation 不合格時打回 Stage 2 重寫，max_retries=3
6. [x] `pipeline/claude_agent.py`：Stage 1/2 呼叫 `claude -p`，單元測試 mock 掉真實呼叫；prompt 內容直接寫在程式碼裡，未另外產出 `templates/prompt_template.md`（避免同一份邏輯維護兩份，屬對原目錄結構的簡化偏離）
7. [x] `pipeline/cli.py run`：對 Python 範例做真實端對端驗證（真的呼叫 claude CLI），一次嘗試即成功，CRAP=3.0、Mutation Score=100%
8. [x] 其餘語言（Go/Rust/JS/C）的 Cleanup+Strengthening 已用真實工具驗證；orchestration（Stage1/2/retry 迴圈）目前只接 Python，其餘語言留待 v0.2
