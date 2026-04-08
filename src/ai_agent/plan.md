# AI Agent 文件整理計畫

## 任務目標

整理目前的 `test.md`，使其符合下列要求：

1. 修正為合法且穩定的 Markdown 結構。
2. 將簡體中文轉為繁體中文。
3. 將外部圖片下載到本目錄下的 `images/`，並改為本地相對路徑引用。
4. 將 `test.md` 改成可讀、可維護、能反映主題的正式檔名。
5. 把新檔案加入 [`../SUMMARY.md`](/home/shihyu/github/jason_note/src/SUMMARY.md) 的合適章節。

## 專案結構組織

本次工作屬於既有筆記維護，不搬動整個主題資料夾；工作範圍集中在目前的 `ai_agent/` 目錄。

- 既有工作目錄：`ai_agent/`
- 正式文章檔：`ai_agent/<正式檔名>.md`
- 圖片資產：`ai_agent/images/<文章前綴>-01.png`
- 規劃文件：`ai_agent/plan.md`

建議正式檔名候選：

1. `claude-agent-teams-c-compiler-case-study.md`
2. `anthropic-agent-teams-c-compiler.md`
3. 若要沿用目前已存在的未追蹤檔名，則為 `Anthropic-用平行Claude打造C編譯器-繁中整理.md`

## 預期產出

### 程式碼 / 文件 / 測試檔案結構

```text
ai_agent/
├── plan.md
├── <正式文章檔名>.md
├── images/
│   ├── <文章前綴>-01.png
│   └── <文章前綴>-02.png
└── tests/
    └── tmp/
```

說明：

- 本次主要產出是文件與圖片，不新增程式碼模組。
- `tests/tmp/` 僅供驗證階段暫存使用，交付前必須清空。

## 架構設計

### 文件整理流程圖

```text
┌──────────────┐
│ 原始 test.md │
└──────┬───────┘
       │
       v
┌──────────────────┐
│ 結構清理         │
│ - 標題階層修正   │
│ - 清單格式修正   │
│ - 連結格式修正   │
└──────┬───────────┘
       │
       v
┌──────────────────┐
│ 內容正規化       │
│ - 簡轉繁         │
│ - 術語一致化     │
│ - 圖片改本地引用 │
└──────┬───────────┘
       │
       v
┌──────────────────┐
│ 檔案整理         │
│ - test.md 重新命名│
│ - 圖片存入 images │
└──────┬───────────┘
       │
       v
┌──────────────────┐
│ 索引更新         │
│ - 更新 SUMMARY   │
└──────────────────┘
```

### 關鍵模組與互動

- `test.md`：原始來源文件。
- `<正式文章檔名>.md`：整理後的正式文章。
- `images/`：文章內圖片的本地資產。
- [`../SUMMARY.md`](/home/shihyu/github/jason_note/src/SUMMARY.md)：書籍目錄入口。

### 具體運行範例

1. 讀取 `test.md`，找出外部圖片 URL 與 Markdown 結構問題。
2. 下載圖片到 `images/`，例如 `images/claude-agent-teams-c-compiler-case-study-01.png`。
3. 將文章改寫為繁體中文，並把圖片連結改成 `![說明](images/...)`。
4. 將檔案重新命名為正式檔名。
5. 在 [`../SUMMARY.md`](/home/shihyu/github/jason_note/src/SUMMARY.md) 的 `AI 與開發輔助工具` 或其他最貼近主題的位置新增目錄連結。

## Makefile 規範

本任務是文件整理，但仍保留標準目標，後續若確認要實作，Makefile 行為如下：

### 必備目標

- `make`：顯示 help。
- `make build`：檢查文章檔存在、圖片檔存在、Markdown 連結路徑存在。
- `make run`：啟動本地預覽伺服器，預設 port `8000`。
- `make test`：執行 Markdown 結構與圖片引用驗證。
- `make clean`：清空 `tests/tmp/` 與驗證輸出。

### 特殊處理

- 預設預覽 port：`8000`
- `make run` 執行前先清理 `8000` port 佔用

## build / debug / test 指令

目前規劃如下，待確認後再決定是否一併實作：

- `make build`
- `make run`
- `make test`
- `make clean`
- 臨時人工檢查：
  - `sed -n '1,220p' <正式文章檔名>.md`
  - `rg -n "https://developer.qcloudimg.com" <正式文章檔名>.md`
  - `rg -n "<正式文章檔名>|test.md" ../SUMMARY.md`

## 驗收標準

1. `test.md` 不再作為最終文章檔名。
2. 正式文章檔名能反映主題，且與現有檔案命名策略不衝突。
3. 文章全文為繁體中文。
4. 文章中的圖片全部改為 `images/` 內的本地檔案。
5. Markdown 標題、清單、圖片、連結語法正確。
6. [`../SUMMARY.md`](/home/shihyu/github/jason_note/src/SUMMARY.md) 已新增正確條目，位置合理。
7. 若使用 `tests/tmp/` 驗證，交付前必須清空。

## 子任務拆解

1. 確認最終檔名策略，避免與既有同主題檔案衝突。
2. 下載 `test.md` 中的外部圖片到 `images/`。
3. 修正文內 Markdown 語法與排版結構。
4. 將全文轉為繁體中文並統一術語。
5. 重新命名正式文章檔。
6. 更新 [`../SUMMARY.md`](/home/shihyu/github/jason_note/src/SUMMARY.md)。
7. 驗證連結、圖片與檔名引用一致性，清理暫存檔。

## 目前已辨識但尚未釐清的事項

1. 同主題未追蹤檔案 `Anthropic-用平行Claude打造C編譯器-繁中整理.md` 已存在，需決定：
   - 以它作為最終正式檔名並覆蓋內容，或
   - 讓 `test.md` 改成另一個新檔名，避免重複主題並存。
2. [`../SUMMARY.md`](/home/shihyu/github/jason_note/src/SUMMARY.md) 目前已有未提交修改，更新時需要以最小差異方式插入，避免覆蓋既有變更。

## 執行紀錄

- 2026-04-09：採用 `claude-agent-teams-c-compiler-case-study.md` 作為正式檔名，保留既有未追蹤同主題檔案不刪除。
- 2026-04-09：已下載 3 張外部圖片到 `images/`，並改為本地相對路徑引用。
- 2026-04-09：已將文章全文轉為繁體中文、修正標題層級與清單格式。
- 2026-04-09：已將 [`../SUMMARY.md`](/home/shihyu/github/jason_note/src/SUMMARY.md) 內既有條目更新為新檔名。
