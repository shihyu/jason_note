# Claude／OpenCode Skills 新手超詳細講解與知識整理

作為剛接觸 Claude 和 OpenCode 的技術新手，不用被文中的專業詞彙嚇到。這篇內容會把 Skills 的核心知識拆成「白話解釋 + 步驟化操作 + 核心差異」，盡量避開複雜術語，讓你快速理解 Skills 是什麼、怎麼用、能帶來什麼價值。

## 一、先搞懂：Skills 到底是什麼？

### 白話版本

Skills 是 Anthropic 在 2025 年推出並逐步開放的功能。簡單來說，它就是給 AI 智能體（Agent）使用的「可重複使用技能包」。你可以把它想成裝在 Claude 或 OpenCode 裡的一組專用工具，裝好之後，AI 就能依照固定流程完成特定任務，不需要你每次都重新教一次。

### 簡單定義

它把流程性的工作知識，例如「怎麼蒐集熱門話題做選題」或「怎麼把 GitHub 專案打包成可直接使用的工具」，封裝成一個資料夾，而不只是單純一段提示詞。當 AI 需要時，可以自行載入並執行，核心價值就在於可重用與自動化。

### 關鍵特點

1. Skills 是資料夾，不是單純文字，裡面可以放指令、腳本、模板與參考資料。
2. 它可以搭配 Claude Code、OpenCode，也常見於其他 AI 編程工作流。
3. 通常用自然語言觸發，例如「開始今日選題生成」。
4. 能減少重複塞入大量上下文，節省 Token，也降低長對話中 AI 失焦的機率。

## 二、最容易懂的類比：Skills、Prompt、MCP 有什麼不同？

把 AI 智能體想成剛入職的實習生，三者差異就很好懂：

| 名稱 | 類比 | 核心作用 | 特點 | 適合情境 |
| --- | --- | --- | --- | --- |
| Prompt | 你站在實習生旁邊，當場口頭交代任務 | 給 AI 臨時、一次性的指令 | 只在當前對話有效，用完就結束 | 偶爾才做一次的小任務，例如改語氣、寫開頭 |
| Skills | 給實習生一本公司內部 SOP 操作手冊 | 給 AI 可重複使用的固定工作流程 | 能長期重用，按需載入 | 重複性工作，例如每日選題、專案打包 |
| MCP | 給實習生一張公司倉庫門禁卡 | 讓 AI 安全連接外部系統或工具 | 負責開權限，不負責教流程 | 需要操作 GitHub、表單、資料庫等外部工具時 |

### 一句話記住差別

- Prompt：臨時教一次，用完就忘。
- Skills：一次整理好，之後反覆使用。
- MCP：提供權限，讓 AI 能接觸外部系統。

## 三、Skills 能做什麼？看兩個實際案例

### 案例 1：AI 選題系統

#### 痛點

以前找選題要手動刷微博、知乎、GitHub 等多個平台，再從中整理熱門事件、切入角度與標題。整個流程可能每天花上 2 到 3 小時。

#### 用 Skills 的做法

建立 1 個總控 Agent，加上 3 個 Skills。你只要說一句「開始今日選題生成」，AI 就能自動完成：

1. 熱點蒐集 Skill：抓取多個平台的最新科技熱點。
2. 選題生成 Skill：依照資訊密度、討論度等標準，篩出可用題目。
3. 選題審核 Skill：檢查是否符合方法論，不合格就退回重做。

#### 結果

原本要花 2 到 3 小時的工作，可能在幾分鐘內完成，還能自動反覆優化。

### 案例 2：整合包生成器

#### 痛點

GitHub 上很多優秀開源專案沒有圖形介面，還需要安裝環境與相依套件。對不熟程式的人來說，門檻很高。

#### 用 Skills 的做法

建立一個整合包生成器 Skill。你只要把 GitHub 專案連結丟給 AI，並說「幫我把這個專案做成整合包」，它就能自動處理：

1. 自動 clone GitHub 倉庫，辨識專案類型並解析相依套件。
2. 自動產生前端介面，例如 Gradio WebUI。
3. 打包成解壓即用的 ZIP，附上啟動腳本與自動安裝流程。
4. 出錯時可依錯誤日誌持續修正。

#### 結果

不懂環境配置的使用者，也能更快使用原本難以上手的開源專案。

### 核心價值

Skills 最適合處理「重複、固定流程、可標準化」的工作，把機械性流程交給 AI，自動化後能省下大量時間。

## 四、Skills 的基本結構

Skills 的本質是一個資料夾。剛開始不一定要自己寫，但要先知道基本規則。

### 1. 資料夾命名規則

資料夾名稱必須使用全小寫加連字號，例如：

```text
hotspot-collector
repo-packager
```

### 2. 核心檔案

一個 Skill 資料夾中，只有 `SKILL.md` 是必要檔案，其他通常都是可選：

- 必要檔案：`SKILL.md`
- 可選檔案：`scripts/`、`templates/`、`README.md` 等

### 3. `SKILL.md` 的固定結構

`SKILL.md` 通常分成兩個部分。

