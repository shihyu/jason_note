# 讓含中文的 ASCII 方框圖真正對齊：原理與作法

> 在 Markdown、終端機或程式註解裡畫 `┌─┐│` 方框圖，只要標籤含中文，右邊框幾乎一定會歪。本文說明為什麼會歪、怎麼用「腳本計算顯示寬度」來畫和驗證，以及我把這套流程包成 Claude Code skill `cjk-ascii-diagram` 的實作細節。

---

## 一、問題長什麼樣

下面是一個很常見的錯誤：用「字數」決定框寬。`開始` 是 2 個字，`Start` 是 5 個字，程式或 AI 以為最寬 5、框寬 7，於是畫成這樣：

```plaintext
┌───────┐
│ 開始    │
│ Start │
└───────┘
```

在終端機或等寬字型下，`開始` 實際佔 4 欄，第二行的右邊框被推到更右邊。正確的圖應該是：

```text
┌───────┐
│ 開始  │
│ Start │
└───────┘
```

> 本文刻意把「錯誤示範」標成 ```` ```plaintext ````，讓後面介紹的 `md_check.py` 略過它們；正確的圖都標成 ```` ```text ````，而且都通過檢查。

圖越大、中文越多，偏差就越明顯：每一行的中文字數不同，右邊框會像階梯一樣一路往右歪。手動用眼睛補空白只能救一時，改一個字就又歪了。

---

## 二、原理

### 2.1 字元數 ≠ 顯示欄位數

終端機和等寬字型是用「欄位（cell）」排版的。英數字佔 1 欄，中日韓文字佔 2 欄。但大部分程式語言的字串長度算的是「字元數」：

| 字串 | `len()` | 實際顯示欄位（`wcswidth`） |
|---|---|---|
| `開始` | 2 | 4 |
| `Start` | 5 | 5 |
| `中文abc` | 5 | 7 |
| `，`（全形逗號） | 1 | 2 |
| `🚀` | 1 | 2 |

（上表由 Python `wcwidth` 0.8.1 實際計算。）

用 `len()` 或 `str.ljust()` 補空白，中文每多一個字，那一行就多出 1 欄。這就是方框歪掉的根本原因。

```python
from wcwidth import wcswidth

len("開始")       # 2
wcswidth("開始")  # 4  ← 終端機實際佔的欄位
```

### 2.2 Unicode East Asian Width：字元寬度從哪來

每個 Unicode 字元都有一個 East Asian Width（UAX #11）屬性，終端機據此決定佔 1 欄還是 2 欄：

| 屬性 | 意義 | 例子 | 顯示寬度 |
|---|---|---|---|
| `W`（Wide） | 寬字元 | 漢字、假名、諺文、多數 emoji | 固定 2 |
| `F`（Fullwidth） | 全形 | `，。：（）！` | 固定 2 |
| `Na`（Narrow） | 窄字元 | ASCII 英數 | 固定 1 |
| `H`（Halfwidth） | 半形 | 半形片假名 | 固定 1 |
| `N`（Neutral） | 中性 | 多數西方符號 | 1 |
| `A`（Ambiguous） | **模糊** | `─ │ ┌ → · × ▼ ★ ○`、希臘字母 | **看終端機設定，1 或 2** |

`wcwidth` 這類函式庫就是把這張表實作出來：W／F 回傳 2，控制字元回傳 -1，其他回傳 1（模糊寬度預設當 1）。

### 2.3 模糊寬度（Ambiguous）：同一張圖在不同電腦長得不一樣

最麻煩的是 `A` 類字元。在西方語系環境它們佔 1 欄，但很多 CJK 使用者會在終端機打開「模糊寬度字元顯示為雙寬」（iTerm2、GNOME Terminal、PuTTY、mintty 都有這個選項，或設定 `VTE_CJK_WIDTH`）。打開後，`→ · ×` 會變成 2 欄。

所以就算你把欄位算得完全正確，只要框內有 `→`，在別人的終端機上還是會歪。實務上的結論：

