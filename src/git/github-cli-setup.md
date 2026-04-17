# GitHub CLI 與 Git 設定完整步驟

## 目標
讓 `git clone`、`git pull`、`git push` 等指令自動使用 GitHub 認證，無需每次輸入帳密。

## 完整步驟

### 1. 安裝 gh（如果還沒安裝）

```bash
# macOS
brew install gh

# Ubuntu/Debian
sudo apt install gh

# 其他系統
# 參考 https://github.com/cli/cli#installation
```

### 2. 登入 GitHub

```bash
gh auth login
```

選擇：
- **GitHub.com** → `HTTPS`
- **登入方式** → 依需求選擇（browser / token）
- 依提示完成認證

### 3. 設定 git 使用 gh 的 credential helper

```bash
git config --global credential.helper "/usr/bin/gh auth git-credential"
```

### 4. 確認設定成功

```bash
git config --global --list | grep credential
```

預期輸出：
```
credential.helper=/usr/bin/gh auth git-credential
```

### 5. 開始使用

```bash
# Clone
git clone https://github.com/owner/repo.git

# Pull
git clone https://github.com/owner/repo.git
cd repo
git pull

# Push
git add .
git commit -m "message"
git push
```

## 原理說明

| 元件 | 角色 |
|------|------|
| `gh` | GitHub CLI，已儲存你的登入 token |
| `gh auth git-credential` | credential helper 程式 |
| git credential.helper | 告訴 git「要認證時問這個程式」 |

設定完成後，git 會自動呼叫 `gh auth git-credential` 取得 token，無需手動輸入帳密。

## 驗證環境

```bash
# 確認 gh 登入狀態
gh auth status

# 確認 git credential helper 設定
git config --global --list | grep credential
```

## 常見問題

**Q: 之後再開新的 terminal 還需要重新設定嗎？**
A: 不需要，設定存在 `~/.gitconfig` 和 `~/.config/gh/hosts.yml`，重開終端依然有效。

**Q: 想切換另一個 GitHub 帳號？**
A: 執行 `gh auth switch` 切換，或重新 `gh auth login`。

**Q: credential.helper 路徑不對？**
A: 用 `which gh` 確認 gh 的安裝路徑，通常是 `/usr/bin/gh` 或 `~/.local/bin/gh`。

## `gh auth setup-git`  vs  手動設定

GitHub CLI 提供兩種設定方式：

### 方式一：文件中的手動設定（步驟 3）

```bash
# 登入
gh auth login

# 手動設定 credential helper
git config --global credential.helper "/usr/bin/gh auth git-credential"
```

### 方式二：`gh auth setup-git`（自動化）

```bash
# 登入
gh auth login

# 一條龍自動設定 credential helper
gh auth setup-git
```

### 差異對照

| | 手動設定 | `gh auth setup-git` |
|---|---|---|
| 安裝 gh | 需手動 | 需手動 |
| 登入 | `gh auth login` | `gh auth login` |
| 設定 credential.helper | 手動 `git config` | 全自動 |

**結論**：`gh auth setup-git` 就是把手動 `git config` 步驟自動化，一個命令搞定。其餘（安裝、登入）兩種方式相同。
