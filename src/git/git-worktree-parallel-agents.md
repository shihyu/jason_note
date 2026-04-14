# 使用 Git Worktree 進行平行代理編程

大多數人每天都會使用 AI 代理。很多時候，我們甚至沒有注意到它。代理現在在程式設計中已經很常見，它們幫助我們完成許多任務。

我們現在正在邁向下一個基於代理編程的階段。我們可以使用平行代理，在同一個儲存庫中同時處理多個功能和修復。

Claude Code 和 Cursor 支援平行代理。它們使用 Git worktree 為每個代理提供自己的工作空間。您可以通過在專案中建立 worktree 來遵循相同的方法。

讓我們先了解什麼是 Git worktree，以及它們如何幫助平行編程。

## 大綱

1. 什麼是 Git worktree
2. Git worktree 與 Git Clone 的比較
3. Git worktree 指令
4. Claude Code 的 Git worktree 平行代理
5. Cursor 的 Git worktree 平行代理
6. CodeRabbit 的 Git worktree runner

## 什麼是 Git worktree

[Git worktree](https://git-scm.com/docs/git-worktree) 是 Git 中的一項功能。在我們了解 Git worktree 之前，讓我們先看看一般的 Git 流程。

- 您有一個工作目錄。
- 您有一個作用中的分支。
- 切換分支會改變該目錄中的所有檔案

```
my-app/
├── src/
├── README.md
└── .git/
```

當您執行 `git checkout "feature-abc"` 時，整個目錄會切換到該分支。

- Worktree 讓您可以從同一個儲存庫擁有多个工作目錄。
- 每個目錄可以有自己的分支。
- 您可以同時在所有這些目錄中工作，而無需切換任何東西。

> 簡單來說，您可以在不切換分支的情況下平行工作。

```
my-app/                    
├── src/
├── README.md
└── .git/

my-app-feature-a/          ← Worktree 1 (feature-a 分支)
├── src/
├── README.md
└── .git                   ← 檔案指向主儲存庫

my-app-feature-b/          ← Worktree 2 (feature-b 分支)
├── src/
├── README.md
└── .git                   ← 檔案指向主儲存庫
```

![Git worktree 概念圖](./images/worktree-concept.gif)

上圖解釋了這個概念。但指令會讓它更加清晰。

這是我們在一般克隆和使用 work tree 時所做的比較。

![Git worktree vs Clone 比較](./images/worktree-vs-clone.png)

## Git worktree 指令

以下是您會經常使用的一些基本 Git worktree 指令。

```bash
# 建立 worktree 和新分支
git worktree add <worktree路徑> -b <新分支名稱>

# 範例
git worktree add ../add-header -b feature/add-header


# 從現有分支建立 worktree
git worktree add <worktree路徑> <分支名稱>

# 範例
git worktree add ../ui-changes feature/ui-changes
```

```bash
# 列出所有作用中的 worktree
git worktree list
```

```bash
# 移除 worktree
git worktree remove <worktree路徑>

# 範例
git worktree remove ../add-header
```

Git 對 worktree 有一個簡單的規則：一個分支只能同時存在於一個 worktree 中。

如果分支已經在某個 worktree 中使用，Git 會阻止您再次使用它。請參見下圖。

![分支已被使用時 Git 會阻擋](./images/worktree-blocked.png)

## Claude Code 的平行代理

當您使用 Git worktree 時，[Claude Code 可以執行平行代理](https://code.claude.com/docs/en/common-workflows#run-parallel-claude-code-sessions-with-git-worktrees)。每個 worktree 都有自己獨立的目錄和分支，因此 Claude 可以同時處理多個任務。

當時我正在建立一個個人使用的 Gmail 郵件中心。同時有 UI 變更和 OAuth 工作在進行。

以下是我如何使用 Claude Code 搭配 worktree 同時建立兩個功能。

```bash
git worktree add ../ui-changes -b feature/ui-changes
```

![建立 UI 變更 worktree](./images/claude-worktree-ui.png)

```bash
git worktree add ../oauth-integration -b feature/oauth-integration
```

![建立 OAuth 整合 worktree](./images/claude-worktree-oauth.png)

建立它们之後，我列出 worktree 以確保一切都設定正確：

![列出所有 worktree](./images/worktree-list.png)

您也可以查看每個分支的獨立目錄。

![各分支的獨立資料夾](./images/worktree-folders.png)

現在 Claude Code 可以在這些分支上工作，而無需切換，因為我們有獨立的目錄。

我使用 Claude Code 透過 worktree 同時處理 UI 變更和 OAuth 整合。

下面的影片展示了它如何即時運作。

## Cursor 的平行代理

Cursor 讓您可以輕鬆地透過在背景[使用 Git worktree](https://cursor.com/docs/configuration/worktrees) 來執行平行代理。

您可以先選擇一個 worktree 並為同一任務選擇多個模型，如下圖所示。Cursor 將同時在所有選定的模型上執行相同的提示。

![Cursor 選擇 Worktree 和模型](./images/cursor-worktree-select.png)

提交提示後，Cursor 會為每個模型顯示一張卡片。您可以點擊這些卡片，查看每個模型如何變更程式碼。

當您喜歡某個版本時，可以點擊 [Apply](https://cursor.com/docs/configuration/worktrees#apply-functionality)。Cursor 會將那些編輯帶入您已checkout 的分支。

您也可以透過編輯 `.cursor/worktrees.json` 檔案來自訂 worktree。

您在 setup-worktree 下新增的所有指令將在設定期間在 worktree 內執行。

![Cursor Worktree 設定](./images/cursor-worktree-setup.png)

您隨時可以透過執行 `git worktree list` 來查看所有作用中的 worktree。如果想在 SCM 面板中查看 Cursor 建立的 worktree，可以啟用 `git.showCursorWorktrees` 設定。

![Cursor SCM 中的 Worktree](./images/cursor-worktree-scm.png)

## CodeRabbit 的 Git Worktree Runner

如果您想要更簡單的方式來處理 worktree，CodeRabbit 提供了一個名為 Git Worktree Runner 的輔助工具。它讓建立、開啟和管理 worktree 變得容易，透過簡短的指令。如果您經常使用 worktree，這個工具可以節省大量打字時間。

您可以在這裡找到它：[CodeRabbit 的 Git Worktree Runner](https://github.com/coderabbitai/git-worktree-runner)

以下是安裝和使用方法。

```bash
# 安裝
git clone https://github.com/coderabbitai/git-worktree-runner.git
cd git-worktree-runner
sudo ln -s "$(pwd)/bin/git-gtr" /usr/local/bin/git-gtr

# 使用方式
cd ~/your-repo                              # 導航到 git 儲存庫
git gtr config set gtr.editor.default cursor    # 一次性設定
git gtr config set gtr.ai.default claude        # 一次性設定

# 日常工作流程
git gtr new my-feature                          # 建立 worktree
git gtr editor my-feature                       # 在編輯器中開啟
git gtr ai my-feature                           # 啟動 AI 工具
git gtr rm my-feature                           # 完成後移除
```

這張表格快速比較了 Git worktree 指令和相應的 gtr 指令。

## 結論

我們探討了 Git worktree 以及它們如何幫助平行代理編程。

Worktree 讓您可以同時建立多個功能，而無需切換分支或建立額外的克隆。

像 Claude Code、Cursor 這樣的工具讓它變得更好，它們將每個代理連結到自己的 worktree。這樣可以保持工作整潔、安全、快速。

一旦您開始使用 worktree，就很回到舊的單一目錄流程了。您將獲得更多專注、更快的速度，以及更少的錯誤。嘗試為您的下一個專案建立一些 worktree，看看同時處理多個功能是多麼簡單。

如果您使用任何基於代理的編碼工具，worktree 將成為您日常工作中很自然的一部分。

現在就試試看，讓我知道它如何幫助您的工作流程！

祝您學習愉快！

感謝您閱讀 Dev Shorts！這篇文章是公開的，所以請自由分享。

[分享](https://www.devshorts.in/p/coding-with-parallel-agents-and-git?utm_source=substack&utm_medium=email&utm_content=share&action=share)
