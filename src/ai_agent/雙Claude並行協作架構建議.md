# 關於你的雙 Claude 並行設計

## 是的，這是並行架構

從你的描述來看：
- **Claude A（QA）**：找問題與寫測試
- **Claude B（Dev）**：修問題與優化

透過 **GitHub Issue 與 PR** 作為溝通介面，這是很聰明的設計。

---

## 協作流程推測

```text
Claude A 發現問題
    ↓
開 GitHub Issue（描述 bug + 測試案例）
    ↓
Claude B 看 Issue
    ↓
提交 PR 修復
    ↓
Claude A 跑測試驗證
    ↓
通過 -> merge；失敗 -> 重開 Issue
```

**優點：**
- Issue/PR 本身就是「規格文件」
- 有 Git history 可追溯
- 測試結果可直接在 CI 上執行

---

## 本機實作建議

既然你問「實用性方法」，我給你幾個選項：

### 方案 1：檔案系統（最簡單）

```text
project/
├── .ai-workspace/
│   ├── issues/          # Claude A 寫的 issue
│   │   └── issue-001.md
│   ├── fixes/           # Claude B 的修復
│   │   └── fix-001.diff
│   └── tests/           # 測試結果
│       └── test-001.log
```

**實作方式：**
- Claude A 寫 Markdown issue
- Claude B 讀 issue，產生 diff/patch
- 用 file watcher 觸發彼此的工作

### 方案 2：SQLite（結構化）

```sql
CREATE TABLE issues (
    id INTEGER PRIMARY KEY,
    description TEXT,
    test_code TEXT,
    status TEXT,  -- open/in_progress/closed
    created_by TEXT  -- claude_a/claude_b
);

CREATE TABLE fixes (
    id INTEGER PRIMARY KEY,
    issue_id INTEGER,
    diff TEXT,
    test_result TEXT
);
```

**優點：**
- 可查詢、統計
- 支援複雜狀態機

### 方案 3：Git-based（最像 GitHub）

```bash
# Claude A
git checkout -b qa/issue-001
echo "測試案例" > tests/test_001.py
git commit -m "Found: XSS vulnerability"

# Claude B
git checkout -b fix/issue-001
# 修改程式碼
git commit -m "Fix: sanitize user input"

# Merge via git merge
```

**優點：**
- 完全模擬真實開發流程
- 可用 git hooks 自動化

---

## 我會選方案 3

因為：
1. **Git 本身就是協作協議**：不用重新發明輪子
2. **Commit message 是溝通介面**：Claude 讀得懂
3. **Branch 是工作隔離**：不會互相干擾
4. **可直接接上真 GitHub**：未來擴展容易

---

## 實作範例（Pseudo）

```python
# Claude A (QA Agent)
class QAAgent:
    def scan_code(self):
        issues = self.find_bugs()
        for issue in issues:
            branch = f"qa/issue-{issue.id}"
            self.git.checkout(branch, create=True)
            self.write_test(issue)
            self.git.commit(f"Test: {issue.title}")

# Claude B (Dev Agent)
class DevAgent:
    def fix_issues(self):
        qa_branches = self.git.branches(pattern="qa/*")
        for branch in qa_branches:
            issue = self.parse_issue(branch)
            fix_branch = f"fix/{issue.id}"
            self.git.checkout(fix_branch, create=True)
            self.apply_fix(issue)
            self.git.commit(f"Fix: {issue.title}")
            self.run_tests()  # 跑 Claude A 寫的測試
```

---

## 關鍵問題

你提到「跑了一天一夜」，這表示：
1. **需要 Rate Limiting**：避免 API 被打爆
2. **需要 State Management**：記住誰在做什麼
3. **需要 Conflict Resolution**：兩個 Claude 改同一行怎麼辦？

---

## 你的「左右互搏術」很妙

但要注意：
- **成本**：兩個 Claude 同時跑，API 費用約 x2
- **收斂性**：會不會無限循環？（A 說有 bug -> B 修 -> A 又說有 bug）
- **優先級**：該先修哪個 bug？

可以加一個「仲裁者 Claude C」專門決定優先級。

---

## 建議升級：A/B 並行 + Coordinator（必要）

如果要穩定跑長時間，建議最小升級成 3 角色：
- `Claude A (QA)`：只負責產生可重現測試與驗收條件
- `Claude B (Dev)`：只負責修復與提交 patch
- `Coordinator`：只負責排程、鎖定、合併策略、停止條件

這樣可以避免 A/B 互相覆蓋與無限循環。

---

## 任務狀態機（避免鬼打牆）

