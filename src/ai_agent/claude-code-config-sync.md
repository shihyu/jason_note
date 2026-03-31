# Claude Code 設定備份與跨機同步指南

把 Claude Code 的設定當成 dotfiles 管理即可。

## 要備份哪些內容？

| 路徑 | 說明 |
|------|------|
| `~/.claude/` | 設定、skills、agents、hooks 主目錄 |
| `~/.claude.json` | MCP 設定、工具偏好（舊版或部分安裝方式） |

> **API key 警告**：`~/.claude.json` 可能含有 `apiKey`，加入 `.gitignore` 再 commit。

## 方法一：快速搬移（tar）

```bash
# 舊機器備份
tar czf claude-backup.tgz ~/.claude ~/.claude.json 2>/dev/null

# 新機器還原（先備份現有設定）
mv ~/.claude ~/.claude.bak 2>/dev/null
tar xzf claude-backup.tgz -C ~
```

或直接用 rsync：

```bash
rsync -avz ~/.claude ~/.claude.json user@new-host:~/
```

## 方法二：直接把 `~/.claude` 做成 git repo（推薦）

不需要 symlink，最簡單：

```bash
# 首次設定
cd ~/.claude
echo '.claude.json' >> .gitignore   # 避免 API key 外洩
git init
git add .
git commit -m "init claude config"
git remote add origin git@github.com:you/claude-config.git
git push -u origin main
```

新機器還原：

```bash
git clone git@github.com:you/claude-config.git ~/.claude
```

日後同步：`git pull` / `git push`。

## 方法三：Git + symlink（適合整合既有 dotfiles repo）

```bash
# 在 dotfiles repo 中
cp -r ~/.claude ~/dotfiles/claude
cp ~/.claude.json ~/dotfiles/  # 若無 API key

# install.sh
rm -rf "$HOME/.claude"
ln -s "$HOME/dotfiles/claude" "$HOME/.claude"
[ -f "$HOME/dotfiles/.claude.json" ] && ln -sf "$HOME/dotfiles/.claude.json" "$HOME/.claude.json"
```

## 哪些該同步？

| 類型 | 建議 |
|------|------|
| agents、skills、hooks、CLAUDE.md | 同步 |
| 通用 MCP server 設定 | 同步 |
| `ANTHROPIC_API_KEY`、model ARN、DB 連線 | 用環境變數或 `settings.local.json`，**不同步** |
| session history、debug logs | 不同步 |

## 結論

- 只搬一次 → 用 `tar` 或 `rsync`
- 多台機器長期維護 → **方法二**（`~/.claude` 直接 git repo）最簡潔
