# AI Skills：前端新的效率神器！

近來，AI 領域有個火爆的話題：**Skills**。

Github 上被瘋狂 star 的倉庫，很多都是和 skills 有關的。

有的倉庫僅僅上線三個月就獲得了快 **50K** 的 star，Skills 的火熱可見一斑。

![](images/img_6978cb43732a930.awebp)

不管是大模型，還是 Cursor、Codex、Claude、Trae、Copilot 等編程 IDE 都在爭先支持 Skills。

圍繞 Skills，它們在做的就是爲了完成一件事情：技能是通過學習和反覆練習獲得的，而 Skills 是把經驗和最佳實踐沉澱爲 AI 能力，將“知道”轉化爲“做到”的本領。

要說清楚什麼是 Skills，先來了解一下關於 AI 的 2 個核心概念：`Agent` 和 `MCP`。

### 關於 Agent

讓 Agent 開發一個在線商城平臺，要完成購物功能，它只需要考慮用戶輸入的“我要購買一個商品”指令，並最終完成購買商品這個目標，它並不關心項目是否前後端分離，前端用 vue 還是 react 來實現，後端用 java 還是 php，選什麼數據庫，也就是說，Agent 不在乎細節。

**Agent 是面向目標的。**

### 關於 MCP

![](images/img_6978cb43732af31.awebp)

我們在開發項目的過程中，一個項目不可能所有的功能都自己實現，往往需要一些第三方的服務，比如短信通知，微信、支付寶支付。而使用這些服務的方式就是通過調用第三方平臺的 API，每個平臺的都有自己的 API 規則。

**而 MCP 就是 AI 的 API，Agent 通過 MCP 來實現調用第三方服務，和第三方服務進行通信。**

### 回到 Skills

![](images/img_6978cb43732b232.awebp)

講清楚了 Agent 和 MCP 的概念後，我們知道，AI 在使用 MCP 或者完成一些目標任務時，會產生很多的重複性的工作，我們可以把這些重複性的工作整合成一個 `工具包`，只需要讓 AI 調用這個工具包就行，而這個工具包就是 `Skills`。

這個工具包，可以是前端的組件開發，文件下載，後端 SQL 查詢，接口文檔生成。所有人都可以使用這些工具包來完成自己工作。

![](images/img_6978cb43732b533.awebp)

下面從我們前端的角度出發，來看看 Skills：

開發一個增刪改查的功能，你要創建 API 文件，狀態管理、路由生成，增刪改查的頁面開發。想要按照項目或者公司的前端開發規範來完成這些任務，用 AI 來實現的話，僅憑一句提示詞：**幫我寫一個文件管理功能**，它可以做出來，但最終結果不是你想要的。

現在你可以使用 `增刪改查 Skill` 來完成這項任務，完全按照你設定的規範來執行，設置幫你把接口聯調好，再多的增刪改查都能一個 Skill 搞定。

這就是 Skill 的便利性，讓你從重複勞動中解放。

### Skills 的應用場景

Skills 是經驗、規則、最佳實踐的積累，它把你 `“封裝組件”`、`“封裝函數”` 的能力都學會了。

在使用 Skills 時，我們要明確 2 個問題：

1.  **這件事情是否是重複的？**
2.  **這件事情是否能夠標準化？**

當你得到肯定答案的時候，就可以考慮使用 Skills 來簡化工作。

Skills 最適合的應用場景：

![](images/img_6978cb43732b734.awebp)

- `頻繁重複性工作`：比如增刪改查。
- `標準化的輸出`：基於 UI 規範，輸出標準化的組件或功能頁面。
- `知識沉澱`：項目或者公司的開發規範，前端的樣式規範，色彩和字體的使用規範等。

## skills.sh

目前社區已經湧現出了很多官方和個人分享的 Skills。

`skills.sh` 是 Vercel 發佈的一個可視化 AI Skills 平臺，可以說它是 `AI Skills 界的 NPM`。

它彙總了所有的公開 Skills，在上面可以看到 Skills 的信息，下載安裝量，其中包括了前端、後端、DevOps、安全等 Skills，能快速檢索出你想要的 Skills。

![](images/img_6978cb43732ba35.awebp)

## 前端 Skills

### agent-skills

![](images/img_6978cb43732bd36.awebp)

vercel 推出的 skills 項目：

是 React 和 Next.js 的 Skills 集合。包含 8 個類別共 45 條規則，旨在指導自動化重構和代碼生成。

目前 agent-skills 裏面包括三個主要的技能集合：

