# Rust Markdown 區塊圖對齊計畫

## 任務目標

檢查 `src/rust/` 內 Markdown 的純文字方框圖、流程圖與表格；只修正實際顯示欄位偏移，保留原有標籤與語意。目錄樹與程式輸出表格也納入盤點，但檢查器誤報須先人工確認。

## 專案資料夾名稱

`rust`（現有文件目錄；不另建專案）。

## 預期產出

- 文件：原 Markdown 檔中有偏移的圖；版本紀錄 `_doc/v0.1.md`。
- 程式碼：預設不新增正式程式碼；如需可重跑的專案檢查入口，再依本計畫新增。
- 測試結構：若新增檢查程式，單元測試放 `tests/unit/`，Markdown 掃描的使用者流程測試放 `tests/system/`；暫存輸出集中 `tests/`。

## Build／debug／test 指令與 Makefile

- 文件修正沒有編譯產物；`make build` 驗證 Markdown 可讀，`make run` 列出檢查結果，`make clean` 清理 `tests/` 內暫存輸出。
- `./test.sh` 為完整驗證入口，`make test` 呼叫 `./test.sh`；腳本失敗時返回非零狀態。
- `make` 無參數顯示 help；`make clean && make build` 可重複執行。
- Debug：對單一檔案執行 `python3 /home/shihyu/.codex/skills/cjk-ascii-diagram/scripts/md_check.py FILE.md`，必要時用 `align.py -` 檢查單張圖。
- 若只修改文件而不新增檢查程式，單元測試與系統測試不適用；`test.sh` 仍須檢查目標 Markdown 圖與變更範圍。

## 驗收標準

1. 盤點所有 Markdown 中的方框圖、流程圖、目錄樹與文字表格，記錄原檔行號；涵蓋無語言標記及 `text` code block，其他 fence 以人工搜尋補查。
2. 對實際偏移的圖，依顯示寬度修正空白與框線，不更動圖外內容或標籤。
3. 修正後目標圖經 `align.py`／`md_check.py` 驗證為 `no drift`／`無偏移`；工具對外部程式輸出（例如 Polars 表格）的誤報須記錄原因與人工驗證結果。
4. `./test.sh` 成功；`git diff` 僅包含規劃、版本文件、驗證入口及必要的圖內修正。

## 子任務

1. 盤點所有 Markdown 圖，分類真實偏移與檢查器誤報；完成後回報是否需更新本計畫。
2. 先建立驗證入口與必要測試，實際執行並回報完整終端輸出；失敗時先報告原因，等待討論。
3. 逐張修正有偏移的圖；每一步執行驗證並回報結果，通過後才繼續。
4. 最後完整掃描、檢查 diff，撰寫 `_doc/v0.1.md`（目標與範圍、變更、測試驗收、風險／相容性／回滾）。

## 初步盤點

目前在 468 個 Markdown 檔中，找到 22 個檔案、70 個含框線的 code block。檢查器回報 114 項：`rust_locks_guide.md` 流程圖 20 項；`第二部分_進階部分_量化實戰.md` 內 Polars 表格 94 項，後者需先確認是否為 `┆` 符號造成的誤報。此數量不代表 114 處都需要修改。
