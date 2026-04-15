# Bitfinex 放貸（Margin Funding）配對規則與 FRR 機制說明

## 一、整體機制概觀

Bitfinex 的放貸（Margin Funding）是一個點對點資金市場，出借人把資金掛單在「Funding order book」，由需要槓桿的交易者或借款人來吃單。 出借成功後，借款人依約定日利率按天支付利息，利息每天大約在 01:30 UTC 入帳給出借人。[^1][^2][^3][^4]

在這個市場中，系統根據「利率優先 + 期限相容」原則自動撮合雙方，不是 Bitfinex 自行決定利率，而是由出借人報價與借款人願意接受的價格交集決定。[^5][^6][^1]

## 二、出借人可以設定的三個要素

當你在 Funding 頁面建立放貸 Offer 時，主要要設定三個核心參數：金額、日利率與最長天期。[^4]

1. **金額（Amount）**  
   - 你可以選擇要出借的資產幣別（例如 USD、USDT、BTC 等），並輸入出借金額，資金需先在 Funding Wallet 中。[^7]
   - 官方與教學文普遍提到，放貸金額有最低門檻，大約在 150 美元等值附近，太小的金額系統會拒絕創單或無法被有效撮合。[^3][^8]

2. **利率（Rate）**  
   - 以「日利率」方式報價，例如 0.02% per day，介面會同時顯示對應 APR（年化）。[^5][^3]
   - 可選擇：
     - 手動固定利率（Fixed rate）
     - 使用 FRR（Flash Return Rate）
     - FRR Delta Fixed（在 FRR 上加減一個固定差值，如 FRR + 0.001）[^1]

3. **天期（Duration / Period）**  
   - 你設定的是「最長出借天數」，借款人可以在這個上限之內任意使用資金（提早還款即可結束）。[^2][^1]
   - 可選區間大約為 2–120 天，Bitfinex 與教學文都以此範圍示意，短天期流動性通常較高。[^2][^7]

## 三、撮合優先順序：利率優先 + 期限相容

Bitfinex 官方與多篇教學一致指出，Funding 的撮合邏輯類似掛單式交易所，但排序是依「利率」而非「價格」：

- **利率越低的出借 Offer 越容易、越優先被借款人吃單**，因為對借款人來說成本較低。[^1][^5]
- 系統只會在「你的最長出借天期 ≥ 借款人想借的天數」時，才會把你列入可匹配的候選清單。[^6][^1]
- 當同一利率與天期條件下有多筆 Offer，系統按時間先後（先掛先享）依序撮合。[^6]

簡化來看，撮合規則可以理解為：

1. 借款人送出「我要借 X 金額、上限利率 Y、天期 Z」的請求。[^6]
2. 系統在 Funding order book 中，從最低利率開始往上找，篩選出「利率 ≤ Y，且天期 ≥ Z」的 Offer。[^5][^1]
3. 依時間優先順序把借款需求拆分到多筆 Offer 上，直到借滿或沒有合格的 Offer 為止。[^6]

## 四、固定利率（Fixed Rate）放貸的運作

### 1. 出借端設定方式

當你手動輸入日利率，且沒有勾選 FRR 或 FRR Delta 選項時，就是標準的固定利率放貸：

- 你明確指定每天要收多少利息（例如 0.02%/day）。[^1]
- 一旦有借款人吃單並成功借出，整段借款期間的日利率就固定不變，即使市場 FRR 之後大幅上升或下降，也不會影響這筆已成交的借貸。[^4][^1]

### 2. 配對條件與匹配過程

固定利率 Offer 的撮合遵循前述「利率優先 + 期限相容」原則：

- 只要有借款人願意接受你報的利率，且他設定的天期不超過你的最長天期，就可以立即被撮合。[^5][^1]
- 如果你的利率相對市場偏高（對借款人來說成本偏貴），就會排在 order book 後面，需要等到低利率掛單被吃完或市場需求暴增時才比較有機會成交。[^7][^5]

### 3. 利息計算與起算時間

- **固定利率借款一旦撮合成功就立即開始計息**，不論借款人是否已把資金從 Margin Wallet 提出運用。[^9]
- 利息以秒為單位累計，但最低會收至少一小時利息；之後按秒計算，系統每天約在 01:30 UTC 把前一天利息結算給出借人。[^9][^1]

