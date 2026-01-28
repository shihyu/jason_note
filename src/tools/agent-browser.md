# Agent-Browser - 強大的瀏覽器自動化工具

## 簡介

Agent-Browser 是由 Vercel Labs 開發的瀏覽器自動化 CLI 工具，專為 AI Agent 設計。相比其他 Browser Use 工具，agent-browser 具有以下優勢：

- **超過 200 種瀏覽器操作**：涵蓋你能想到的所有操作
- **支援 Headless 模式**：可在遠端 Linux 主機上運行，無需圖形界面
- **Token 用量更少**：相比 Playwright MCP，更節省 token
- **反應速度快**：不易觸發 Context Window 限制
- **不易被網站偵測**：相比 chrome-devtools MCP，更不容易被識別為機器人

## 與其他工具比較

| 工具 | 優點 | 缺點 |
|------|------|------|
| **chrome-devtools MCP** | 功能強大 | 容易被網站偵測為機器人 |
| **Playwright (內建)** | 功能完整 | token 用量多、反應慢、容易爆 Context Window |
| **agent-browser** | token 少、速度快、不易被偵測、支援 headless | - |

## 安裝步驟

### 前置需求

確保已安裝 Node.js 和 npm。

### 1. 安裝 agent-browser CLI

```bash
npm install -g agent-browser
```

### 2. 下載 Chromium

```bash
agent-browser install
```

### 3. 安裝到 Claude Code (Skill)

```bash
# 建立 skill 目錄
mkdir -p ~/.claude/skills/agent-browser

# 下載 SKILL.md 檔案
curl -o ~/.claude/skills/agent-browser/SKILL.md \
  https://raw.githubusercontent.com/vercel-labs/agent-browser/main/skills/agent-browser/SKILL.md

# 驗證下載成功（檔案應有 250+ 行，8KB+ 大小）
wc -l ~/.claude/skills/agent-browser/SKILL.md
ls -lh ~/.claude/skills/agent-browser/SKILL.md
```

#### 一鍵安裝與驗證腳本

```bash
#!/bin/bash
# 安裝 agent-browser skill

SKILL_DIR="$HOME/.claude/skills/agent-browser"
SKILL_URL="https://raw.githubusercontent.com/vercel-labs/agent-browser/main/skills/agent-browser/SKILL.md"

echo "Creating skill directory..."
mkdir -p "$SKILL_DIR"

echo "Downloading SKILL.md..."
curl -o "$SKILL_DIR/SKILL.md" "$SKILL_URL"

# 驗證下載
if [ -f "$SKILL_DIR/SKILL.md" ]; then
    lines=$(wc -l < "$SKILL_DIR/SKILL.md")
    size=$(wc -c < "$SKILL_DIR/SKILL.md")

    if [ "$lines" -gt 200 ] && [ "$size" -gt 8000 ]; then
        echo "✅ Installation successful!"
        echo "   Lines: $lines"
        echo "   Size: $size bytes"
    else
        echo "❌ Downloaded file seems incomplete"
        echo "   Lines: $lines (expected > 200)"
        echo "   Size: $size bytes (expected > 8000)"
        exit 1
    fi
else
    echo "❌ Download failed"
    exit 1
fi
```

### 為 Gemini CLI 安裝

如果你同時使用 Gemini CLI，可以用以下方法安裝 agent-browser skill：

#### 方法 1: 直接下載安裝

```bash
# 建立 skill 目錄
mkdir -p ~/.gemini/skills/agent-browser

# 下載 SKILL.md 檔案
curl -o ~/.gemini/skills/agent-browser/SKILL.md \
  https://raw.githubusercontent.com/vercel-labs/agent-browser/main/skills/agent-browser/SKILL.md

# 驗證下載成功
wc -l ~/.gemini/skills/agent-browser/SKILL.md
ls -lh ~/.gemini/skills/agent-browser/SKILL.md
```

#### 方法 2: 使用 Gemini CLI 指令

