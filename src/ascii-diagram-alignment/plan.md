# src Markdown 純文字圖對齊計畫

## 任務目標

檢查 `/home/shihyu/github/jason_note/src` 下所有 Markdown 的 ASCII／Unicode 方框圖、流程圖、架構圖、文字表格與目錄樹；只修正實際的顯示欄位偏移。保留原有 emoji、標籤、內容與圖外文字。推送前逐檔驗證並只提交本任務檔案。

## 專案資料夾名稱

`ascii-diagram-alignment`（本計畫及驗證工具的資料夾；待修的 Markdown 仍留在各自原位置）。

## 預期產出

- 文件：各 Markdown 中實際歪掉的圖，以及 `_doc/v0.1.md` 版本紀錄；如需下一版，依序使用 `_doc/v0.2.md`。
- 程式碼：可重跑的圖形盤點／驗證工具，放在 `ascii-diagram-alignment/`，只負責掃描與報告，不改寫原檔。
- 測試：公開函式的行為與邊界條件放 `tests/unit/`；從 `src` 根目錄掃描 Markdown 的完整流程放 `tests/system/`。日誌和暫存產物集中 `tests/`，完成後清理。

## Build／debug／test 與 Makefile

- `make` 無參數顯示 help；必備 `build`、`run`、`test`、`clean`。
- `make build` 檢查 Python 程式與 Markdown 可讀性；`make run` 列出有圖的檔案、行號及偏移；`make test` 只呼叫 `./test.sh`；`make clean` 清理 `tests/` 暫存產物。
- `./test.sh` 為本任務全部單元＋系統測試的單一入口，失敗時返回非零狀態；`make clean && make build` 可重複執行。
- Debug：單張圖用 `python3 /home/shihyu/.codex/skills/cjk-ascii-diagram/scripts/align.py -`；未標記與 `text` code block 用同 skill 的 `md_check.py FILE.md`；其他語言標記的圖由掃描工具抽出後送 `align.py`。
- 本任務不是 server，沒有預設 port。

## 驗收標準

1. 盤點所有 `.md`，包含有／無語言標記的 fenced block 及圖形字元；記錄原檔與行號。暫以 4,269 個 Markdown、470 個方框候選檔為初步規模，最終數字以完整掃描為準。
2. 修改前先讀目標路徑適用的 `AGENTS.md` 與既有 `plan.md`，並檢查檔案原本是否有使用者未提交變更。
3. 區分真正偏移與檢查器誤報（例如程式輸出表格）；只調整圖內空白或框線。emoji 一律保留；若不能只靠排版修正，先回報再討論。
4. 每張修正圖由 `align.py`／`md_check.py` 或對應幾何檢查驗證；全目錄 `./test.sh`、`git diff --check` 通過，原有圖示與文字未遺失。
5. 版本文件包含目標與範圍（相對前版）、新增／修改／移除項目、測試與驗收、風險／相容性／回滾。提交並推送時僅包含本任務相關檔案。

## 子任務

1. 全目錄盤點並人工覆核候選圖；標出真實偏移、誤報、目標檔的本地規則。每步結束回報是否需更新本計畫。
2. 先寫單元與系統測試，實際執行並提供完整終端輸出；若失敗，先回報原因並等待討論。
3. 建立最小掃描工具與 `test.sh`／Makefile，執行測試；逐張修圖、逐張驗證，通過後才進下一張。
4. 全量驗證、檢查 diff、撰寫 `_doc/v0.1.md`，再提交與推送。

## 對應版本文件

`/home/shihyu/github/jason_note/src/ascii-diagram-alignment/_doc/v0.1.md`
