# 630 行程式碼讓 AI 自主做研究：Karpathy AutoResearch 完整解析

凌晨兩點，你盯著終端機裡緩慢跳動的 loss 曲線，等著這一輪訓練跑完，準備手動調一次 learning rate 再重跑。你喝了第四杯咖啡，眼睛發乾，腦中還在盤算：`batch size` 要不要再加大？`depth 12` 會不會比 `depth 8` 好？Muon 最佳化器的 `momentum` 要不要再降一點？

做過機器學習研究的人，對這種場景都不陌生。

然後 Andrej Karpathy 在三月初丟出一個只有 630 行的 Python 腳本，傳達的訊息很直接：這些反覆實驗，現在可以交給 AI 代理自己跑。

這個名為 [autoresearch](https://github.com/karpathy/autoresearch) 的開源專案，在兩天內吸引了超過 860 萬次瀏覽。它不是大型框架，也不是企業平台，而是一個極簡的自動化迴圈，讓 AI 代理在你離開電腦時持續完成機器學習實驗。

更值得注意的是，代理找到的改進，據 Karpathy 的描述，已經超過他自己多年手動調校的結果。

---

## 五分鐘看懂 AutoResearch 在做什麼

AutoResearch 的核心概念可以濃縮成一句話：

**AI 代理讀懂你的訓練程式，提出改進方案，跑一輪實驗驗證，有效就保留，無效就丟棄，然後重複。**

整個儲存庫的核心只有兩個檔案：

| 檔案 | 用途 |
| --- | --- |
| `train.py` | 代理唯一能修改的檔案，包含 GPT 模型定義、最佳化器設定、訓練迴圈等核心邏輯。 |
| `program.md` | 研究方向說明文件，用 Markdown 告訴代理該往哪些方向嘗試。 |

沒有複雜的設定檔，沒有分散式叢集管理，除了 PyTorch 之外幾乎沒有額外依賴。

每一輪實驗的流程如下：

1. 代理讀取 `train.py`，理解目前模型結構與超參數。
2. 根據 `program.md` 提出一個新的改進假設。
3. 修改 `train.py`。
4. 將變更提交到 Git 功能分支。
5. 啟動訓練，固定執行 5 分鐘。
6. 檢查 `val_bpb` 是否改善。
7. 若結果更好就保留 commit，否則捨棄。
8. 回到第一步，繼續下一輪。

以這個節奏來看，一小時大約能跑 12 個實驗，一個晚上可以累積接近 100 次；Karpathy 兩天內總共跑了大約 650 次完整實驗。

這裡最關鍵的設計之一是固定時間預算。不管代理怎麼改模型大小、批次大小或訓練流程，每次都只跑 5 分鐘。這讓所有候選方案都能在同一個硬體條件下直接比較，也等於是在搜尋「這張 GPU 在 5 分鐘內能訓練出來的最佳版本」。

代價也很明確：不同人因為 GPU 不同，結果不能直接橫向比較。但對於本機研究迭代來說，這個取捨非常實用。

---

## 這 630 行程式碼最聰明的地方

「讓 AI 自動跑實驗」本身不是新概念。AutoML、超參數搜尋、NAS（Neural Architecture Search）都已經存在很多年。AutoResearch 真正精準的地方，在於一個非常小但非常重要的設計決策：

**Frozen Metric，也就是凍結評估指標。**

代理可以修改 `train.py` 裡幾乎所有內容，包含模型架構、最佳化器、learning rate、`batch size`，甚至整個訓練流程；但它碰不到最終評估標準 `val_bpb`，也就是 validation bits per byte。

這個限制非常重要。因為如果系統既能改模型，又能改評分標準，那最後得到的「進步」很可能只是作弊。AutoResearch 的設計重點不是讓代理無限制地自由發揮，而是把評估機制放在代理無法汙染的邊界之外。

這其實很像一個縮小版的 AI 對齊問題。當我們讓 AI 最大化某些商業或產品指標時，最擔心的就是它找到形式上達標、實質上失真的捷徑。AutoResearch 用最簡潔的方式示範了一個方向：把關鍵評估指標獨立出來，不讓代理任意改寫。

這也帶來第二個好處。因為指標被凍結，所以人類可以信任不同 commit 之間的比較結果。你隔天早上回來看保留下來的改動時，知道那些數字至少是在同一套評估規則下產生的。

---

## 成效：代理真的比資深研究者更強嗎

先看幾個關鍵數字：

| 指標 | 數值 |
| --- | --- |
| `val_bpb` 改善幅度 | 從 1.0 降到 0.97 |
| 總實驗數 | 約 650 次（兩天） |
| 單次實驗時間 | 固定 5 分鐘 |
| 每小時實驗量 | 約 12 次 |

`val_bpb` 從 1.0 降到 0.97，看起來幅度不大，但在這種語言模型訓練指標上，0.03 的改善其實相當可觀，尤其這還是建立在已經經過 Karpathy 手動優化過的基準之上。

更重要的是，Karpathy 提到，在 `depth 12` 小模型上找出的改進，可以順利遷移到 `depth 24` 的更大模型。這表示代理找到的不只是特定尺寸模型的偶然技巧，而是更通用的訓練或架構改善。

當然，這裡還是要講清楚界線。代理目前擅長的是超參數調整、結構微調與訓練流程改寫，不是憑空發明新理論，也不是提出全新的模型家族。但如果問題是「給定一份訓練程式，把它調到更好」，那麼大量自動實驗搭配語意推理，確實已經能在某些場景超過人類專家。

---

## 社群為什麼反應這麼大

AutoResearch 爆紅的原因，不只在技術本身，也在於它的展示方式足夠簡單、足夠直接。

Karpathy 在 X 上發文後，兩天內累積超過 860 萬次瀏覽。整個 AI 圈很快開始用「Karpathy Loop」來稱呼這類自動實驗迴圈。[VentureBeat 的報導](https://venturebeat.com/technology/andrej-karpathys-new-open-source-autoresearch-lets-you-run-hundreds-of-ai)也直接把它形容成具有重大影響的做法。

Reddit 上幾個社群的討論尤其熱烈：

- `r/LocalLLaMA`：偏重技術細節與可重現性。
- `r/singularity`：討論這是否代表更早期的研究自動化拐點。
- `r/AgentsOfAI`：聚焦在代理框架的設計與擴充可能。

不過，批評聲音也很清楚，主要集中在三點：

- 這個概念並不算全新，類似的多代理研究框架早就有人做過。
- 目前範圍仍然偏窄，主要聚焦在小型 GPT 訓練場景。
- 社群對 AI hype 的疲勞感，也讓部分人對這類敘事保持保留態度。

即使如此，AutoResearch 仍然抓住了一個很關鍵的點：它把原本抽象的「AI 自動做研究」變成一個任何人都看得懂、也有機會自己重現的工作流。

---

## 更大的野心：從一個研究生到一個研究社群

AutoResearch 發佈後不久，Karpathy 又提出下一步構想：讓大量代理在不同機器上非同步協作，像 SETI@home 一樣把全球硬體資源串起來，共同探索研究空間。

這個方向的核心想法是：

- 每個代理在自己的硬體上跑實驗。
- 成功與失敗的結果都公開回報。
- 其他代理再從目前全域最佳設定接手繼續迭代。

社群很快就開始實作各種延伸版本，例如：

- 分散式 fork，例如 `autoresearch-at-home`。
- 把流程搬到點對點網路上運行。
- 嘗試在 Apple Neural Engine 等不同硬體上執行。
- 使用地端 LLM 而不是商用 API，降低實驗成本。

但如果真的要做成分散式研究網路，會遇到一個很實際的問題：AutoResearch 現在依賴固定 5 分鐘的時間預算，而不同硬體在 5 分鐘內能完成的訓練量差很多。H100 跑出來的結果，要怎麼跟 RTX 4090 或其他消費級 GPU 的結果放在同一個排名系統裡，這件事並不容易。

---

## 它真正改變的是人的角色

退一步看，AutoResearch 最值得思考的地方，不是某個訓練技巧，而是它重新分配了人與機器的工作。

過去做機器學習研究時，人類通常要自己讀論文、想假設、改程式、跑實驗、看結果、再調參數。你是實驗執行者，也是調參操作員。

AutoResearch 之後，人類更像是在寫 `program.md`。你的主要工作變成定義研究方向、設定約束條件、描述值得探索的假設，然後讓代理去做高頻率的實驗執行。

這也對應到軟體開發領域正在發生的變化。隨著 AI 程式助理越來越強，開發者的價值正逐漸從「親手寫每一行程式」轉向「定義問題、設計系統、設下正確約束」。AutoResearch 只是把這個趨勢更明確地投射到機器學習研究上。

而其中最值得記住的，還是 frozen metric 這個設計理念：**約束不是阻礙，約束本身就是系統智慧的一部分。**

如果下一次你又在半夜盯著 loss 曲線，也許真正該做的不是再手動試一次 learning rate，而是先把研究目標與評估邊界寫清楚，然後把反覆驗證交給代理。

---

## 一句話總結：AutoResearch 能拿來幹嘛？

**讓 AI 代理自動跑機器學習實驗，取代人類半夜手動調參。**

### 四大用途

1. **超參數自動調校**
   - learning rate、batch size、momentum 等，代理自己試、自己評估
   - 一晚上跑 ~100 次實驗，比人類手動快幾十倍

2. **模型架構探索**
   - 自動嘗試不同 depth、width、attention head 數等結構組合
   - 不需要你每次手改 `train.py` 再重跑

3. **訓練流程優化**
   - 自動修改 optimizer 設定、scheduler、warmup 策略等
   - 找出你自己可能想不到的組合

4. **小模型的快速 baseline 搜尋**
   - 固定 5 分鐘 budget，讓每個假設都在相同條件下競爭
   - 找到的改進可以遷移到更大的模型

### 關鍵設計：Frozen Metric

代理可以改 `train.py` 的任何東西，但**不能碰評估指標 `val_bpb`**。
這樣才能確保「改進」是真實的，不是代理自己把評分標準改鬆來作弊。

### 你的角色改變

| 過去 | AutoResearch 之後 |
|------|------------------|
| 親手改程式、調參數 | 寫 `program.md` 定義研究方向 |
| 盯著 loss 等結果 | 隔天看代理保留下來的 commit |
| 一晚最多試幾次 | 一晚可跑 100 次實驗 |

> 簡單說：你睡覺，代理幫你做實驗。你只需要說清楚「往哪個方向探索」，剩下的執行交給它。

---

## 延伸閱讀

- [karpathy/autoresearch GitHub Repo](https://github.com/karpathy/autoresearch) - 官方原始碼
- [VentureBeat: AutoResearch lets you run hundreds of AI experiments a night](https://venturebeat.com/technology/andrej-karpathys-new-open-source-autoresearch-lets-you-run-hundreds-of-ai) - 媒體報導
- [The Frozen Metric of Autoresearch](https://hybridhorizons.substack.com/p/the-frozen-metric-of-autoresearch) - 凍結指標的分析
- [MarkTechPost: 630-Line Python Tool for Autonomous ML Experiments](https://www.marktechpost.com/2026/03/08/andrej-karpathy-open-sources-autoresearch-a-630-line-python-tool-letting-ai-agents-run-autonomous-ml-experiments-on-single-gpus/) - 技術架構整理
- [Karpathy on X: SETI@home Vision](https://x.com/karpathy/status/2030705271627284816) - 分散式協作願景
- [r/LocalLLaMA Discussion](https://www.reddit.com/r/LocalLLaMA/comments/1rowp28/karpathy_autoresearch/) - 社群討論串
- [Getting Started Full Guide](https://medium.com/modelmind/getting-started-with-andrej-karpathys-autoresearch-full-guide-c2f3a80b9ce6) - 入門教學
