#!/usr/bin/env bash
# ============================================================
# Claude Code 完整安裝 / 重裝腳本
# 根據 installed-setup-2026-04-01.md 重建所有設定
#
# 適用情境：
#   A) 乾淨新機器（首次安裝）
#   B) 現有機器重裝（清除舊設定重建）
#
# 乾淨機器需先手動完成：
#   1. 安裝 Node.js >= 18  (https://nodejs.org)
#   2. 安裝 Claude Code CLI: npm install -g @anthropic-ai/claude-code
#   3. 登入 Claude: claude login
#
# 保留：~/.claude.json（MCP設定）、~/.agents/（skills）
# 清除：~/.claude/（plugins, sessions, history, plans）
# ============================================================

set -euo pipefail

# ─── 顏色 ────────────────────────────────────────────────────
RED='\033[0;31m'; YELLOW='\033[1;33m'; GREEN='\033[0;32m'
BLUE='\033[0;34m'; CYAN='\033[0;36m'; NC='\033[0m'

info()    { echo -e "${BLUE}[INFO]${NC} $*"; }
success() { echo -e "${GREEN}[OK]${NC} $*"; }
warn()    { echo -e "${YELLOW}[WARN]${NC} $*"; }
error()   { echo -e "${RED}[ERROR]${NC} $*"; exit 1; }
section() { echo -e "\n${CYAN}══════════════════════════════════════${NC}"; echo -e "${CYAN}  $*${NC}"; echo -e "${CYAN}══════════════════════════════════════${NC}"; }

# ─── 前置檢查 ────────────────────────────────────────────────
section "前置檢查"
command -v node  >/dev/null || error "找不到 Node.js，請先安裝 https://nodejs.org"
command -v npm   >/dev/null || error "找不到 npm"
command -v claude >/dev/null || error "找不到 claude CLI，請執行: npm install -g @anthropic-ai/claude-code"
command -v npx   >/dev/null || error "找不到 npx"

NODE_VER=$(node --version)
CLAUDE_VER=$(claude --version 2>/dev/null | head -1)
success "Node.js: $NODE_VER"
success "Claude Code: $CLAUDE_VER"

# ─── 確認操作 ────────────────────────────────────────────────
echo ""
echo "======================================================"
echo "  Claude Code 完整安裝 / 重裝腳本"
echo "======================================================"
echo ""
echo "此腳本將會："
echo "  [清除] ~/.claude/    (plugins, sessions, history, plans)"
echo "  [保留] ~/.claude.json (MCP 設定)"
echo "  [重裝] Plugins  × 25"
echo "  [重裝] Global Skills × 31  (透過 npx skills add -g)"
echo ""
echo "  注意：MCP Servers 需手動重新設定（腳本結尾有指令）"
echo ""
read -r -p "確定要繼續嗎？(輸入 yes 確認): " CONFIRM
[[ "$CONFIRM" == "yes" ]] || { echo "取消操作。"; exit 0; }

# ─── Step 1: 備份 ────────────────────────────────────────────
section "Step 1: 備份現有設定"
BACKUP_DIR="$HOME/claude-backup-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"

[[ -f ~/.claude.json ]] \
    && cp ~/.claude.json "$BACKUP_DIR/" \
    && success "備份 ~/.claude.json"
[[ -f ~/.claude/settings.json ]] \
    && cp ~/.claude/settings.json "$BACKUP_DIR/settings.json" \
    && success "備份 settings.json"
[[ -f ~/.claude/settings.local.json ]] \
    && cp ~/.claude/settings.local.json "$BACKUP_DIR/settings.local.json"
[[ -f ~/.agents/.skill-lock.json ]] \
    && cp ~/.agents/.skill-lock.json "$BACKUP_DIR/skill-lock.json" \
    && success "備份 skill-lock.json"

success "備份完成：$BACKUP_DIR"

# ─── Step 2: 清除 ~/.claude ──────────────────────────────────
section "Step 2: 清除 ~/.claude"
if [[ -d ~/.claude ]]; then
    rm -rf ~/.claude
    success "~/.claude 已清除"
else
    info "~/.claude 不存在（乾淨機器），跳過"
fi

# ─── Step 3: 新增 Marketplaces ──────────────────────────────
section "Step 3: 新增 Marketplaces"

claude plugin marketplace add anthropics/claude-plugins-official \
    && success "added: claude-plugins-official"

claude plugin marketplace add rohittcodes/claude-plugin-suite \
    && success "added: claude-plugin-suite"

claude plugin marketplace add openai/codex-plugin-cc \
    && success "added: openai-codex"

# ─── Step 4: 安裝 Plugins ────────────────────────────────────
section "Step 4: 安裝 Plugins (共 25 個)"

# 來自 claude-plugins-official（24 個，按字母排序）
PLUGINS_OFFICIAL=(
    agent-sdk-dev
    chrome-devtools-mcp
    claude-code-setup
    claude-md-management
    code-review
    code-simplifier
    commit-commands
    context7
    feature-dev
    figma
    frontend-design
    gopls-lsp
    playwright
    pr-review-toolkit
    pyright-lsp
    remember
    rust-analyzer-lsp
    searchfit-seo
    security-guidance
    semgrep
    skill-creator
    supabase
    superpowers
    typescript-lsp
)