## 五、FRR（Flash Return Rate）機制與放貸方式

### 1. FRR 的定義與計算

Bitfinex 官方把 FRR 描述為：

- 一種「特殊的浮動參考利率」，不是雙方事先約定的固定利率，而是根據「當前所有有效固定利率借貸的金額加權平均」計算出來。[^10]
- FRR 約每小時更新一次，使得利率能跟隨 Funding 市場的實際供需情況。[^10]
- 當某個交易對（例如 BTC/USD）的市場需求上升、槓桿需求變高時，相關幣別的 FRR 也會上升；反之則下降。[^10]

### 2. 出借端使用 FRR 的兩種模式

在建立 Funding Offer 或設定 Auto-renew 時，可以選擇使用 FRR：

1. **FRR（純 FRR）**  
   - 你的 Offer 利率設定為「成交當下的 FRR」，一旦借款成交，整段借款期間利率就固定在那個 FRR 值，不再隨後續 FRR 變動而改變。[^10][^1]
   - 優點是可以避免自己每天調整利率，且大致跟著市場平均水準走，不會報價太離譜。[^1]

2. **FRR Delta Fixed（FRR 差值固定）**  
   - 你可以設定一個「FRR + / − 差值」，例如 FRR + 0.001，表示你願意在 FRR 基礎上多收一點利息，或為了優先成交而設定 FRR − 0.001。[^1]
   - 成交時，實際日利率會是「當下 FRR ± 你設定的差值」，一樣在整段借款期間固定不變。[^1]

### 3. FRR 訂單的撮合特性

Bitfinex 說明指出，FRR 相關的 Funding Offer 具有以下匹配特性：

- FRR Offer 雖然會隨市場利率變化自動調整掛單利率，但**並不保證立即成交**，仍需等到市場借款利率到達或超過該 FRR 水準才會被借款人吃單。[^5][^1]
- 系統會把 FRR 類型的借款請求與 FRR 類型的放貸 Offer 優先互相匹配；固定利率借款則會去吃固定利率的放貸掛單。[^1]
- 對出借人來說，使用 FRR 可以降低自己報錯價格的風險，但在利率快速上行時，有可能短期內成交不到，因為 FRR 是加權平均且有平滑機制，不會馬上追到極端報價。[^10][^1]

## 六、借款人視角：如何發出借款請求

借款人可以透過兩個主要入口取得 Funding：Margin Trading（開槓桿倉位時系統自動借入）與 Bitfinex Borrow（主動抵押資產借幣）。[^8][^4]

1. **Margin Trading 情境**  
   - 當交易者在 Margin 模式下開倉或維持槓桿倉位時，系統會自動根據需要的槓桿金額，在 Funding 市場中尋找合適利率與天期的資金。[^2][^4]
   - 實務上，交易者多半只看到「平均借款利率」與「借款天期」，背後實際上可能是多筆 Funding Offer 被拆分配對的結果。[^2][^6]

2. **Bitfinex Borrow 情境**  
   - 使用者可以主動在 Bitfinex Borrow 介面填寫「想借幣種、金額、天期與願意接受的利率上限」，並以現有資產作為抵押。[^8]
   - 系統同樣會在 Funding order book 中，尋找符合條件（利率、天期、金額）的放貸掛單來撮合。[^8][^6]

在兩種情境下，借款人都不需要手動挑選每一筆 Funding，系統會自動拆單與最適化匹配，以確保借款需求能以最低可用利率被滿足。[^2][^6]

## 七、固定利率 vs FRR：出借實務上的差異

下表整理出借人角度，固定利率與 FRR 的主要差異：

| 面向 | 固定利率（Manual Fixed） | FRR / FRR Delta Fixed |
|------|--------------------------|------------------------|
| 報價方式 | 手動輸入明確日利率 | 以當下 FRR 為基準，自動填入或加減差值[^1][^10] |
| 成交後利率 | 完全固定，不隨市場變動 | 以成交當下 FRR（±差值）鎖定，之後也固定[^1] |
| 報錯價風險 | 高：報太低賺少、報太高難成交 | 較低：大致貼近市場平均，有平滑效果[^1][^10] |
| 成交速度 | 報價偏低時非常快；報高時可能久掛 | 取決於 FRR 相對即時需求，利率上行期可能稍慢[^1][^5] |
| 操作複雜度 |需要自己調整利率，搭配機器人較佳 | 操作簡單，適合被動型出借人[^7] |