#### 第一部分：YAML 頭部

用 `---` 包住，記錄技能名稱與描述。通常至少包含：

- `name`
- `description`

描述最好直接說明技能何時觸發、會做什麼。

```yaml
---
name: repo-packager
description: 分析 GitHub 上的 Python 專案，產生 Gradio WebUI，並在使用者提供 GitHub URL 且提到打包或部署時觸發。
---
```

#### 第二部分：Markdown 主體

通常包含：

- `Instructions`：技能執行步驟
- `Examples`：實際輸入與輸出範例

例如：

```md
## Instructions

1. Clone repository.
2. Detect dependencies.
3. Generate UI wrapper.
4. Build portable package.

## Examples

Input: `https://github.com/example/project`
Output: Portable ZIP package with launcher scripts.
```

### 補充

一般會建議 `SKILL.md` 不要寫得過長，避免 AI 在載入時負擔過大。

## 五、新手最實用：Skills 的取得、安裝與使用方式

如果你剛入門，完全不需要從零開始自己寫。先用現成的 Skills 最有效率。

### 第一步：取得現成 Skills

Anthropic 在 GitHub 上公開了不少實用 Skills，可以直接參考：

- <https://github.com/anthropics/skills>

### 官方常見 Skills

- `docx`
- `frontend-design`
- `pdf`
- `skill-creator`
- `xlsx`

其中 `skill-creator` 很重要，因為它本身就是用來生成其他 Skills 的 Skill。

### 第二步：安裝 Skills

以下以 Claude Code 或 OpenCode 這類工具的常見用法來看。

#### 方法 1：讓 AI 協助安裝

直接輸入類似以下內容：

```text
安裝這個 skill，skill 專案地址為：
https://github.com/anthropics/skills/tree/main/skills/skill-creator
```

如果你要安裝其他 Skill，只要把 URL 換掉即可，例如：

```text
https://github.com/anthropics/skills/tree/main/skills/xlsx
```

#### 方法 2：手動安裝

1. 建立對應的技能目錄。
2. 從 GitHub 下載對應 Skill 資料夾。
3. 將資料夾重新命名為全小寫加連字號格式。
4. 放到工具指定的 Skills 路徑。

常見路徑示意：

```text
Claude Code: ~/.claude/skills
OpenCode: ~/.config/opencode/skill
```

有些工具需要重新啟動後才會重新掃描 Skills。

### 第三步：使用 Skills

安裝完成後，通常不需要記額外命令，直接用自然語言描述需求即可。

例如：

```text
幫我把這個 GitHub 專案做成整合包：
https://github.com/example/project
```

常見使用流程：

1. 打開 Claude Code 或 OpenCode。
2. 輸入帶有需求與關鍵詞的自然語言。
3. 如有需要，先讓 AI 用 Plan 模式規劃步驟。
4. 確認後再執行。

### 小技巧

如果 Skills 放在全域目錄，之後你在任何專案資料夾中開啟工具，都比較容易直接重用。

## 六、Skills 的核心設計原則：漸進式揭露

漸進式揭露的概念，是讓 AI 不要一開始就讀入所有內容，而是依需求分階段載入。

### 白話理解

就像你在手機 App 中不會一打開就看到全部設定，而是先進主選單，再逐步打開細節頁。

### 對 AI 的作用

當 AI 使用 Skills 時，常見流程是：

1. 先讀取技能的基本資訊，判斷這個 Skill 是否適用。
2. 需要時再載入完整的 `SKILL.md`。
3. 若還不夠，再讀取腳本、模板或參考資料。

### 帶來的好處

- 減少上下文負擔。
- 降低出錯機率。
- 節省 Token。

## 七、新手學 Skills 的建議路線

### 入門階段：先學會用

1. 先安裝 Anthropic 官方的現成 Skills。
2. 優先熟悉 `skill-creator`。
3. 用自然語言實際操作 `xlsx`、`pdf` 等技能，先感受流程自動化。

### 進階階段：開始生成自己的 Skills

可以直接讓 AI 幫你產生專屬 Skill，例如：

```text
幫我做一個可以把網址整理成摘要的 Skill。
```

產出的內容通常會包含：

- `SKILL.md`
- 對應資料夾結構
- 可能需要的模板或腳本

之後你再依自己的需求微調觸發條件與步驟即可。

### 高階階段：把自己的工作流封裝起來

當你已經有穩定且反覆使用的工作流程，就很適合封裝成專屬 Skills，例如：

- 自媒體排版 Skill
- 資料分析 Skill
- 專案打包 Skill

## 八、核心知識速記

1. Skills 是給 AI 使用的可重複利用技能包。
2. 它的形式通常是資料夾，必要檔案是 `SKILL.md`。
3. Prompt 是臨時指令，Skills 是可重複調用的流程封裝。
4. MCP 主要負責外部系統權限，不等於 Skills。
5. 新手最有效率的做法，是先裝現成 Skills，再逐步學會生成自己的版本。
6. Skills 最有價值的地方，在於把重複流程交給 AI 自動完成。

## 備註

本文為學習整理筆記，非原創內容。
