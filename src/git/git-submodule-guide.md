# Git Submodule 完整使用指南

本指南說明如何在你的 GitHub repo 中引用其他 repo（如 `anthropics/claude-plugins-official`），並持續追蹤最新版本。

---

## 📋 目錄

- [什麼是 Git Submodule](#什麼是-git-submodule)
- [初始設定步驟](#初始設定步驟)
- [日常使用](#日常使用)
- [自動化更新（GitHub Actions）](#自動化更新github-actions)
- [團隊協作](#團隊協作)
- [常見問題](#常見問題)
- [進階技巧](#進階技巧)

---

## 什麼是 Git Submodule

Git Submodule 允許你在一個 Git repo 中引用另一個 Git repo，同時保持它們的獨立性。

**使用情境：**
- 追蹤第三方專案的最新版本
- 重用共享的程式庫或組件
- 在主專案中整合外部依賴

**優點：**
- ✅ 保持原始 repo 完整性
- ✅ 可以鎖定特定版本
- ✅ 容易更新到最新版本
- ✅ 支援多個 submodule

---

## 初始設定步驟

### 1. 在你的 repo 中添加 Submodule

```bash
# 進入你的 repo 目錄
cd your-repo

# 添加 submodule
git submodule add https://github.com/anthropics/claude-plugins-official

# 或指定自訂目錄名稱
git submodule add https://github.com/anthropics/claude-plugins-official plugins

# 提交變更
git add .
git commit -m "Add claude-plugins-official as submodule"
git push
```

### 2. 驗證設定

執行後會產生：
- `.gitmodules` 檔案（記錄 submodule 資訊）
- `claude-plugins-official/` 目錄（submodule 內容）

查看 `.gitmodules` 內容：
```bash
cat .gitmodules
```

應該看到類似：
```ini
[submodule "claude-plugins-official"]
	path = claude-plugins-official
	url = https://github.com/anthropics/claude-plugins-official
```

---

## 日常使用

### 更新 Submodule 到最新版本

```bash
# 方法 1：更新所有 submodules
git submodule update --remote

# 方法 2：更新特定 submodule
git submodule update --remote claude-plugins-official

# 提交更新
git add claude-plugins-official
git commit -m "Update claude-plugins-official to latest version"
git push
```

### 檢查 Submodule 狀態

```bash
# 查看 submodule 當前版本
git submodule status

# 查看 submodule 的變更
cd claude-plugins-official
git log --oneline -5  # 查看最近 5 個 commit
cd ..
```

### Clone 包含 Submodule 的 Repo

**方法 1：一次完成**
```bash
git clone --recursive https://github.com/your-username/your-repo
```

**方法 2：分步驟**
```bash
# 先 clone 主 repo
git clone https://github.com/your-username/your-repo
cd your-repo

# 初始化並更新 submodule
git submodule init
git submodule update
```

**方法 3：簡化版**
```bash
git clone https://github.com/your-username/your-repo
cd your-repo
git submodule update --init --recursive
```

---

## 自動化更新（GitHub Actions）

創建 `.github/workflows/update-submodules.yml` 來自動檢查並更新 submodule。

### 基礎版本（每日檢查）

```yaml
name: Update Submodules

on:
  schedule:
    # 每天 UTC 00:00 執行（台灣時間上午 8:00）
    - cron: '0 0 * * *'
  workflow_dispatch:  # 允許手動觸發

jobs:
  update:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          submodules: recursive
          token: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Update submodules
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git submodule update --remote --merge
      
      - name: Commit changes
        run: |
          git add .
          if git diff --staged --quiet; then
            echo "No changes to commit"
          else
            git commit -m "chore: update submodules to latest version"
            git push
          fi
```

### 進階版本（帶通知和分析）

```yaml
name: Update and Analyze Submodules

on:
  schedule:
    - cron: '0 0 * * *'
  workflow_dispatch:

jobs:
  update:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          submodules: recursive
          token: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Get current submodule version
        id: before
        run: |
          cd claude-plugins-official
          echo "version=$(git rev-parse HEAD)" >> $GITHUB_OUTPUT
          cd ..
      
      - name: Update submodules
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git submodule update --remote --merge
      
      - name: Get new submodule version
        id: after
        run: |
          cd claude-plugins-official
          echo "version=$(git rev-parse HEAD)" >> $GITHUB_OUTPUT
          cd ..
      
      - name: Generate changelog
        if: steps.before.outputs.version != steps.after.outputs.version
        run: |
          cd claude-plugins-official
          echo "## 更新摘要" > ../SUBMODULE_CHANGES.md
          echo "" >> ../SUBMODULE_CHANGES.md
          echo "從 ${{ steps.before.outputs.version }} 更新到 ${{ steps.after.outputs.version }}" >> ../SUBMODULE_CHANGES.md
          echo "" >> ../SUBMODULE_CHANGES.md
          echo "### 變更內容" >> ../SUBMODULE_CHANGES.md
          git log --oneline ${{ steps.before.outputs.version }}..${{ steps.after.outputs.version }} >> ../SUBMODULE_CHANGES.md
          cd ..
      
      - name: Commit changes
        run: |
          git add .
          if git diff --staged --quiet; then
            echo "No changes to commit"
          else
            git commit -m "chore: update claude-plugins-official submodule

$(cat SUBMODULE_CHANGES.md)"
            git push
          fi
      
      - name: Create issue for updates
        if: steps.before.outputs.version != steps.after.outputs.version
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const changes = fs.readFileSync('SUBMODULE_CHANGES.md', 'utf8');
            
            github.rest.issues.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              title: '📦 Submodule 已更新：claude-plugins-official',
              body: changes,
              labels: ['submodule-update', 'automated']
            });
```

---

## 團隊協作

### 團隊成員首次設定

```bash
# Clone repo
git clone --recursive https://github.com/your-username/your-repo
cd your-repo

# 如果忘記加 --recursive，補救方法：
git submodule update --init --recursive
```

### 同步其他人的更新

```bash
# Pull 主 repo 的更新
git pull

# 更新 submodule
git submodule update --init --recursive
```

### 設定別名（簡化指令）

在 `~/.gitconfig` 或專案的 `.git/config` 中加入：

```ini
[alias]
    supdate = submodule update --remote --merge
    spull = !git pull && git submodule update --init --recursive
    spush = !git push && git submodule foreach git push
```

使用方式：
```bash
git supdate    # 更新 submodule
git spull      # Pull 並更新 submodule
```

---

## 常見問題

### Q1: 如何移除 Submodule？

```bash
# 1. 刪除 .gitmodules 中的相關條目
git config -f .gitmodules --remove-section submodule.claude-plugins-official

# 2. 刪除 .git/config 中的相關條目
git config -f .git/config --remove-section submodule.claude-plugins-official

# 3. 移除目錄和快取
git rm --cached claude-plugins-official
rm -rf claude-plugins-official
rm -rf .git/modules/claude-plugins-official

# 4. 提交變更
git add .
git commit -m "Remove claude-plugins-official submodule"
```

### Q2: Submodule 顯示 "detached HEAD" 狀態？

這是正常的！Submodule 預設會指向特定的 commit，而不是分支。

如果想切換到分支：
```bash
cd claude-plugins-official
git checkout main
cd ..
```

### Q3: 如何鎖定 Submodule 版本？

```bash
cd claude-plugins-official
git checkout <specific-commit-hash>
cd ..
git add claude-plugins-official
git commit -m "Lock submodule to specific version"
```

### Q4: Pull 時 Submodule 沒有自動更新？

需要手動執行：
```bash
git submodule update --init --recursive
```

或設定自動更新：
```bash
git config submodule.recurse true
```

---

## 進階技巧

### 1. 建議的專案結構

```
your-repo/
├── .github/
│   └── workflows/
│       └── update-submodules.yml    # 自動更新
├── claude-plugins-official/          # submodule
├── docs/
│   ├── analysis/                     # 你的分析文件
│   │   ├── features-overview.md
│   │   ├── changes-log.md
│   │   └── usage-examples.md
│   └── README.md
├── scripts/
│   └── analyze-plugins.sh            # 分析腳本
├── .gitmodules                       # submodule 設定
└── README.md
```

### 2. 建立分析腳本

創建 `scripts/analyze-plugins.sh`：

```bash
#!/bin/bash

# 分析 claude-plugins-official 的變更

echo "=== Claude Plugins 分析 ==="
echo ""

cd claude-plugins-official

# 顯示最新 10 個 commits
echo "## 最近更新"
git log --oneline -10

echo ""
echo "## 檔案統計"
find . -name "*.py" | wc -l | xargs echo "Python 檔案數量:"
find . -name "*.md" | wc -l | xargs echo "Markdown 檔案數量:"

echo ""
echo "## 目錄結構"
tree -L 2 -I '.git'

cd ..
```

### 3. 設定 Pre-commit Hook

創建 `.git/hooks/pre-commit`：

```bash
#!/bin/bash

# 檢查 submodule 狀態
if git submodule status | grep -q '^+'; then
    echo "警告: Submodule 有未提交的變更"
    git submodule status
    exit 1
fi
```

### 4. 多個 Submodules 管理

```bash
# 添加多個 submodules
git submodule add https://github.com/user/repo1 external/repo1
git submodule add https://github.com/user/repo2 external/repo2

# 批次更新所有 submodules
git submodule update --remote --merge

# 對所有 submodules 執行命令
git submodule foreach 'git checkout main'
git submodule foreach 'git pull'
```

---

## 推薦工作流程

### 日常開發流程

1. **開始工作**
   ```bash
   git pull
   git submodule update --init --recursive
   ```

2. **檢查 Submodule 更新**
   ```bash
   git submodule update --remote
   ```

3. **撰寫分析文件**（在 `docs/analysis/` 中）

4. **提交變更**
   ```bash
   git add .
   git commit -m "docs: 新增 XXX 功能分析"
   git push
   ```

### 定期維護

- ✅ 每日：GitHub Actions 自動檢查更新
- ✅ 每週：手動檢查重要變更並撰寫分析
- ✅ 每月：更新整體功能概覽文件

---

## 實用資源

- [Git Submodules 官方文件](https://git-scm.com/book/en/v2/Git-Tools-Submodules)
- [GitHub: Working with Submodules](https://github.blog/2016-02-01-working-with-submodules/)
- [Atlassian Git Submodules Tutorial](https://www.atlassian.com/git/tutorials/git-submodule)

---

## 總結

使用 Git Submodule 的關鍵要點：

✅ **初始設定**：`git submodule add <url>`  
✅ **更新版本**：`git submodule update --remote`  
✅ **Clone 專案**：`git clone --recursive <url>`  
✅ **自動化**：設定 GitHub Actions 定期更新  
✅ **團隊協作**：確保所有人使用 `--recursive` flag  

有問題歡迎參考官方文件或提出 issue！
