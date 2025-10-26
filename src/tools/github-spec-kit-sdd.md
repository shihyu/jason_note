# AI 時代，一定要學會使用 GitHub spec kit — SDD 規格驅動開發

**作者**: Milk Midi
**發布日期**: 2025年10月8日
**閱讀時間**: 8 分鐘
**原文連結**: https://milkmidi.medium.com/ai-%E6%99%82%E4%BB%A3-%E4%B8%80%E5%AE%9A%E8%A6%81%E5%AD%B8%E6%9C%83%E4%BD%BF%E7%94%A8-github-spec-kit-sdd-%E8%A6%8F%E6%A0%BC%E9%A9%85%E5%8B%95%E9%96%8B%E7%99%BC-f2df57cfdf3c

---

![封面圖片](images/image01.png)

大家好，我是奶綠

今天來和大家分享最近很火熱的一種開發模式 **SDD 規格驅動**。

SDD 全名為 **Spec Driven Development**，規格驅動開發，也就是先有 spec 規格書，經由專業的人員審視過後才進行開發。

這樣的優點就是有明確的規格書，AI 能夠更精準的知道這個專案要做些什麼。

來實際走一次看看 SDD：

先到 https://github.com/github/spec-kit 讀一下 README.md 文件。

並請先確認你有安裝 python 環境。

## Step1：Get Started

安裝 specify cli，文件有兩種安裝方式，

在這奶綠我選擇 **Option 2: One-time Usage**，

選擇這個方案是因為這樣可以確保是最新的 specify cli 版本。

```bash
uvx --from git+https://github.com/github/spec-kit.git specify init <PROJECT_NAME>
```

如果想要在現有的專案資料夾使用的話，拿掉 `<PROJECT_NAME>` 並加上參數 `--here` 即可。

```bash
uvx --from git+https://github.com/github/spec-kit.git specify init --here
```

spec-kit 支援多種 AI assistant，選一個你用的上手的吧，奶綠我選用 claude

![選擇 AI assistant](images/image02.png)

選擇 script type，如果你是 Mac，就選 sh，Windows 選 ps

![選擇 script type](images/image03.png)

設定完成後，spec-kit 就有 Next Steps 和你說下一步怎麼做。

![Next Steps](images/image04.png)

接著啟動 Claude Code，使用 slash command 時，就會出現 speckit 相關的指令。

![Claude Code slash commands](images/image05.png)

## Step2: Establish project principles

使用 `/speckit.constitution` 來建立專案的原則。

constitution 翻譯成中文是憲法，也就是整個專案的最高原則，是不可違背的。

官方範例使用了這段：

```
/speckit.constitution Create principles focused on code quality, testing standards, user experience consistency, and performance requirements
```

奶綠我的版本，加了使用 MVP，不要 overdesign，避免 AI 加了過多幻想的功能。

這句 prompt 很重要，所以要說三次：

**使用 MVP，不要 overdesign**
**使用 MVP，不要 overdesign**
**使用 MVP，不要 overdesign**

```
/speckit.constitution 建立高品質，可被 testable，mininum viable product(MVP)，不要 overdesign，一率使用正體中文
```

完成後，就會在專案資料夾自動建立 `.specify/memory/consitution.md` 檔

## Step3: Create the spec

使用 `/speckit.specify` 建立想要的功能，重點放在 **what and why**，這裡不要提到含任何的 tech stack。

奶綠平常有練吉他的習慣，那我們就來開發一個 Web 版 Metronome 吧。

```
/speckit.specify 建立一個 Metronome Web App，拍子需要精準，
需要有 scrollbar 能調整 BPM 的速度，
有 Button 能切換 3 小節或是 4 小節，
第一拍的音效要為重音
```

完成後會在專案建立 `specs/001-metronomne-web-app/spec.md` 和 `requirements.md` 檔。

![生成的 spec 文件](images/image06.png)

這時候 spec-kit 的優點就出現了，如果你的 spec 有不清楚的地方，在這個階段 AI 就會主動提出需要澄清的問題。

這時就可以使用 `/speckit.clarify` 來針對 AI 提出的問題做進一步的說明，讓 spec 更加精準。

而且會自動幫你建立 git branch，真的超推的。

## Step4: Create a technical implementation plan

使用 `/speckit.plan` 建立技術文件，在這就可以決定要用什麼樣的技術開發。

官方範例：

```
/speckit.plan The application uses Vite with minimal number of libraries. Use vanilla HTML, CSS, and JavaScript as much as possible. Images are not uploaded anywhere and metadata is stored in a local SQLite database.
```

奶綠的版本：

```
/speckit.plan 使用 vite, react, typescript, tailwindcss@3 建立 web app，
UI library 使用 shadcn，
使用 vitest 做為 unit-test library，
不要使用 JavaScript setInterval 做為播放拍子的函式，因為時間會不精準
```

完成。

![技術實作計畫](images/image07.png)

## Step5: Break down into tasks

使用 `/speckit.tasks` 建立可執行的任務列表。這裡不需要帶入任何的 prompt 文字，直接輸入該 command line 即可。

完成。會發現 spec-kit 自帶 TDD 開發，真是太讚了，完全不需要另外設定。

![任務列表](images/image08.png)

## Step6: Execute implementaion

使用 `/speckit.implement` 就可以請 AI 開工啦。

這裡 spec-kit 還有些選項能夠讓你選，可以看這個任務的情境，是 feature 開發，還是 POC。

因為奶綠我剛好要出門，又懶的每個 permission allow，就決定打開 claude code yolo mode。

```bash
claude --dangerously-skip-permissions
```

然後跟 AI 說：

```
我等會要出門，希望 2 小時候後所有的 tasks 都可以完成，如果有卡住或是 test 失敗 2 次，你先 skip 掉，並留下 comment：「這個我修不好，需要專業的奶綠大大來處理」，並請忽略所有的 eslint 錯誤，加油，你可以的
```

![實作執行](images/image09.png)

附上有設計師製作的精美 workflow 圖表：

https://github.com/github/spec-kit/issues/467

## 一些奶綠的個人心得：

- 有明確的規格可以讓團隊有個對焦的文件，畢竟每個人對文字的理解是不一樣的，而且 AI 是可以協助理清不明確的需求。

- **plan 這個階段真的超重要的**，這裡就需要專業的 RD 提供精準的 tech stack，像是用 vue 還是 react，用什麼 testing library，用什麼 state manager，這些都是需要 RD 累積的開發經驗。

- 人類在 SDD 模式下，**review 文件變得更重要**，spec-kit 每個 Step 產生的文件都需要專業人員 review，確保是你想要的。

- 最後 Coding 這麼簡單的事，就交給 AI 吧，人類就只要負責喝酒吃餅干，然後最後跟 AI 說，Good job。

## 不要再相信 "不需要程式背景，也可以開發出百萬級應用程式"

下圖是一個社群流傳的圖片，我想身為專業工程師的你，這個發文也只能會心一笑。

![社群流傳圖片](images/image10.png)

祝大家學習愉快，願 AI 與你同在。

---

**標籤**: AI, TDD, SDD, Spec Driven Development

**原文作者**: Milk Midi
**關注數**: 982 followers · 115 following