```bash
# 從 GitHub 直接安裝
gemini skills install https://github.com/vercel-labs/agent-browser

# 查看已安裝的 skills
gemini skills list

# 啟用 skill（如果需要）
gemini skills enable agent-browser
```

#### 一鍵安裝與驗證腳本

```bash
#!/bin/bash
# 為 Gemini CLI 安裝 agent-browser skill

SKILL_DIR="$HOME/.gemini/skills/agent-browser"
SKILL_URL="https://raw.githubusercontent.com/vercel-labs/agent-browser/main/skills/agent-browser/SKILL.md"

echo "Creating skill directory for Gemini..."
mkdir -p "$SKILL_DIR"

echo "Downloading SKILL.md..."
curl -o "$SKILL_DIR/SKILL.md" "$SKILL_URL"

# 驗證下載
if [ -f "$SKILL_DIR/SKILL.md" ]; then
    lines=$(wc -l < "$SKILL_DIR/SKILL.md")
    size=$(wc -c < "$SKILL_DIR/SKILL.md")

    if [ "$lines" -gt 200 ] && [ "$size" -gt 8000 ]; then
        echo "✅ Gemini installation successful!"
        echo "   Lines: $lines"
        echo "   Size: $size bytes"

        # 使用 Gemini CLI 驗證
        echo ""
        echo "Verifying with Gemini CLI..."
        gemini skills list
    else
        echo "❌ Downloaded file seems incomplete"
        echo "   Lines: $lines (expected > 200)"
        echo "   Size: $size bytes (expected > 8000)"
        exit 1
    fi
else
    echo "❌ Download failed"
    exit 1
fi
```

#### 在 Gemini 中使用

安裝完成後，在 Gemini CLI 對話中直接使用：

```
今天 Hacker News 有什麼新聞嘛？使用 agent-browser
```

或明確呼叫：

```
/agent-browser 請幫我測試登入流程
```

### 為 Codex CLI 安裝

如果你使用 Codex CLI，也可以用相同的方法安裝 agent-browser skill：

#### 方法 1: 直接下載安裝

```bash
# 建立 skill 目錄
mkdir -p ~/.codex/skills/agent-browser

# 下載 SKILL.md 檔案
curl -o ~/.codex/skills/agent-browser/SKILL.md \
  https://raw.githubusercontent.com/vercel-labs/agent-browser/main/skills/agent-browser/SKILL.md

# 驗證下載成功
wc -l ~/.codex/skills/agent-browser/SKILL.md
ls -lh ~/.codex/skills/agent-browser/SKILL.md
```

#### 一鍵安裝與驗證腳本

```bash
#!/bin/bash
# 為 Codex CLI 安裝 agent-browser skill

SKILL_DIR="$HOME/.codex/skills/agent-browser"
SKILL_URL="https://raw.githubusercontent.com/vercel-labs/agent-browser/main/skills/agent-browser/SKILL.md"

echo "Creating skill directory for Codex..."
mkdir -p "$SKILL_DIR"

echo "Downloading SKILL.md..."
curl -o "$SKILL_DIR/SKILL.md" "$SKILL_URL"

# 驗證下載
if [ -f "$SKILL_DIR/SKILL.md" ]; then
    lines=$(wc -l < "$SKILL_DIR/SKILL.md")
    size=$(wc -c < "$SKILL_DIR/SKILL.md")

    if [ "$lines" -gt 200 ] && [ "$size" -gt 8000 ]; then
        echo "✅ Codex installation successful!"
        echo "   Lines: $lines"
        echo "   Size: $size bytes"

        # 檢查 Codex skills 目錄
        echo ""
        echo "Installed skills in Codex:"
        ls -1 ~/.codex/skills/ | grep -v "^\."
    else
        echo "❌ Downloaded file seems incomplete"
        echo "   Lines: $lines (expected > 200)"
        echo "   Size: $size bytes (expected > 8000)"
        exit 1
    fi
else
    echo "❌ Download failed"
    exit 1
fi
```