for plugin in "${PLUGINS_OFFICIAL[@]}"; do
    if claude plugin install "${plugin}@claude-plugins-official"; then
        success "installed: $plugin"
    else
        warn "failed: $plugin（繼續安裝其他）"
    fi
done

# 來自 openai-codex（1 個）
if claude plugin install "codex@openai-codex"; then
    success "installed: codex"
else
    warn "failed: codex"
fi

# ─── Step 5: 安裝 Global Skills（透過 npx skills）────────────
section "Step 5: 安裝 Global Skills (共 31 個)"
info "使用 npx skills add -g 安裝至 ~/.agents/skills/"
echo ""

# Skills 按來源分組（來自 ~/.agents/.skill-lock.json）
SKILL_SOURCES=(
    "anthropics/skills"             # canvas-design, doc-coauthoring, docx, frontend-design, pdf, pptx, skill-creator, theme-factory, web-artifacts-builder, webapp-testing, xlsx
    "obra/superpowers"              # brainstorming, executing-plans, requesting-code-review, systematic-debugging, test-driven-development, writing-plans
    "vercel-labs/agent-skills"      # vercel-composition-patterns, vercel-react-best-practices, vercel-react-native-skills, web-design-guidelines
    "vercel-labs/skills"            # find-skills
    "wshobson/agents"               # architecture-decision-records, architecture-patterns
    "nhadaututtheky/neural-memory"  # memory-audit, memory-evolution, memory-intake
    "othmanadi/planning-with-files" # planning-with-files
    "shadcn/ui"                     # shadcn
    "shubhamsaboo/awesome-llm-apps" # project-planner
    "squirrelscan/skills"           # audit-website
)

for source in "${SKILL_SOURCES[@]}"; do
    # 去除 inline 註解
    src="${source%%#*}"
    src="${src%% }"
    if npx skills add -g "$src" --all --yes 2>/dev/null; then
        success "installed skills from: $src"
    else
        warn "failed: $src（可能需要手動安裝）"
    fi
done

echo ""
info "驗證安裝結果："
INSTALLED_COUNT=$(npx skills list -g 2>/dev/null | grep -c "~/.agents/skills/" || echo "?")
echo "  ~/.agents/skills/ 內共有：$INSTALLED_COUNT 個 skills"

# ─── Step 6: MCP Servers（手動設定指引）────────────────────
section "Step 6: MCP Servers 設定（需手動執行）"

info "MCP Servers 設定存於 ~/.claude.json"
echo ""
echo "目前 ~/.claude.json 內的 MCP servers："
python3 -c "
import json, os
path = os.path.expanduser('~/.claude.json')
try:
    with open(path) as f:
        d = json.load(f)
    mcps = d.get('mcpServers', {})
    for k in mcps:
        print(f'  ✓ {k}')
    if not mcps:
        print('  (空白 — 需要重新設定)')
except Exception as e:
    print(f'  無法讀取: {e}')
" 2>/dev/null

echo ""
echo "  若 ~/.claude.json 不存在或 MCP 遺失，請執行以下指令重新加入："
echo ""
echo "  ┌─ stdio MCPs ──────────────────────────────────────────────────"
echo "  │"
echo "  │  # playwright"
echo "  │  claude mcp add playwright -- npx -y @executeautomation/playwright-mcp-server"
echo "  │"
echo "  │  # memory（graph-based）"
echo "  │  claude mcp add memory -- npx -y @modelcontextprotocol/server-memory"
echo "  │"
echo "  │  # filesystem"
echo "  │  claude mcp add filesystem -- npx -y @modelcontextprotocol/server-filesystem \$HOME"
echo "  │"
echo "  │  # git"
echo "  │  claude mcp add git -- uvx mcp-server-git"
echo "  │"
echo "  │  # sequential-thinking"
echo "  │  claude mcp add sequentialthinking -- npx -y @modelcontextprotocol/server-sequential-thinking"
echo "  │"
echo "  │  # neural-memory（需先安裝 nmem: pip install nmem）"
echo "  │  claude mcp add neural-memory -- nmem-mcp"
echo "  │"
echo "  │  # context7（Upstash 文件查詢）"
echo "  │  claude mcp add context7 -- npx -y @upstash/context7-mcp@latest"
echo "  │"
echo "  └───────────────────────────────────────────────────────────────"
echo ""
echo "  ┌─ http MCPs ───────────────────────────────────────────────────"
echo "  │"
echo "  │  # github（需要 GitHub PAT，至 https://github.com/settings/tokens 申請）"
echo "  │  claude mcp add --transport http github https://api.githubcopilot.com/mcp \\"
echo "  │    --header 'Authorization: Bearer <YOUR_GITHUB_PAT>'"
echo "  │"
echo "  └───────────────────────────────────────────────────────────────"
echo ""
echo "  注意：chrome-devtools-mcp、context7（plugin）、figma、playwright（plugin）、"
echo "        supabase 為 Plugin MCPs — 安裝對應 plugin 後自動啟用，不需手動加入。"

# ─── 完成 ────────────────────────────────────────────────────
section "安裝完成"
success "請重新啟動 Claude Code"
echo ""
echo "  備份位置  ：$BACKUP_DIR"
echo "  驗證指令  ："
echo "    claude plugin list          → 確認 25 個 plugins"
echo "    npx skills list -g          → 確認 31 個 global skills"
echo "    claude mcp list             → 確認 MCP servers"
echo ""
