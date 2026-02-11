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