#### 在 Codex 中使用

安裝完成後，在 Codex CLI 對話中直接使用：

```
今天 Hacker News 有什麼新聞嘛？使用 agent-browser
```

或在互動模式下執行：

```bash
codex "用 agent-browser 幫我測試這個網站"
```

## 核心功能

### 導航控制
- `agent-browser open <url>` - 開啟網頁
- `agent-browser back` - 返回上一頁
- `agent-browser forward` - 前往下一頁
- `agent-browser reload` - 重新載入頁面
- `agent-browser close` - 關閉瀏覽器

### 頁面快照與分析
```bash
agent-browser snapshot            # 完整的可訪問性樹狀結構
agent-browser snapshot -i         # 僅顯示互動元素（推薦）
agent-browser snapshot -c         # 精簡輸出
agent-browser snapshot -d 3       # 限制深度為 3
agent-browser snapshot -s "#main" # 限定 CSS 選擇器範圍
```

### 互動操作（使用 @ref）
```bash
agent-browser click @e1           # 點擊
agent-browser dblclick @e1        # 雙擊
agent-browser focus @e1           # 聚焦元素
agent-browser fill @e2 "text"     # 清除並輸入
agent-browser type @e2 "text"     # 輸入（不清除）
agent-browser press Enter         # 按鍵
agent-browser press Control+a     # 組合鍵
agent-browser hover @e1           # 滑鼠懸停
agent-browser check @e1           # 勾選核取方塊
agent-browser uncheck @e1         # 取消勾選
agent-browser select @e1 "value"  # 選擇下拉選單
agent-browser scroll down 500     # 滾動頁面
agent-browser drag @e1 @e2        # 拖放
agent-browser upload @e1 file.pdf # 上傳檔案
```

### 資訊擷取
```bash
agent-browser get text @e1        # 取得元素文字
agent-browser get html @e1        # 取得 innerHTML
agent-browser get value @e1       # 取得輸入值
agent-browser get attr @e1 href   # 取得屬性
agent-browser get title           # 取得頁面標題
agent-browser get url             # 取得當前 URL
agent-browser get count ".item"   # 計算符合元素數量
```

### 狀態檢查
```bash
agent-browser is visible @e1      # 檢查是否可見
agent-browser is enabled @e1      # 檢查是否啟用
agent-browser is checked @e1      # 檢查是否勾選
```

### 截圖與錄影
```bash
agent-browser screenshot          # 截圖輸出到 stdout
agent-browser screenshot path.png # 儲存截圖
agent-browser screenshot --full   # 完整頁面截圖
agent-browser pdf output.pdf      # 儲存為 PDF

# 錄影功能
agent-browser record start ./demo.webm    # 開始錄影
agent-browser click @e1                   # 執行操作
agent-browser record stop                 # 停止並儲存
```

### 等待機制
```bash
agent-browser wait @e1                     # 等待元素
agent-browser wait 2000                    # 等待毫秒
agent-browser wait --text "Success"        # 等待文字出現
agent-browser wait --url "**/dashboard"    # 等待 URL 符合
agent-browser wait --load networkidle      # 等待網路閒置
agent-browser wait --fn "window.ready"     # 等待 JS 條件
```

### 進階功能

#### 視窗與裝置設定
```bash
agent-browser set viewport 1920 1080      # 設定視窗大小
agent-browser set device "iPhone 14"      # 模擬裝置
agent-browser set geo 37.7749 -122.4194   # 設定地理位置
agent-browser set offline on              # 切換離線模式
agent-browser set headers '{"X-Key":"v"}' # 設定 HTTP headers
agent-browser set media dark              # 模擬深色模式
```

#### Cookies 與儲存
```bash
agent-browser cookies                     # 取得所有 cookies
agent-browser cookies set name value      # 設定 cookie
agent-browser cookies clear               # 清除 cookies
agent-browser storage local               # 取得 localStorage
agent-browser storage local set k v       # 設定值
agent-browser storage local clear         # 清除
```