- **線框字元 `─│┌┐└┘├┤┬┴┼` 與箭頭 `▼ ▲ ► ◄`**：雖然被歸在 `A` 類，但幾乎所有終端機都特別把它們當 1 欄處理，可以放心用。
- **`→ ← · × ÷ § ° ± ★ ○ □`、希臘字母**：不要放在會決定框寬或欄位的地方。`→` 改寫成 `->`，`×` 改 `x`，`·` 改 `/`。
- **emoji、ZWJ 組合字、變體選擇符（U+FE0F）**：寬度依字型而定，完全不要放進圖裡。

### 2.4 字型：欄位算對了，還要字型配合

欄位數正確只是第一步。中文字型的寬度如果不是英文的剛好 2 倍，畫面還是會有細微偏差。建議使用中英 2:1 的等寬字型，例如更紗黑體（Sarasa Mono）、Noto Sans Mono CJK。

---

## 三、作法：讓腳本當寬度的唯一依據

核心想法只有一句：**不要用眼睛估空白，所有欄位都交給腳本算；交付前一定跑檢查器，exit 0 才算完成。**

```text
┌─────────────────────────────────┐
│ 1. 畫：generate.py 或 canvas.py │◄────┐
│    （腳本依顯示寬度放字）       │     │
└───────────┬─────────────────────┘     │ exit 1：依報告的
            ▼                           │ 行號、欄位修正
┌────────────────────────────────┐      │
│ 2. 驗：align.py 或 md_check.py │──────┘
└───────────┬────────────────────┘
            │ exit 0
            ▼
┌───────────────────────┐
│ 3. 交付：附上檢查輸出 │
└───────────────────────┘
```

（這張圖本身就是用下面介紹的 `canvas.py` 畫的，並通過 `align.py` 檢查。）

