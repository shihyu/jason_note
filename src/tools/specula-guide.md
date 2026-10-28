# Specula：安裝、使用與相關工具

> 查核日期：2026-10-28。本文以 [Specula 官方專案](https://github.com/specula-org/Specula) 的 README、[Usage Guide](https://github.com/specula-org/Specula/blob/main/docs/Usage.md) 和本地 1.2.0 原始碼為依據。指令與支援範圍可能隨版本改變，實際操作前可再執行 `specula --help`、`specula run --help`。

## Specula 是什麼？

Specula 是針對**並行與分散式系統程式碼**找深層錯誤的工具。它讓程式代理閱讀目標程式碼，建立描述系統行為與正確性條件的 TLA+ 模型，再用模型檢查器搜尋違反條件的執行路徑；找到候選問題後，還會嘗試用實際程式碼與測試環境重現。它適合檢查共識協定、狀態同步、併發控制、故障恢復等容易出現交錯執行錯誤的程式。[來源：Specula README](https://github.com/specula-org/Specula#readme)

流程可簡化為：

```text
目標程式碼 → 分析與建模 → TLA+ 規格 → 產生執行 trace 的 harness
           → trace 驗證與 TLC 模型檢查 → 程式碼層確認 → 嚴重度報告
```

這個流程結合抽象模型與程式碼驗證。**模型檢查通過不等於整份程式碼已被證明正確**：結果仍取決於建模範圍、抽象方式、檢查設定，以及 harness 能否呈現真實行為。候選錯誤也應閱讀重現證據，而非只看模型反例。[來源：Specula 論文](https://arxiv.org/abs/2607.25333)

## 安裝前準備

| 必要項目 | 用途 |
| --- | --- |
| Python 3.10+，含 `pip`、`venv` | CLI 與 MCP 工具環境 |
| [uv](https://docs.astral.sh/uv/) | 安裝 `specula` 命令 |
| JDK 21+、Maven | TLA+ 檢查工具與 CFA 工具建置 |
| Git、Bash、`curl` 或 `wget` | 原始碼操作與初次下載 |
| [GitHub CLI (`gh`)](https://cli.github.com/) | 儲存庫及 issue 研究 |
| 一種受支援的代理 CLI | 執行分析流程，例如 Claude Code、Codex、Copilot CLI、OpenCode 或 Pi |
| 目標專案自己的建置與測試依賴 | 產生 harness 和重現錯誤 |

`specula setup` **不會安裝**上表的系統依賴或代理 CLI。初次設定需能連到 GitHub、PyPI、Maven Central；代理執行時還需模型供應商的帳號或憑證。官方建議至少 32 GB RAM 與 100 GB 可用磁碟空間；模型檢查可能需要大量時間與記憶體。[來源：Specula Usage Guide](https://github.com/specula-org/Specula/blob/main/docs/Usage.md#getting-started)

支援 Linux、macOS，以及在 **WSL2 內**執行的 Windows。macOS 還需 GNU coreutils，並將 `gnubin` 放進 `PATH`；Windows 原生終端目前不是官方支援的執行環境。[來源：平台需求](https://github.com/specula-org/Specula/blob/main/docs/Usage.md#supported-platforms)

### 安裝 Specula

先自行安裝上述依賴與一種代理 CLI，接著執行：

```bash
git clone https://github.com/specula-org/Specula.git
cd Specula
uv tool install -e .
specula setup
specula --help
```

這裡的 `-e` 很重要：`specula` 命令會呼叫儲存庫內的腳本，所以安裝後要保留該 checkout。`specula setup` 會下載 TLA+ JAR、建置 CFA 工具、建立 MCP 工具環境，並詢問是否整合偵測到的代理。它不會執行完整的目標專案分析。[來源：安裝說明](https://github.com/specula-org/Specula/blob/main/docs/Usage.md#requirements)

若使用 Codex，設定畫面可選 `y`（分別安裝 skills 與 MCP）或 `plugin`（安裝 `specula-codex@specula`）。Plugin 會作用於目前 Codex profile，可供該 profile 下各專案使用；這是設定時要留意的範圍。[來源：Codex 設定](https://github.com/specula-org/Specula/blob/main/docs/Usage.md#requirements)

## 第一次執行

在 **Specula checkout 根目錄**執行，將 `/absolute/path/to/source` 換成已能正常建置的目標儲存庫絕對路徑：

```bash
specula run \
  --agent=codex \
  --artifact=/absolute/path/to/source \
  --keep-original \
  "mysys|owner/repository|Go|系統設計或參考演算法"
```

`--agent=codex` 可改為 `claude-code`、`copilot-cli`、`opencode` 或 `pi`；若省略，預設使用 `claude-code`。最後的引號內依序是**輸出名稱、GitHub 儲存庫、主要語言、參考設計**，必須加引號，否則 `|` 會被 shell 當作管線。`--artifact` 指向要分析的原始碼。[來源：First run](https://github.com/specula-org/Specula/blob/main/docs/Usage.md#first-run)

`--keep-original` 會在私有副本中分析，保留原 checkout，並輸出可審閱的 `changes.patch`。若不加這個選項，harness 或重現工作**可能直接修改** `--artifact` 指向的原始碼。首次探索建議使用私有副本。[來源：Output Structure](https://github.com/specula-org/Specula/blob/main/docs/Usage.md#output-structure)

需要把分析集中在特定模組或情境時，可先參考[建模指引範本](https://github.com/specula-org/Specula/blob/main/docs/modeling-guidance-template.md)，再加上 `--guidance=/absolute/path/to/guidance.md`。這個檔案是建議項，不是安裝必要條件。[來源：First run](https://github.com/specula-org/Specula/blob/main/docs/Usage.md#first-run)

### 結果在哪裡？

預設隔離模式把產物放在 Specula checkout 的 `runs/<run-id>/`；`runs/latest` 指向最新執行。先看：

1. `runs/latest/pipeline-summary.md`：整體狀態。
2. `runs/latest/index.md`：選擇目標並進入個別報告。
3. 目標的 `.specula-output/index.md`：摘要、確認結果、嚴重度及技術細節。
4. `pipeline.log`：流程出錯時的日誌；使用 `--keep-original` 時再查看 `changes.patch`。

候選問題應逐一確認其重現結果與環境限制，不能把所有模型反例直接視為已證實的程式錯誤。[來源：輸出結構](https://github.com/specula-org/Specula/blob/main/docs/Usage.md#output-structure)

### 進階用法

| 情境 | 命令或入口 | 說明 |
| --- | --- | --- |
| 已有 TLA+ 模型 | `specula run --byom=/absolute/path/to/model-or-assets --artifact=/absolute/path/to/source "mysys|owner/repository|Go|reference"` | 匯入模型或 trace 等既有資產；參閱 [BYOM](https://github.com/specula-org/Specula/blob/main/docs/Usage.md#bring-your-own-model-byom) |
| 建立持續驗證基線 | `specula run --ci-init --ci-dir=/work/mysys-ci --artifact=/absolute/path/to/source "mysys|owner/repository|Go|reference"` | 將 CI 資料夾放在目標 checkout 外；參閱 [CI 指南](https://github.com/specula-org/Specula/blob/main/docs/Usage.md#add-specula-to-ci) |
| 檢查後續程式碼變更 | `specula run --incremental --ci-dir=/work/mysys-ci` | 使用上述基線檢查新版本 |
| 手動控制每個階段 | `code-analysis → spec-generation → harness-generation → validation-workflow → bug-confirmation` | 在代理中依序呼叫 skills；參閱 [Interactive Mode](https://github.com/specula-org/Specula#interactive-mode) |

## 相關工具怎麼選？

| 工具 | 主要用途 | 與 Specula 的關係 |
| --- | --- | --- |
| [TLA+ / TLC](https://lamport.azurewebsites.net/tla/tools.html) | 手寫 TLA+ 模型，用 TLC 檢查狀態空間 | Specula 以 TLA+ 與 TLC 為核心，額外串接代理、trace 與程式碼重現 |
| [TLA+ Toolbox / PlusCal](https://lamport.azurewebsites.net/tla/toolbox.html) | 編輯規格、把 PlusCal 演算法翻譯成 TLA+、查看 TLC 反例 | 適合手動建模、學習及審查 Specula 產生的模型 |
| [Apalache](https://apalache-mc.org/) | 使用 SMT 求解器對 TLA+ 模型做符號式、有限步數等檢查 | 可補充 TLC 的檢查視角；有限步數未找到反例不代表所有長度都安全 |
| [SPIN](https://spinroot.com/spin/whatispin.html) | 以 Promela 描述並行系統並進行模型檢查 | 同類形式驗證工具，但模型語言與工具鏈不同 |
| [Alloy](https://alloytools.org/) | 以 Alloy 語言建模並搜尋符合或違反約束的實例 | 適合研究結構關係與小範圍行為；需另寫 Alloy 模型 |
| [Jepsen](https://jepsen.io/analyses) | 對真實分散式系統施加故障並檢查操作歷史 | 偏向黑箱整合測試，可補足抽象模型與真實部署之間的落差 |

這些工具不保證可直接讀取彼此的模型。若重點是快速分析**既有程式碼**並追蹤模型反例到實作，可先試 Specula；若要完全控制規格與檢查設定，可先從 TLA+ / TLC 或其他模型檢查器開始。Jepsen 適合驗證真實叢集在故障條件下的外部行為。[來源：Specula](https://github.com/specula-org/Specula)、[TLA+](https://lamport.azurewebsites.net/tla/tla.html)、[Jepsen](https://jepsen.io/analyses)

## 常見問題

**找不到 `specula` 命令？** 確認 `uv tool install -e .` 已在 Specula checkout 執行，且 uv 的工具命令目錄位於 `PATH`。可先查 `uv tool list` 與 `specula --help`。[uv 官方文件](https://docs.astral.sh/uv/concepts/tools/)

**`specula setup` 後仍不能跑？** 先確認 Python、Java、Maven、`gh`、代理 CLI 與目標專案工具鏈都能執行；`setup` 不負責安裝這些依賴。[需求清單](https://github.com/specula-org/Specula/blob/main/docs/Usage.md#requirements)

**模型檢查很慢或記憶體不足？** 先縮小建模範圍，檢查磁碟及 JVM 記憶體設定；進階參數見 `specula run --help` 與[資源說明](https://github.com/specula-org/Specula/blob/main/docs/Usage.md#output-structure)。

**可以只用其中一段流程嗎？** 可以。CLI 提供 `analyze`、`specgen`、`harness`、`validate`、`confirm`、`classify` 等分段命令；詳細輸入輸出見 [Individual Steps](https://github.com/specula-org/Specula/blob/main/docs/Usage.md#individual-steps)。

## 參考資料

- [Specula 原始碼與 README](https://github.com/specula-org/Specula)
- [Specula Usage Guide](https://github.com/specula-org/Specula/blob/main/docs/Usage.md)
- [Specula 論文](https://arxiv.org/abs/2607.25333)
- [TLA+ 工具](https://lamport.azurewebsites.net/tla/tools.html)、[Apalache](https://apalache-mc.org/)、[SPIN](https://spinroot.com/spin/whatispin.html)、[Alloy](https://alloytools.org/)、[Jepsen](https://jepsen.io/)