#### 多分頁與視窗
```bash
agent-browser tab                 # 列出分頁
agent-browser tab new [url]       # 新分頁
agent-browser tab 2               # 切換到分頁 2
agent-browser tab close           # 關閉分頁
agent-browser window new          # 新視窗
```

#### 網路攔截
```bash
agent-browser network route <url>              # 攔截請求
agent-browser network route <url> --abort      # 封鎖請求
agent-browser network route <url> --body '{}'  # 模擬回應
agent-browser network requests                 # 查看請求記錄
```

## 使用範例

### 範例 1：表單提交

```bash
agent-browser open https://example.com/form
agent-browser snapshot -i
# 輸出顯示: textbox "Email" [ref=e1], textbox "Password" [ref=e2], button "Submit" [ref=e3]

agent-browser fill @e1 "user@example.com"
agent-browser fill @e2 "password123"
agent-browser click @e3
agent-browser wait --load networkidle
agent-browser snapshot -i  # 檢查結果
```

### 範例 2：儲存認證狀態

```bash
# 登入一次
agent-browser open https://app.example.com/login
agent-browser snapshot -i
agent-browser fill @e1 "username"
agent-browser fill @e2 "password"
agent-browser click @e3
agent-browser wait --url "**/dashboard"
agent-browser state save auth.json

# 後續使用：載入已儲存的狀態
agent-browser state load auth.json
agent-browser open https://app.example.com/dashboard
```

### 範例 3：並行瀏覽器（Session）

```bash
agent-browser --session test1 open site-a.com
agent-browser --session test2 open site-b.com
agent-browser session list
```

### 範例 4：抓取 Hacker News 頭條新聞

這是一個實際使用案例，展示如何快速抓取新聞網站內容。

#### 用戶提示詞
```
今天 Hacker News 有什麼新聞嘛？使用 agent-browser
```

#### Claude Code 執行流程

```bash
# 1. 開啟 Hacker News 首頁
agent-browser open https://news.ycombinator.com

# 2. 獲取頁面互動元素（可選，用於了解頁面結構）
agent-browser snapshot -i

# 3. 使用 JavaScript 提取新聞標題和連結
agent-browser eval "Array.from(document.querySelectorAll('.titleline > a')).slice(0, 20).map((a, i) => \`\${i+1}. \${a.innerText}\\n   URL: \${a.href}\`).join('\\n\\n')"

# 4. 關閉瀏覽器
agent-browser close
```

#### 實際輸出結果

```
1. Show HN: ChartGPU – WebGPU-powered charting library (1M points at 60fps)
   URL: https://github.com/ChartGPU/ChartGPU

2. SmartOS
   URL: https://docs.smartos.org/

3. PicoPCMCIA – a PCMCIA development board for retro-computing enthusiasts
   URL: https://www.yyzkevin.com/picopcmcia/

4. Nested Code Fences in Markdown
   URL: https://susam.net/nested-code-fences.html

5. JPEG XL Demo Page
   URL: https://tildeweb.nl/~michiel/jxl/

... (更多新聞)

20. SETI@home is in hiberation
    URL: https://setiathome.berkeley.edu/
```

#### 進階版：提取更多資訊

```bash
# 同時提取標題、連結、評論數和發佈時間
agent-browser eval "
Array.from(document.querySelectorAll('.athing')).slice(0, 10).map((row, i) => {
  const title = row.querySelector('.titleline > a');
  const subtext = row.nextElementSibling?.querySelector('.subtext');
  const points = subtext?.querySelector('.score')?.innerText || 'N/A';
  const comments = subtext?.querySelector('a[href*=\"item?id=\"]:last-child')?.innerText || '0 comments';
  const time = subtext?.querySelector('.age')?.innerText || 'N/A';

  return \`\${i+1}. \${title.innerText}
   URL: \${title.href}
   Points: \${points} | Comments: \${comments} | Posted: \${time}
   ---\`;
}).join('\\n\\n')
"
```