```text
OPEN
  -> QA_READY        (A 已提交 failing test)
  -> DEV_WORKING     (B 已領取任務)
  -> DEV_READY       (B 已提交 fix + 本地測試)
  -> QA_VERIFYING    (A 驗證中)
  -> DONE            (驗證通過)
  -> REOPENED        (驗證失敗，附新證據)
  -> BLOCKED         (衝突/依賴缺失/超時)
```

規則：
- `REOPENED` 最多 2 次，超過直接進 `BLOCKED` 交給 C
- 每個 issue 設定 `max_iterations=3`
- 單任務 TTL（例如 30 分鐘），超時回收

---

## 衝突處理策略（同檔同區塊修改）

採用「先測試、後合併、再重放」：
1. A 的測試分支先 merge 到整合分支
2. B 的修復分支 rebase 到整合分支最新
3. 若衝突：
   - 同檔同函式：交給 C 做一次性裁決
   - 不同函式：自動合併
4. 合併後固定跑：
   - 目標測試（A 提交的測試）
   - 快速 smoke test

---

## 最小資料結構（JSON）

```json
{
  "issue_id": "ISSUE-042",
  "title": "xss in comment preview",
  "priority": "high",
  "owner": "claude_b",
  "status": "DEV_WORKING",
  "qa_branch": "qa/ISSUE-042",
  "dev_branch": "fix/ISSUE-042",
  "acceptance": [
    "test_xss_preview fails before fix",
    "test_xss_preview passes after fix"
  ],
  "iterations": 1,
  "ttl_minutes": 30
}
```

---

## 可直接落地的目錄

```text
.ai-orchestrator/
├── queue/
│   ├── open/
│   ├── working/
│   ├── verify/
│   └── done/
├── locks/
│   └── ISSUE-042.lock
├── logs/
│   ├── qa.log
│   ├── dev.log
│   └── coordinator.log
└── state/
    └── ISSUE-042.json
```

---

## Coordinator 核心守則（精簡版）

- 一次只允許一個 agent 持有同一個 `issue lock`
- 若 `test baseline` 改變，強制重新驗證所有 `DEV_READY`
- 每輪只放行 `Top-N` 高優先級 issue（避免 token 爆量）
- 每日預算上限：
  - token budget
  - API cost budget
  - max active issues

---

## 你可直接補資料的區塊模板

把你後續要給我的內容直接填在這裡，我可再幫你轉成流程與腳本：

```markdown
### 專案背景
- 

### 目前技術棧
- 

### 已知痛點
- 

### 必要限制（成本/時間/模型配額）
- 

### 你想優先自動化的 3 件事
1. 
2. 
3. 
```

---

## 開源專案候選（多 Agent 協作）

> 註：星數與活躍度會變動，以下以「架構匹配度」為主。

| 專案名稱 | 連結 | 核心特色 | 對應你的場景 |
|---|---|---|---|
| MetaGPT | https://github.com/geekan/MetaGPT | 多角色軟體公司流程（PM/Architect/Engineer），可輸出文件與程式碼，適合 SOP 化協作 | 可映射 `Claude A(QA)` / `Claude B(Dev)`，並由 Coordinator 控管流程 |
| ChatDev | https://github.com/OpenBMB/ChatDev | 角色對話式開發（CEO/CTO/Programmer/Reviewer/Tester），支援分階段協作 | 適合做「QA 產測試 -> Dev 修復 -> QA 驗證」回圈 |
| PR-Agent | https://github.com/qodo-ai/pr-agent | 針對 PR 的自動審查、摘要與建議，整合 GitHub 流程 | 可作為 B 提交後的自動審核層，補強 QA Gate |

---

## 導入順序建議（最小風險）

1. 先上 `MetaGPT` 做單一 repo PoC，只開 1 條 issue 流水線驗證可行性。
2. 加入 `PR-Agent` 接在 PR 階段，讓審查標準固定化。
3. 需要更多角色對話時再引入 `ChatDev`，避免初期系統過重。

---

## 與 A/B/Coordinator 的映射

- `Claude A (QA)`：
  - 產 failing tests
  - 定義 acceptance criteria
  - 驗證 `DEV_READY`
- `Claude B (Dev)`：
  - 依 issue 與測試修復
  - 提交 fix branch / PR
- `Coordinator`：
  - 控 `lock`、TTL、重試次數
  - 決定 merge 順序與優先級
  - 超過迭代上限時標記 `BLOCKED`

---

## 快速啟動原則（避免跑一天一夜）

- 限制並行數：`max_active_issues = 3`
- 限制迭代數：`max_iterations = 3`
- 限制驗證時間：`ttl_minutes = 30`
- 固定節流：每輪 agent 呼叫加入延遲（rate limit）
- 預算硬上限：token / cost / 日任務數超限即停