## 八、量化策略與實務建議（簡述）

對於想用程式或機器人做 Bitfinex 放貸的量化交易者，可以從以下幾點著手：

- 利率模型：利用 Funding 歷史利率與 FRR 時間序列，建模不同幣種在波動率、交易量高低時的利率分佈，設計動態報價策略。[^11][^12]
- 天期選擇：短天期（2–7 天）流動性高，適合頻繁調整利率；長天期適合在高利率時鎖定收益，但須承擔利率回落與資金鎖定風險。[^7][^2]
- 組合拆分：可以把大額資金拆成多筆不同利率與天期的 Offer，增加部份資金優先成交的機會，同時保留部分資金等待更高利率。[^12][^6]

對一般使用者，若不打算寫機器人、也不想頻繁調整利率，通常建議以 FRR 或 FRR Delta Fixed 搭配 Auto-renew，作為相對省心的被動收入工具，再視市場情況偶爾手動掛一些較高利率短天期固定單。

---

## References

1. [How to Earn with Margin Lending on Bitfinex](https://blog.bitfinex.com/education/how-to-earn-with-margin-lending-on-bitfinex/) - If you’re holding either fiat or cryptocurrency on Bitfinex but not actively trading, Margin Lending...

2. [What Is Bitfinex Margin Funding? A Beginner's Guide | LendPace](https://lendpace.aicclemon.com/en/blog/what-is-bitfinex-margin-funding) - Learn how Bitfinex margin funding works, who borrows your crypto and why, and how you can earn passi...

3. [How to Earn with Margin Lending on Bitfinex - Cryptohopper](https://www.cryptohopper.com/zh-cn/news/how-to-earn-with-margin-lending-on-bitfinex-12551) - If you’re holding either fiat or cryptocurrency on Bitfinex but not actively trading, Margin Lending...

4. [What is Margin Funding](https://support.bitfinex.com/hc/en-us/articles/214441185-What-is-Margin-Funding) - Margin Funding on Bitfinex goes hand in hand with Margin Trading. Through Margin Funding, users with...

5. [How to Earn with Margin Lending on Bitfinex](https://www.cryptohopper.com/ko/news/exchange/bitfinex/12551-how-to-earn-with-margin-lending-on-bitfinex)

6. [AltInvest Blog - How Bitfinex Matches Lending Funds? Behind the ...](https://altinvest.finance/blog/179) - Bitfinex’s P2P lending market lets you lend like a bank, with automatic loan matching based on your ...

7. [Bitfinex Lending Guide: Earn 15-25% APY with Passive Income](https://cryptoguide.business/en/guide/tutorial/bitfinex-lending-guide) - Complete step-by-step guide to using Bitfinex's P2P margin funding feature to earn passive income by...

8. [What is Bitfinex Borrow](https://support.bitfinex.com/hc/en-us/articles/900003195246-What-is-Bitfinex-Borrow) - Bitfinex Borrow is a peer-to-peer (P2P) funding platform that allows you to borrow funds from other ...

9. [Our Fees](https://www.bitfinex.com/fees/?locale=en) - The fees schedule for various Bitfinex services.

10. [What is the Bitfinex Funding Flash Return Rate](https://support.bitfinex.com/hc/en-us/articles/213919009-What-is-the-Bitfinex-Funding-Flash-Return-Rate) - What is the Flash Return Rate (FRR) The Flash Return Rate (FRR) is a special rate used to calculate ...

11. [V2 REST¶](https://bitfinex.readthedocs.io/en/latest/restv2.html)

12. [Bitfinex放貸全攻略-2025年利率優化、風險控管與機器人實戰 ...](https://chainstockalchemy.com/bitfinex-lending-guide-2025/) - 想透過Bitfinex放貸賺取被動收入嗎？本篇2025年最新教學,從利率優化技巧、風險管理,到放貸機器人設定進行全方位解析,助你穩健提升加密資產收益。