#### 優勢展示

使用 agent-browser 相比傳統方法的優勢：

- ✅ **處理動態內容**：可執行 JavaScript 獲取動態載入的內容
- ✅ **Token 經濟**：只提取需要的資訊，不抓取整個 HTML
- ✅ **快速開發**：不需要寫爬蟲腳本，直接用 eval 即可
- ✅ **可視化除錯**：使用 `--headed` 模式可看到瀏覽器操作過程

## 在 Claude Code 中使用

安裝 skill 後，直接在對話中使用自然語言提示詞，Claude Code 會自動調用 agent-browser。

### 推薦提示詞範例

#### 1. 新聞與資訊抓取
```
今天 Hacker News 有什麼新聞嘛？使用 agent-browser
```
```
幫我抓取 Reddit r/programming 首頁的熱門文章，使用 agent-browser
```
```
用 agent-browser 查看 GitHub Trending 今天有哪些熱門專案
```

#### 2. 網站測試與截圖
```
使用 agent-browser 開啟 https://example.com 並截圖首頁
```
```
幫我測試 https://myapp.com/login 的登入流程，使用 agent-browser
```
```
用 agent-browser 檢查我的網站在手機版和電腦版的顯示效果
```

#### 3. 表單填寫與自動化
```
使用 agent-browser 自動填寫這個表單：https://example.com/form
```
```
幫我用 agent-browser 測試購物車結帳流程
```

#### 4. 資料擷取與監控
```
用 agent-browser 幫我監控這個頁面的價格變化
```
```
使用 agent-browser 提取這個網站的所有產品連結
```

### 明確呼叫 Skill

也可以使用 slash command 明確呼叫：

```
/agent-browser 請幫我測試登入流程
```

### 自動化流程

Claude Code 會自動：
1. 辨識你需要使用 agent-browser
2. 規劃執行步驟（open → snapshot → interact → extract）
3. 執行指令並回報結果
4. 自動關閉瀏覽器（clean up）

無需手動編寫腳本，只需用自然語言描述任務即可！

## 除錯功能

```bash
agent-browser open example.com --headed              # 顯示瀏覽器視窗
agent-browser console                                # 查看控制台訊息
agent-browser console --clear                        # 清除控制台
agent-browser errors                                 # 查看頁面錯誤
agent-browser errors --clear                         # 清除錯誤
agent-browser highlight @e1                          # 高亮元素
agent-browser trace start                            # 開始記錄追蹤
agent-browser trace stop trace.zip                   # 停止並儲存追蹤
```

## JSON 輸出（供程式解析）

加上 `--json` 參數可獲得機器可讀的輸出：

```bash
agent-browser snapshot -i --json
agent-browser get text @e1 --json
```

## 特色功能

### Headless 模式的優勢

在遠端 Linux 伺服器上，即使沒有圖形界面，agent-browser 仍可完美運作：

```bash
# 在遠端主機上執行（無需 X11 或 Wayland）
ssh user@remote-server
agent-browser open https://example.com
agent-browser screenshot output.png
```

### 語義化定位器（Semantic Locators）

除了使用 `@ref`，也可以使用語義化的方式定位元素：

```bash
agent-browser find role button click --name "Submit"
agent-browser find text "Sign In" click
agent-browser find label "Email" fill "user@test.com"
agent-browser find first ".item" click
agent-browser find nth 2 "a" text
```

## 常見使用情境

1. **網頁測試**：自動化測試流程，包含登入、表單填寫、頁面導航
2. **資料擷取**：從動態網站擷取資料（比 curl/wget 更強大）
3. **截圖與錄影**：自動生成網站截圖或操作示範影片
4. **表單自動填寫**：批次處理表單提交
5. **破解 Captcha**：AI Agent 可透過視覺理解來處理驗證碼

