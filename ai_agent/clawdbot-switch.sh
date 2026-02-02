#!/bin/bash
#
# Clawdbot Model 快速切換腳本
# 用途：在不同的 AI Model 之間快速切換
# 作者：根據 Clawdbot-Guide.md 建立
#
# 使用方法：
#   ./clawdbot-switch.sh claude   - 切換到 Claude Sonnet 4.5
#   ./clawdbot-switch.sh gemini   - 切換到 Gemini 3 Pro
#   ./clawdbot-switch.sh codex    - 切換到 Codex GPT-5.2
#   ./clawdbot-switch.sh opus     - 切換到 Claude Opus 4.5
#   ./clawdbot-switch.sh status   - 查看當前 model
#   ./clawdbot-switch.sh list     - 列出所有可用 models
#

set -e  # 遇到錯誤立即退出

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 檢查 clawdbot 是否安裝
if ! command -v clawdbot &> /dev/null; then
    echo -e "${RED}錯誤：找不到 clawdbot 指令${NC}"
    echo "請先安裝 Clawdbot: curl -fsSL https://clawd.bot/install.sh | bash"
    exit 1
fi

case "$1" in
  claude)
    echo -e "${BLUE}🤖 切換到 Claude Sonnet 4.5...${NC}"
    clawdbot models set claude
    echo -e "${GREEN}✅ 切換成功！${NC}"
    ;;
  opus)
    echo -e "${BLUE}🤖 切換到 Claude Opus 4.5...${NC}"
    clawdbot models set opus
    echo -e "${GREEN}✅ 切換成功！${NC}"
    ;;
  gemini)
    echo -e "${BLUE}🤖 切換到 Gemini 3 Pro Preview...${NC}"
    echo -e "${YELLOW}⚠️  注意：Gemini 回應較慢（約 2 分鐘）${NC}"
    clawdbot models set gemini
    echo -e "${GREEN}✅ 切換成功！${NC}"
    ;;
  codex)
    echo -e "${BLUE}🤖 切換到 Codex GPT-5.2...${NC}"
    clawdbot models set codex
    echo -e "${GREEN}✅ 切換成功！${NC}"
    ;;
  status)
    echo -e "${BLUE}📊 當前 Model 狀態：${NC}"
    clawdbot models status | grep -A 3 "Default\|Primary"
    ;;
  list)
    echo -e "${BLUE}📋 可用的 Models：${NC}"
    clawdbot models aliases list
    echo ""
    echo -e "${BLUE}完整的 Models 列表：${NC}"
    clawdbot models list | grep -v "missing"
    ;;
  setup-aliases)
    echo -e "${BLUE}🔧 設定 Model Aliases...${NC}"
    clawdbot models aliases add claude anthropic/claude-sonnet-4-5
    clawdbot models aliases add opus anthropic/claude-opus-4-5
    clawdbot models aliases add gemini google-gemini-cli/gemini-3-pro-preview
    clawdbot models aliases add codex openai-codex/gpt-5.2-codex
    echo -e "${GREEN}✅ Aliases 設定完成！${NC}"
    echo ""
    clawdbot models aliases list
    ;;
  install-shell-aliases)
    echo -e "${BLUE}🔧 安裝 Shell Aliases...${NC}"

    # 檢測使用的 shell
    if [ -n "$ZSH_VERSION" ]; then
        RC_FILE="$HOME/.zshrc"
    elif [ -n "$BASH_VERSION" ]; then
        RC_FILE="$HOME/.bashrc"
    else
        RC_FILE="$HOME/.bashrc"
    fi

    # 檢查是否已經安裝
    if grep -q "cb-claude" "$RC_FILE" 2>/dev/null; then
        echo -e "${YELLOW}⚠️  Aliases 已經存在於 $RC_FILE${NC}"
        read -p "是否覆蓋？(y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "取消安裝"
            exit 0
        fi
    fi

    # 安裝 aliases
    cat >> "$RC_FILE" << 'EOF'

# Clawdbot Model 快速切換 (auto-generated)
alias cb-switch='~/clawdbot-switch.sh'
alias cb-claude='clawdbot models set claude'
alias cb-gemini='clawdbot models set gemini'
alias cb-codex='clawdbot models set codex'
alias cb-opus='clawdbot models set opus'
alias cb-status='clawdbot models status | grep -A 3 "Default"'
alias cb-list='clawdbot models aliases list'
EOF

    echo -e "${GREEN}✅ Aliases 已加入到 $RC_FILE${NC}"
    echo ""
    echo "請執行以下指令使其生效："
    echo -e "${YELLOW}source $RC_FILE${NC}"
    echo ""
    echo "之後就可以使用以下指令："
    echo "  cb-claude  - 切換到 Claude"
    echo "  cb-gemini  - 切換到 Gemini"
    echo "  cb-codex   - 切換到 Codex"
    echo "  cb-status  - 查看狀態"
    ;;
  help|--help|-h)
    echo "Clawdbot Model 快速切換腳本"
    echo ""
    echo "用法: $0 {command}"
    echo ""
    echo "切換 Model："
    echo "  claude   - 切換到 Claude Sonnet 4.5（快速、日常對話）"
    echo "  opus     - 切換到 Claude Opus 4.5（最強推理）"
    echo "  gemini   - 切換到 Gemini 3 Pro（大 context，較慢）"
    echo "  codex    - 切換到 Codex GPT-5.2（代碼優化）"
    echo ""
    echo "查詢："
    echo "  status   - 查看當前使用的 model"
    echo "  list     - 列出所有可用 models"
    echo ""
    echo "設定："
    echo "  setup-aliases          - 設定 Clawdbot model aliases"
    echo "  install-shell-aliases  - 安裝 shell aliases (cb-claude 等)"
    echo ""
    echo "Model 特性比較："
    echo "  Claude Sonnet 4.5  : 快速（~10秒）、平衡、適合日常"
    echo "  Claude Opus 4.5    : 最聰明、較慢、較貴、最強推理"
    echo "  Gemini 3 Pro       : 大 context (1024k)、很慢（~2分鐘）"
    echo "  Codex GPT-5.2      : 代碼優化、快速（~15秒）"
    exit 0
    ;;
  *)
    echo -e "${RED}錯誤：未知的指令 '$1'${NC}"
    echo ""
    echo "用法: $0 {claude|opus|gemini|codex|status|list|help}"
    echo ""
    echo "快速切換 AI Model："
    echo "  $0 claude   - 切換到 Claude Sonnet 4.5（快速、日常對話）"
    echo "  $0 opus     - 切換到 Claude Opus 4.5（最強推理）"
    echo "  $0 gemini   - 切換到 Gemini 3 Pro（大 context）"
    echo "  $0 codex    - 切換到 Codex GPT-5.2（代碼優化）"
    echo "  $0 status   - 查看當前使用的 model"
    echo "  $0 list     - 列出所有可用 models"
    echo "  $0 help     - 顯示完整說明"
    echo ""
    echo "首次使用？執行："
    echo "  $0 setup-aliases          # 設定 model aliases"
    echo "  $0 install-shell-aliases  # 安裝 shell aliases"
    exit 1
    ;;
esac