#### react-best-practices

專門用於 react 和 nextjs：

基於 Vercel 工程團隊的 React/Next.js 性能優化指南，含 40+ 分級規則：

適用場景：

-   新組件 / 頁面開發
-   數據請求實現
-   代碼性能評審、包體積
-   加載速度優化

核心規則：

-   消除請求瀑布（核心）
-   包體積優化（核心）
-   服務端性能
-   客戶端數據請求
-   重渲染優化
-   ...

都是非常實用的。

#### web-design-guidelines

對 UI 代碼進行多維度合規性審計，含 100+ 規則：

適用場景：

-   UI 評審
-   可訪問性檢查
-   設計審計
-   站點最佳實踐校驗

核心規則：

-   無障礙適配
-   焦點狀態
-   表單設計
-   動畫性能
-   排版規範
-   圖片優化
-   暗黑模式適配
-   ...

解決 AI 開發中的各種 UI 問題。

#### vercel-deploy-claimable

實現應用一鍵部署到 Vercel 平臺，支持所有權轉移：

適用場景：

-   應用部署
-   生產環境發佈
-   獲取線上預覽鏈接

核心規則：

-   自動識別 40+ 前端框架
-   生成預覽 URL 和所有權認領 URL
-   自動過濾無用文件（node\_modules/.git）

Github 地址：github.com/vercel-labs…

### vue-skills

![](images/img_6978cb43732c037.awebp)

![](images/img_6978cb43732c338.awebp)

`vue-skills` 是 voidzero 團隊成員發起的項目：

也就是教 AI 怎麼寫 Vue3。

vue-skills 中包含 3 個主要的技能集合：

#### vue-best-practices

核心規則：

-   vue3 最佳實踐
-   Composition API 最佳實踐
-   vue-router 類型處理
-   vue3 代碼可維護性

#### vueuse-best-practices

核心規則：

-   VueUse 組合式 API 的最佳實踐
-   VueUse 常見問題規範

#### pinia-best-practices

核心規則：

-   Vue3 應用中 Pinia的 TypeScript 配置
-   Pinia 的最佳實踐
-   Pinia 常見問題規範

vue-skills Github 地址：github.com/hyf0/vue-sk…

## 如何快速上手 Skills

這些 Skills 包是實打實的能在你的項目中發揮作用的，下面來看看如何快速使用。

1.  安裝

在項目中執行以下命令：

```bash
npx skills add https://github.com/vercel-labs/agent-skills --skill vercel-react-best-practices

```

![](images/img_6978cb43732c639.awebp)

安裝過程中會讓你確認： 選擇支持的 AI 工具。

目前支持的工具包括：

![](images/img_6978cb43732c9310.awebp)

-   Antigravity
-   Codex
-   Cursor
-   Gemini CLI
-   Trae

啓用的範圍:

![](images/img_6978cb43732cc311.awebp)

-   項目
-   全局

安裝完成後，會自動根據你的提示詞來啓用 Skills，無需手動操作。

## 開始編碼

接下來你就可以正常進行你的任務了，比如讓 AI 幫你開發組件，它會自動調用 Skills 來完成任務。

## 企業/個人 Skills 開發

Skills 這麼好用，我們也想自己開發一個 Skills 來提高我們的工作效率。

一個標準的 Skills 文件結構：

```text
my-Skill/
├── Skill.md          # 必需：核心指令
├── rules/            # 可選：規則設置
│   └── crud.md
├── examples/         # 可選：輸入/輸出示例
│   ├── input.md
│   └── output.md
├── templates/        # 可選：可複用的模板
│   └── component.tsx
├── LICENSE.txt       # 可選：開源協議
└── resources/        # 可選：參考文件、運行腳本或素材
    └── style-guide.md

```

你可以自由去設計自己的 Skills，一個 `CRUD` 的 Skill，或者是項目的 `UI` Skill。

## 新的起點

vercel 率先祭出了 skills.sh 這個平臺，更多類 NPM 的 Skills 平臺將會如雨後春筍一般出現，AI 也要有自己的 Skills NPM 平臺，這勢必又是一場話語權的爭奪。

而更多的、更高質量的 Skills 將會出現：

-   3D、2D 模型 skills
-   node skills
-   ios skills
-   ui skills
-   企業 skills
-   個人 skills
-   ...

目前 AI 開發已經不再侷限於大模型的能力，高質量的代碼取決於你給 AI 賦予了什麼技能。

AI + Skills 的開發方式已經不可避免的成爲未來前端開發的新方向。
