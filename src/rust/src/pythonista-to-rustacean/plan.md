# plan.md

## 任務目標

對 `pythonista-to-rustacean` 範例倉庫進行編譯、測試與執行驗證，回報實際 terminal 輸出與失敗原因。

下一階段已確認：修正目前 5 個 `cargo build` 失敗項目，並重新執行編譯與可安全執行的範例。

## 專案資料夾名稱

`pythonista-to-rustacean`

## 現況與範圍

- 根目錄目前沒有 `Cargo.toml` workspace，也沒有 `Makefile`。
- 本倉庫包含多個章節子專案，目前偵測到 81 個 `Cargo.toml` 與 18 個 `pyproject.toml`。
- 部分教材範例名稱顯示可能是刻意無法編譯的案例，例如 `borrow_of_moved`、`cannot_borrow_as_mutable`、`does_not_live_long`。這些失敗需分類回報，不直接修復。
- Ch9 PyO3 範例使用 `uv` / `pytest`。
- Ch10、Ch11 AI 範例可能需要模型檔、網路下載或較長執行時間；先以編譯/測試為主，執行階段需逐項確認是否安全且合理。
- 已知待修正編譯失敗項目：
  - `ch09_pyo3/09_enum2class_example`
  - `ch09_pyo3/14_inheritance_example`
  - `ch10_candle_ai/01_candle_mnist`
  - `ch10_candle_ai/02_candle_distilbert`
  - `ch11_burn_ai/03_burn_huggingface_dataset`

## 預期產出

```text
pythonista-to-rustacean/
├── plan.md
└── tests/
    └── logs/
        ├── environment.log
        ├── cargo-build.log
        ├── cargo-test.log
        ├── cargo-run.log
        └── uv-pytest.log
```

若使用臨時二進位或中間檔，全部放在 `tests/tmp/`，任務結束後清理。

## Build / Debug / Test 指令

### 環境檢查

```bash
cargo --version
rustc --version
uv --version
python --version
```

### Rust 編譯

逐一對所有 Cargo 子專案執行：

```bash
cargo build --manifest-path <path>/Cargo.toml
```

### Rust 測試

逐一對所有 Cargo 子專案執行：

```bash
cargo test --manifest-path <path>/Cargo.toml
```

### Rust 執行

只對具有 binary target 的 Cargo 子專案執行：

```bash
cargo run --manifest-path <path>/Cargo.toml
```

`ch01_basics/01_rust_intro/main.rs` 沒有 `Cargo.toml`，以 `rustc` 編譯到 `tests/tmp/` 後執行：

```bash
rustc ch01_basics/01_rust_intro/main.rs -o tests/tmp/ch01_01_rust_intro
tests/tmp/ch01_01_rust_intro
```

### PyO3 / Python 測試

逐一進入含 `pyproject.toml` 的 Ch9 子專案執行：

```bash
uv run pytest
```

## Makefile 規範

若本任務要固化為專案工具，需新增根目錄 `Makefile`，並提供：

- `make`：顯示 help
- `make build`：執行 Rust 編譯驗證
- `make test`：執行 Rust / PyO3 測試驗證
- `make run`：執行可安全執行的 binary 範例
- `make clean`：清理 `tests/tmp/`、`tests/logs/` 與建置產物

本輪若未被確認，不新增 Makefile。

## 驗收標準

- 實際執行環境檢查並回報完整輸出。
- 實際執行編譯命令並回報完整輸出。
- 實際執行測試命令並回報完整輸出。
- 實際執行可執行範例並回報完整輸出。
- 對每個失敗項目標示：命令、路徑、錯誤摘要、是否可能為教材預期失敗。
- 測試/執行產物集中在 `tests/`，任務結束後清理臨時檔。
- 修正後 5 個既有失敗項目需 `cargo build` 通過。
- 可安全執行的 binary target 需 `cargo run` 通過；若範例需要外部模型、網路、GPU 或長時間訓練，需在回報中列為跳過原因。
- 若發現需要額外系統套件或依賴策略調整，先優先採用專案內可重現的 Cargo 設定；無法處理時再回報環境需求。

## 子任務拆解

1. 確認本 `plan.md`。
2. 建立 `tests/logs/` 與 `tests/tmp/`。
3. 執行環境檢查。
4. 掃描所有 Cargo / PyO3 子專案。
5. 執行 Rust 編譯驗證。
6. 執行 Rust 測試驗證。
7. 執行可安全執行的 binary 範例。
8. 執行 PyO3 / Python 測試。
9. 彙整 pass/fail、完整輸出與失敗分類。
10. 清理臨時檔，提出是否需更新 `plan.md` 的建議。
11. 針對 5 個編譯失敗項目重跑 failing baseline。
12. 逐項修正失敗原因，重新執行對應 `cargo build`。
13. 對修正後且可安全執行的 binary 範例執行 `cargo run`。
14. 彙整修正內容、pass/fail 與完整輸出位置。