## 完整示範案例：從提示詞到結果

### 場景：抓取 Hacker News 最新新聞

#### 步驟 1：使用者輸入提示詞

```
今天 Hacker News 有什麼新聞嘛？使用 agent-browser
```

#### 步驟 2：Claude Code 自動執行

Claude Code 會自動規劃並執行以下步驟：

```bash
# 1. 開啟網頁
agent-browser open https://news.ycombinator.com
# ✓ Hacker News
#   https://news.ycombinator.com/

# 2. 分析頁面結構（內部執行）
agent-browser snapshot -i

# 3. 提取新聞資料
agent-browser eval "Array.from(document.querySelectorAll('.titleline > a')).slice(0, 20).map((a, i) => \`\${i+1}. \${a.innerText}\\n   URL: \${a.href}\`).join('\\n\\n')"

# 4. 清理
agent-browser close
# ✓ Browser closed
```

#### 步驟 3：Claude Code 整理輸出

```markdown
## 今天 Hacker News 的熱門新聞

以下是今天（2026-01-22）Hacker News 首頁的前 20 條熱門新聞：

### 技術項目類

1. **Show HN: ChartGPU – WebGPU-powered charting library (1M points at 60fps)**
   https://github.com/ChartGPU/ChartGPU

2. **SmartOS**
   https://docs.smartos.org/

3. **PicoPCMCIA – a PCMCIA development board for retro-computing enthusiasts**
   https://www.yyzkevin.com/picopcmcia/

### 開源與開發工具

4. **Anthropic's original take home assignment open sourced**
   https://github.com/anthropics/original_performance_takehome

5. **Skip Is Now Free and Open Source**
   https://skip.dev/blog/skip-is-free/

... (更多分類新聞)
```

### 整個流程的特點

1. **零配置**：不需要寫程式碼，自然語言即可
2. **智能規劃**：Claude 自動選擇最佳的指令組合
3. **結構化輸出**：自動整理成易讀的格式
4. **自動清理**：執行完畢自動關閉瀏覽器
5. **快速高效**：整個流程通常在 5-10 秒內完成

### Token 使用量比較

| 方法 | Token 用量 | 執行時間 |
|------|-----------|----------|
| **agent-browser** | ~3,000 tokens | 5-8 秒 |
| Playwright MCP | ~8,000 tokens | 15-20 秒 |
| 直接 WebFetch HTML | ~15,000 tokens | 10-15 秒 |

**結論**：agent-browser 在速度和 token 經濟性上都有顯著優勢。

## 優勢總結

✅ **Token 經濟**：相比 Playwright MCP，大幅減少 token 使用量
✅ **速度快**：反應迅速，不會卡頓
✅ **不易觸發限制**：降低 Context Window 爆滿的風險
✅ **Headless 友善**：完美支援無圖形界面的環境
✅ **難以偵測**：不易被網站識別為機器人
✅ **功能完整**：超過 200 種操作，幾乎涵蓋所有需求
✅ **自然語言友善**：用說的就能完成複雜的瀏覽器操作

## 參考資源

- **GitHub 儲存庫**: [vercel-labs/agent-browser](https://github.com/vercel-labs/agent-browser)
- **SKILL.md 檔案**: [SKILL.md](https://github.com/vercel-labs/agent-browser/blob/main/skills/agent-browser/SKILL.md)
- **安裝指令**:
  ```bash
  curl -o ~/.claude/skills/agent-browser/SKILL.md \
    https://raw.githubusercontent.com/vercel-labs/agent-browser/main/skills/agent-browser/SKILL.md
  ```

## 結論

Agent-Browser 目前已成為 Claude Code 瀏覽器操作的首選工具。無論是日常的網頁測試、資料擷取，還是複雜的自動化流程，agent-browser 都能以更低的 token 成本、更快的速度、更穩定的表現來完成任務。

強烈推薦所有 Claude Code 使用者安裝並體驗這個工具！