這套「生成 → 驗證迴圈」的想法與檢查器，來自 [kouko/monkey-skills](https://github.com/kouko/monkey-skills) 的 `ascii-graph` skill（MIT 授權）。我在它的基礎上補了兩支工具：

| 工具 | 來源 | 用途 |
|---|---|---|
| `generate.py` | 上游 | 固定形狀的生成器：表格、直線流程、樹、長條圖、分層架構、時序圖 |
| `align.py` | 上游 | 對齊檢查器（只報告，不修改） |
| `canvas.py` | 新增 | 任意方框＋箭頭圖的畫布，依顯示寬度放字 |
| `md_check.py` | 新增 | 掃描整份 Markdown，檢查裡面的圖並回報原檔行號 |

### 3.1 生成器：固定形狀直接產生

形狀固定的圖，直接用生成器最省事，輸出保證對齊：

```bash
echo '{"steps":["收到訂單","驗證","出貨"]}' | python3 scripts/generate.py flow
```

```text
┌──────────┐
│ 收到訂單 │
└──────────┘
      │
      ▼
┌──────────┐
│   驗證   │
└──────────┘
      │
      ▼
┌──────────┐
│   出貨   │
└──────────┘
```

支援的形狀與輸入格式（stdin 給 JSON）：

| 形狀 | JSON |
|---|---|
| `table` | `{"headers":[...],"rows":[[...]]}` |
| `flow` | `{"steps":[...]}` |
| `tree` | `{"node":{"label":...,"children":[...]}}` |
| `bar` | `{"pairs":[["標籤",數值]],"width":20}` |
| `arch` | `{"layers":[{"name":...,"components":[...]}]}` |
| `seq` | `{"participants":[...],"messages":[{"from":..,"to":..,"label":..}]}` |

### 3.2 畫布 canvas.py：任意版面的圖

架構圖常常有分岔、橫向箭頭、回頭線，生成器畫不出來。這時用畫布：**座標的 x 是顯示欄位，不是字元索引**。

```python
from canvas import Canvas

c = Canvas()
_, b = c.box(0, 0, ["API 閘道"], bottom_tee=6)      # 回傳 (右邊框欄位, 底邊列號)
c.put(b + 1, 6, "▼")
r1, b1 = c.box(b + 2, 0, ["訂單服務"], bottom_tee=6)
c.put(b + 3, r1 + 1, "──寫入──► ")
c.box(b + 2, r1 + 11, ["Redis 佇列"])
c.put(b1 + 1, 6, "▼")
c.box(b1 + 2, 0, ["對帳服務"])
print(c.render())
```

```text
┌──────────┐
│ API 閘道 │
└─────┬────┘
      ▼
┌──────────┐          ┌────────────┐
│ 訂單服務 │──寫入──► │ Redis 佇列 │
└─────┬────┘          └────────────┘
      ▼
┌──────────┐
│ 對帳服務 │
└──────────┘
```

`box()` 回傳右邊框的欄位與底邊列號，下一個元件就用這兩個數字計算位置，完全不用手數空白。也可以寫成 JSON 規格，用命令列執行：

```bash
cat > spec.json <<'EOF'
{"ops": [
  {"op": "box", "y": 0, "x": 0, "lines": ["API 閘道"], "bottom_tee": 6},
  {"op": "put", "y": 3, "x": 6, "text": "▼"}
]}
EOF
python3 scripts/canvas.py spec.json
```

**畫布的實作原理**

畫布是一張「列 → 欄 → 格子」的二維表。寫入一個字元時，先用 `wcwidth` 算寬度：

- 寬度 1：佔 1 格。
- 寬度 2：佔 2 格，第 2 格放一個「佔位記號」，輸出時跳過。
- 寬度 ≤ 0（控制字元、零寬字元、Tab、換行）：直接拒絕。這些字元會讓欄位計算失準。

以 `put(0, 0, "中ab")` 為例：

| 欄位 | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| 格子內容 | `中` | 佔位 | `a` | `b` |

最容易出錯的是「覆寫」：如果新字元寫到某個寬字元的前半格或後半格，就把整個寬字元清成空白，否則會剩下半個字，整行錯位。`render()` 逐列把格子接起來（跳過佔位記號），並去掉行尾空白。

### 3.3 檢查器 align.py：三種偏移檢查

`align.py` 讀入一張圖，先用 `wcwidth` 算出每個字元的顯示欄位，再做三種檢查。它**只報告、不修改**；修正由人或 AI 依報告處理。

1. **垂直縫線（seam）**：每個 `│` 的正上方或正下方（同一欄）都必須有結構字元，例如另一個 `│`、角落、`┬┴├┤`、`▼▲`。中文被當成 1 欄時，右邊框會被推到一個「上下都接不到東西」的欄位，立刻被抓到。
2. **表格等寬（table）**：同一個方框裡的每一行，顯示寬度必須一致。檢查器以多數行的寬度為準，標出不一樣的行。
3. **折線與箭頭（kink / arrowhead）**：連線在相鄰兩行之間偏移 1 欄，而且那裡沒有轉角字元，就算折線；`▼` 必須落在下一行方框的範圍內。

拿第一節的錯誤示範去跑：

```bash
python3 scripts/align.py bad.txt
```

```plaintext
  ln  width | content
   1     9 | ┌───────┐
   2    11 | │ 開始    │
   3     9 | │ Start │
   4     9 | └───────┘
line 2: col 9: table line display width 11 differs from block width 9
line 2: col 10: '│' at display-col 10 connects to nothing vertically
```

exit code 為 1，報告直接指出第 2 行寬度 11（應為 9），以及第 10 欄的 `│` 上下都接不到東西。修好後輸出 `✓ no drift`，exit 0。

### 3.4 文件掃描 md_check.py：直接檢查整份 Markdown

修既有文件時，不需要先手動把圖剪出來：

```bash
python3 scripts/md_check.py docs/ARCH.md
```

```plaintext
docs/ARCH.md:5:9: table line display width 11 differs from block width 9
docs/ARCH.md:5:10: '│' at display-col 10 connects to nothing vertically
```

實作重點：

- **只檢查圖**：只檢查 ```` ```text ```` 與沒標語言的 code block。`json`、`bash`、`mermaid`、`plaintext` 等區塊一律略過，避免把程式碼誤判成圖。
- **依 CommonMark 規則辨識 fence**：
  - ```` ``` ```` 與 `~~~` 都算 fence，最多 3 個空白縮排（4 個以上算縮排程式碼，不是 fence）。
  - 結束 fence 必須是同一種字元，長度不得短於開頭；縮排的 fence 會從內容去掉同樣的縮排。
  - 沒有閉合的 fence 依規格延伸到檔尾，並額外回報「未閉合」。
- **行號換算**：把每個區塊在原檔的起始行號記下來，檢查結果的行號加上這個位移，回報的就是原檔行號，可以直接跳過去修。
- **只用 `\n` 切行**：Python 的 `str.splitlines()` 也會把 `\v`、U+2028 等字元當換行，行號會跟編輯器對不上，所以不用它。
- **exit code**：0 = 全部對齊；1 = 有偏移或未閉合的區塊；2 = 參數或讀檔錯誤。可以直接放進 CI 或 `test.sh`。

---

## 四、實戰：修一份架構文件的流程

我第一次用這套方法，是修一份內部架構文件的系統總覽圖。過程如下：

1. **量化問題**：`md_check.py` 報出 31 處偏移。逐行計算右邊框位置後發現，有一個方框的右邊框從第 82 欄一路歪到第 89 欄，而且每多一個中文字就多歪 1 欄，正是「用字數補空白」的典型症狀。
2. **找出隱性風險**：框內用了 `→ · ×` 等模糊寬度字元。就算欄位算對，在 ambiguous=wide 的終端機上，同一行的寬度可能差到幾十欄。
3. **重畫**：用 `canvas.py` 按原圖內容逐一放置方框。方框寬度由內容自動計算，箭頭與 `┬` 放在同一欄，框內的 `→` 改成 `->`、`×` 改成 `x`、`·` 改成 `/`；文字內容不變。
4. **驗證**：`align.py` 回報 `✓ no drift`，再用 `md_check.py` 確認整份文件 exit 0。
5. **只換圖**：寫回文件時只替換那一個 code block，用 diff 確認其他內容一字未改。

整個過程中沒有任何一個空白是用眼睛數的。

---

## 五、包成 Claude Code skill：cjk-ascii-diagram

為了讓 Claude Code 以後畫圖時自動照這套流程走，我把它包成 skill，安裝在 `~/.claude/skills/cjk-ascii-diagram/`。

### 5.1 結構

```text
cjk-ascii-diagram/
├── SKILL.md              觸發條件、流程、字元規則、輸出契約
├── LICENSE               上游 MIT 授權
├── ATTRIBUTION.md        上游來源 commit 與哪些檔案是複製的
├── skill_lifecycle.yaml
├── assets/evals/         觸發與功能測試案例
├── references/           發版證據（readiness report）
└── scripts/
    ├── align.py          檢查器（上游）
    ├── generate.py       生成器入口（上游）
    ├── canvas.py         畫布（新增）
    ├── md_check.py       Markdown 掃描（新增）
    └── ...               width.py、glyphs.py、checks_*.py、gen_*.py
```

開發與測試放在 skill 資料夾**外面**，安裝時只複製 skill 資料夾，測試不會跟著進到 `~/.claude/skills/`：

```text
cjk-ascii-diagram-skill/
├── Makefile              make build / run / test / install / clean
├── test.sh               lint + 單元 + 系統 + skill gate 的單一入口
├── cjk-ascii-diagram/    ← 要安裝的 skill
└── tests/
    ├── unit/             上游 90 個測試 + canvas + md_check
    ├── system/           以子行程跑 CLI 的端對端測試
    └── fixtures/         修正前後的架構圖
```

### 5.2 SKILL.md 的設計重點

- **觸發**：要畫或修「含中文的 ASCII 方框圖、架構圖、流程圖、表格」，或使用者說「圖沒對齊」「方框歪掉」。描述中同時放中文與英文觸發語。
- **不觸發／交棒**：要 SVG／PNG 圖片時交給 Mermaid 渲染類 skill；class／ER／state／gantt 圖直接輸出 Mermaid 原始碼，因為 ASCII 無法可靠表達這類圖。
- **流程**：確認輸入 → 修檔時先 `md_check.py` 定位 → 選生成器或畫布 → 遵守字元規則 → 驗證迴圈 → 只替換目標區塊。
- **硬規則**：未通過檢查的圖不得當成完成品交付；驗證迴圈連續 3 輪失敗就停下回報。

### 5.3 測試與驗證

| 層級 | 內容 | 結果 |
|---|---|---|
| Lint | `ruff check` 新增的腳本與測試 | 通過 |
| 單元測試 | 上游 90 個（確認複製後行為不變）、canvas 34 個、md_check 20 個 | 144 passed |
| 系統測試 | 修正前的圖要被抓出、修正後要通過；canvas 重建的圖要與修正版逐字相同；各生成器輸出接 align；執行後不留 `__pycache__` | 11 passed |
| Skill gate | skill-creator-advanced 的 format、create stage、draft release、路徑、孤兒檔案檢查 | 全部 PASS |
| 實際觸發 | 用 `claude -p` 開新 session 請它畫含中文的流程圖 | 自動載入 skill，產出的兩張圖都跑了 `align.py` 且 `✓ no drift` |

canvas 的單元測試特別涵蓋了幾個容易出錯的邊界：

- 寫到寬字元的前半格或後半格時，整個寬字元要被清掉。
- 寬字元蓋在兩個窄字元上時，兩格都要被取代。
- 控制字元、零寬字元、負座標必須被拒絕。
- `center` 置中時，左右空白不相等的話，多的那格放右邊。

### 5.4 使用方式

安裝後不用手動呼叫。直接說「畫一張 ASCII 架構圖」「這份文件的區塊圖沒對齊」，Claude Code 就會載入 skill。也可以單獨使用腳本：

```bash
S=~/.claude/skills/cjk-ascii-diagram/scripts

# 檢查文件裡的圖
python3 $S/md_check.py docs/*.md

# 生成器 + 驗證
echo '{"headers":["項目","數量"],"rows":[["茶葉","100"]]}' | python3 $S/generate.py table

# 檢查任意一張圖（stdin）
python3 $S/align.py - < diagram.txt
```

唯一的依賴是 `pip install wcwidth`。

---

## 六、限制與常見問題

**Q：檢查通過，為什麼在某台電腦上還是歪？**
有兩個可能：字型的中英寬度不是 2:1；或那台終端機開了 ambiguous=wide，而圖裡有模糊寬度字元。前者換字型解決，後者照 2.3 節的規則把框內的 `→ · ×` 等字元換掉。`align.py` 只能保證欄位數正確，管不到字型。

**Q：為什麼不全部改成 `+ - |` 純 ASCII 邊框？**
可以，這樣最保險，但沒有必要。線框字元在實務上幾乎所有終端機都當 1 欄處理；真正會出問題的是框內的 `→ · ×` 這類符號。

**Q：網頁上（GitHub、mdBook）看會對齊嗎？**
只要 code block 用等寬字型，而且字型的中文寬度剛好是英文的 2 倍，就會對齊。很多網站的等寬字型沒有中文字形，會改用系統的中文字型顯示，寬度可能不是剛好 2 倍。這是瀏覽器字型設定的問題，不是圖的問題。

**Q：時序圖（seq）為什麼不經過 align 檢查？**
時序圖是橫向箭頭穿過縱向生命線，跟 align 的「垂直縫線」模型不同，會產生誤報。上游的設計是由生成器的建構方式保證對齊，並有自己的結構測試。

**Q：很複雜的圖怎麼辦？**
節點很多、線很密的圖，ASCII 本來就不適合。建議改用 Mermaid 原始碼，需要時再附一張標明「簡化版」的 ASCII 圖。

**Q：用 `python -I` 執行時找不到 `width` 模組？**
隔離模式（`-I`）不會把腳本所在的資料夾加入 import 路徑。直接用 `python3 腳本路徑` 執行即可。

---

## 參考資料

- [kouko/monkey-skills — ascii-graph-toolkit](https://github.com/kouko/monkey-skills)：生成器與 `align.py` 的上游專案（MIT）
- [wcwidth（PyPI）](https://pypi.org/project/wcwidth/)：Python 顯示寬度計算
- [UAX #11: East Asian Width](https://www.unicode.org/reports/tr11/)：Unicode 字元寬度屬性規格
- [CommonMark Spec — Fenced code blocks](https://spec.commonmark.org/current/#fenced-code-blocks)：`md_check.py` 辨識 code fence 的依據
