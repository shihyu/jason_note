# Bitfinex P2P Lending (Margin Funding) — Matching Rules Research

## 研究目標
理解 Bitfinex P2P 借貸的利率匹配規則，特別是掛單（offer/bid）如何成交。

---

## 一、官方與參考來源

| 來源 | URL |
|------|-----|
| Bitfinex Help Center — What is Margin Funding | https://support.bitfinex.com/hc/en-us/articles/214441185-What-is-Margin-Funding |
| Bitfinex Help Center — How to reserve Funding on Bitfinex | https://support.bitfinex.com/hc/en-us/articles/900000898423-How-to-reserve-Funding-on-Bitfinex |
| Bitfinex Help Center — What is the Bitfinex Funding Flash Return Rate | https://support.bitfinex.com/hc/en-us/articles/213919009-What-is-the-Bitfinex-Funding-Flash-Return-Rate |
| Bitfinex Help Center — What is the Bitfinex Funding FRR Delta | https://support.bitfinex.com/hc/en-us/articles/115003284729-What-is-the-Bitfinex-Funding-FRR-Delta |
| Bitfinex Blog — How to Earn with Margin Lending | https://blog.bitfinex.com/education/how-to-earn-with-margin-lending-on-bitfinex/ |
| Bitfinex API Docs — Submit Funding Offer | https://docs.bitfinex.com/reference/rest-auth-submit-funding-offer |
| Bitfinex API Docs — Flag Values | https://docs.bitfinex.com/docs/flag-values |
| Bitfinex API Docs — Public Book | https://docs.bitfinex.com/reference/rest-public-book |
| AltInvest — Bitfinex 匹配規則詳解 | https://altinvest.finance/blog/179 |

---

## 二、匹配規則核心邏輯

### 2.1 官方可確認的匹配條件：Period + Rate

Bitfinex 官方 Help Center 明確寫的是：
- Funding Bids 與 Offers 要成交，**Rate 與 Period 都要 match**
- 如果 Bid 要 10 天，必須對到 **10 天或更長** 的 Offer
- 系統在保證金借款時，會以 **best available rates** 自動保留 funding

> 注意：官方文件**沒有公開完整撮合引擎規則**，例如是否明文採用「price-time priority」。因此本文凡是「最低 offer 先成交 / 最高 bid 先成交」的描述，都應視為根據 order book 與 best available rates 的**高可信推論**，不是官方明文規則。

### 2.2 期限匹配條件

借款人請求的期限（duration）**必須** ≤ 出借人設定的最長期限。

**範例：**
| 借款人請求期限 | 出借人設定期限 | 是否匹配 |
|--------------|--------------|--------|
| 10 天 | 10 天以上 | ✅ 匹配 |
| 10 天 | 5 天 | ❌ 不匹配（出借人不願借那麼久） |
| 15 天 | 30 天 | ✅ 匹配（出借人願意借更久） |

### 2.3 FRR 與固定利率 **不能** 交叉匹配

| 類型 | 說明 |
|------|------|
| **固定利率（Fixed Rate）** | 明確寫死的利率，如 `0.05%` / 天 |
| **FRR（Flash Return Rate）** | Bitfinex 的動態利率參考值，每小時更新 |

**關鍵限制：**
- 固定利率 Bid **無法** 與 FRR Offer 成交
- FRR Bid **無法** 與 固定利率 Offer 成交
- FRR Bid 與 FRR Offer ✅ **可以成交**（同為 FRR 類型）

> 官方規則：*"a fixed rate bid/offer cannot match with a Flash Return Rate (FRR) offer/bid"* — 防火牆只存在於「固定利率 ↔ FRR」之間，同屬 FRR 市場的雙方可正常匹配。

---

## 三、FRR（Flash Return Rate）系統

### 3.1 FRR 是什麼？
FRR 是 Bitfinex 的動態利率參考指標，**每小時更新一次**。

但官方來源對其精確定義有兩種說法：
- Help Center：FRR 是 **all active fixed-rate fundings weighted by amount** 的平均
- 官方 Blog：FRR 是 **the weighted average of the most recent funding trades**，並做平滑處理以避免尖峰

因此較穩妥的寫法是：
> **FRR 是 Bitfinex 用於 Funding 市場的動態參考利率，每小時更新；官方不同來源對其底層計算口徑描述不完全一致。**

### 3.2 FRR 訂單類型

| 類型 | 說明 |
|------|------|
| **FRR（UI 選項）** | 以成交當下的 FRR 為基準；成交後該筆 loan 利率固定 |
| **FRRDELTAVAR** | 以 FRR + 溢價/折價掛單，匹配後利率會隨 FRR 調整而浮動 |
| **FRRDELTAFIX** | 以 FRR + 溢價/折價掛單；**成交前** 會跟 FRR 更新，**成交後** 固定 |

> 補充：
> - UI/Blog 用語有 `FRR`、`FRR Variable`、`FRR Fixed`
> - API `submit funding offer` 文件明列的 `type` 是 `LIMIT`、`FRRDELTAVAR`、`FRRDELTAFIX`
> - 因此 UI 名稱與 API 名稱並不是 1:1 逐字對應

---

## 四、利息計算公式

### 4.1 出借人（Provider）實際所得

```
實際所得 = 本金 × (利率/100) × (秒數 / 86400) × 0.85
```

| 參數 | 說明 |
|------|------|
| `本金` | 借貸金額 |
| `利率` | 日利率（%），如 `0.05` 表示 0.05% / 天 |
| `秒數` | 實際借貸秒數（精確到秒） |
| `86400` | 一天的秒數 |
| `0.85` | 出借人實得比例（85%），Bitfinex 收取 15% 手續費 |

**範例：** 借 $1,000、利率 0.05%/天、借 15 天：
```
本金 × rate% × (sec/86400) × 0.85
= 1000 × 0.0005 × (15×86400 / 86400) × 0.85
= 1000 × 0.0005 × 15 × 0.85
= $6.375（15天總利息）
```

### 4.2 手續費結構

| 訂單類型 | Bitfinex 手續費 | 出借人實得 |
|----------|----------------|------------|
| 普通 Offer | 15% | **85%** (0.85) |
| Hidden Offer | 18% | **82%** (0.82) |

> ⚠️ Hidden Offer 的 `0.85` 需改為 `0.82`，否則計算會多算。

### 4.3 最低借貸金額
Bitfinex 借貸的最低門檻為 **$150 USD 等值**。

### 4.4 借貸期限範圍
可借期限為 **2 天 ～ 120 天**。

---

## 五、Matching Rules 摘要

### 匹配流程（官方已證實 + 推論）

```
第一步：檢查 Period 與 Rate 是否可匹配（官方明文）
└── Bid 與 Offer 的 Rate / Period 不可衝突

第二步：系統以 best available rates 完成匹配（官方明文）
└── book 呈現與一般 order book 一致，故可合理推論價格更優者優先
```

### 期限匹配條件
- 借款人請求的期限（duration）**必須** ≤ 出借人設定的最長期限
- 例如：借款人要 15 天，出借人願借最長 30 天 → ✅ 匹配

### 利率匹配邏輯
- 官方明文只有：**Rate 與 Period 需要 match**
- 官方也明文表示：系統會以 **best available rates** 自動保留 funding
- 因此可高可信推論：在滿足 Period 的前提下，**價格較優的一側更容易先成交**
- 但 Bitfinex **未公開完整撮合規則**，故不應把「最低 Offer 一定先成交」寫成官方明文事實

### 利率競價範例

情境：3 個出借人都掛 P30，借款人掛 Bid: 0.06%，請求 P15

| 出借人 | Offer 利率 | 排序（從低到高） |
|--------|-----------|-----------------|
| Lender A | 0.04% | 1️⃣ 最便宜，先成交 |
| Lender B | 0.05% | 2️⃣ |
| Lender C | 0.06% | 3️⃣ 最貴，後成交 |

**較合理的推論：** 若 book 中存在符合 period 條件的 0.04% offer，系統大概率會先以更優價格成交，而不是直接用借款人的 0.06% 上限成交。

> **實務意義：**
> - 出借人利率設太低 → 優先成交，但賺得少
> - 出借人利率設太高 → 匹配不到，被市場更低的 Offer 擠掉

### FRR 與固定利率**不能**交叉匹配
| 類型 | 說明 |
|------|------|
| **固定利率（Fixed Rate）** | 明確寫死的利率，如 `0.05%` / 天 |
| **FRR（Flash Return Rate）** | Bitfinex 的動態利率參考值，每小時更新 |

**關鍵限制：**
- 固定利率 Bid **無法**與 FRR Offer 成交
- FRR Bid **無法**與固定利率 Offer 成交
- FRR Bid 與 FRR Offer ✅ 可以成交（同屬 FRR 市場）
- 防火牆只存在於「固定利率 ↔ FRR」之間，同類型之間可正常匹配

### 手續費层级
| 訂單類型 | 手續費 | 出借人實得 |
|----------|--------|------------|
| 普通 Offer | 15% | 85% |
| Hidden Offer | 18% | 82% |

---

## 六、實例說明

### 情境設定

| 角色 | 掛單類型 | 利率 | 期限 | 金額 |
|------|----------|------|------|------|
| 出借人（Lender） | Offer | 0.05% / 天 | 最長 30 天 | $1,000 USD |
| 借款人（Borrower） | Bid | 0.06% / 天 | 請求 15 天 | $1,000 USD |

### 匹配判斷

| 條件 | 判斷 | 說明 |
|------|------|------|
| 利率 | ✅ 0.06% ≥ 0.05% | 借款人願付 ≥ 出借人願收 |
| 期限 | ✅ 15天 ≤ 30天 | 借款期限被出借人最長期限覆蓋 |
| 類型 | ✅ 同為固定利率 | 固定與 FRR 不能交叉匹配 |

### 成交結果

- **日利率：** 0.05%（以出借人報價成交）
- **結算天數：** 15 天
- **出借人實得利息：**
```
本金 × rate% × (sec/86400) × 0.85
= 1000 × 0.0005 × (15×86400 / 86400) × 0.85
= 1000 × 0.0005 × 15 × 0.85
= $6.375（15天總利息）
```
- **借款人應付利息：** $7.50
- **Bitfinex 手續費：** $1.125（15%）

### 期限匹配範例

出借人掛 **P120（最長 120 天）**：

| 借款人掛的期限 | 是否匹配 | 原因 |
|---------------|---------|------|
| P2 | ✅ | 2 ≤ 120 |
| P15 | ✅ | 15 ≤ 120 |
| P30 | ✅ | 30 ≤ 120 |
| P60 | ✅ | 60 ≤ 120 |
| P90 | ✅ | 90 ≤ 120 |
| P120 | ✅ | 120 ≤ 120 |

> **關鍵：借款人不需要掛跟出借人相同的期限。只要「請求期限 ≤ 出借人願借的最長期限」就會匹配。**

---

## 七、出借期限策略分析

### 長期出借（P60 ～ P120）

| 優點 | 缺點 |
|------|------|
| 匹配成功率最高（覆蓋 2-120 天所有借款人） | 資金鎖定時間長，流動性低 |
| 不需要頻繁重新掛單 | 若市場利率上升，無法及時調整 |
| 適合長期不動用的閒置資金 | 借款人提前還款時，資金可能空等 |

**適合情境：** 閒置資金、不在乎短期流動性、懶人策略

### 短期出借（P2 ～ P15）

| 優點 | 缺點 |
|------|------|
| 資金回籠快，流動性高 | 匹配成功率較低（只能匹配短期借款人） |
| 若市場利率上升，可快速重新掛單 | 需要頻繁監控和調整掛單 |
| 適合短期可能需要動用資金的場合 | 可能出現資金空等期（掛單未匹配） |

**適合情境：** 資金短期有其他用途、預期利率會上升、願意頻繁操作

### 中期出借（P30 ～ P60）

| 優點 | 缺點 |
|------|------|
| 平衡流動性與匹配率 | 各方面都中等，沒有特別突出 |
| 不需頻繁操作 | - |

**適合情境：** 多數普通用戶的一般選擇

### 實務建議

1. **資金閒置且長期不看盤** → 掛 P120，利率設市場均值，省心
2. **資金可能短期動用** → 掛 P15～P30，保持流動性
3. **預期利率會上升** → 掛短天期（如 P7～P15），到期後可重新以更高利率掛單
4. **同時掛多筆** → 可以分散風險，例如：
   - $700 掛 P120（長期鎖定）
   - $300 掛 P15（保持流動性）

---

## 七之二、借款人期限策略（P120 能當萬用選項嗎？）

### 核心問題
> 借款人是不是先借 P120 就好？可以隨時還，何必掛短天期？

**結論：可以隨時還，但 P120 並不是「免費的最大彈性」，有隱性成本。**

### ✅ 優點

| 項目 | 說明 |
|------|------|
| **上限彈性大** | 最多可用 120 天，不用擔心中途被系統強制到期 |
| **可提前還款** | 官方明確允許：*"borrowers can return funds at any time before the maximum lending period ends"* |
| **免展期麻煩** | 不需要每 2/7/30 天重新借一次，省掉重複競價、滑價風險 |
| **對沖不確定性** | 若持倉時間不確定（可能 3 天、也可能 2 個月），P120 一次解決 |

### ❌ 缺點（重點）

| 項目 | 說明 |
|------|------|
| **利率較貴** | Funding book 裡長天期 offer 通常利率較高。出借人鎖資金越久風險越大，會要求溢價 → 借款人掛 P120 bid 配對到的實際成交利率會比 P2/P7 高 |
| **流動性差** | 短天期 offer 數量遠多於長天期，P120 可能掛很久才匹配到、或只能以市場最高利率成交 |
| **最低 1 小時利息** | Bitfinex 對「手動提前歸還」收取最少 1 小時利息，防止刷量套利。即使你借 10 秒就還，也要付 1 小時的錢 |
| **被迫成交到高價 offer** | 長天期位在 order book 較稀疏的區間，容易被 FRR/高利率 offer 吃掉 |
| **無法縮短鎖定成本** | 雖然可以早還，但沒還之前利息照跳。若市場利率一路下跌，你被鎖在當初較高的成交利率上 |
| **沒有長期折扣** | 和傳統金融不同，crypto funding 沒有「長天期因為穩定所以打折」的概念，剛好相反 |

### 實務建議

| 情境 | 建議期限 |
|------|---------|
| 確定只借 1–3 天（短線操作） | **P2 最便宜**，利率通常最低 |
| 中期持倉（約 1–2 週） | P7 ~ P15，平衡流動性與利率 |
| 持倉時間完全不確定、但最長不超過 1 個月 | P30 |
| 真的要長期持有保證金、懶得管 | P120，但要接受高利率 |
| 預期市場利率會下跌 | **絕對不要掛 P120**，會被鎖在高利率 |
| 預期市場利率會上漲 | 可考慮 P120 鎖成本，但前提是當下利率不算高 |

### 關鍵觀念

> **「隨時能還」≠「免費的長期選擇權」。**
> 你為 P120 付出的溢價，就是這個「提前歸還權利」的價格。若你確定只借 3 天，掛 P3 或 P7 通常更划算。

### 出借人 vs 借款人 期限邏輯對照

| 角色 | 掛長天期（P120） | 掛短天期（P2~P15） |
|------|-----------------|-------------------|
| **出借人** | 優：匹配率最高、覆蓋所有借款人 ❌ 缺：資金被鎖、錯過利率上升 | 優：流動性高、跟得上利率變化 ❌ 缺：匹配率低 |
| **借款人** | 優：最大彈性、免展期 ❌ 缺：利率貴、流動性差 | 優：利率便宜、匹配快 ❌ 缺：需自己管理展期 |

> 雙方對長短天期的動機**恰好相反**：出借人希望長期鎖高利率，借款人希望短期拿低利率。Funding book 的均衡價就是從這個張力中產生的。

---

## 八、相關 API 端點

| 操作 | API 端點 | 認證 |
|------|---------|------|
| 提交 Funding Offer / Bid | `POST /v2/auth/w/funding/offer/submit` | ✅ |
| 取消 Funding Offer | `POST /v2/auth/w/funding/offer/cancel` | ✅ |
| 查詢自己的 Active Offers | `POST /v2/auth/r/funding/offers/{symbol}` | ✅ |
| 查詢自己已放出的 Credits | `POST /v2/auth/r/funding/credits/{symbol}` | ✅ |
| 查詢 Funding Book（市場深度） | `GET /v2/book/{symbol}/P0` | ❌ public |
| 查詢 FRR（在 Funding Ticker 中） | `GET /v2/tickers?symbols=fUSD` | ❌ public |

> 備註：借款人（margin trader）通常不直接掛 bid，系統會在借用保證金時自動吃掉 funding book 上的 offer。若要主動掛 Funding Bid（即 `amount` 為負值的 offer），仍是透過 `submit` 端點，只是 amount 帶負號。

---

## 九、官方文檔索引

| 文檔 | URL | 驗證內容 |
|------|-----|---------|
| What is Margin Funding | https://support.bitfinex.com/hc/en-us/articles/214441185-What-is-Margin-Funding | 匹配條件、FRR 隔離、手續費、最低金額 |
| How to reserve Funding on Bitfinex | https://support.bitfinex.com/hc/en-us/articles/900000898423-How-to-reserve-Funding-on-Bitfinex | `best available rates`、Rate/Period match |
| Margin Funding interest on Bitfinex | https://support.bitfinex.com/hc/en-us/articles/115004554309-Margin-Funding-interest-on-Bitfinex | 利息計算公式 |
| How are Funding interest earnings and fees calculated | https://support.bitfinex.com/hc/en-us/articles/360024039494-How-are-the-Funding-interest-earnings-and-fees-calculated-at-Bitfinex | 利息公式驗證 |
| Margin Funding on Bitfinex | https://support.bitfinex.com/hc/en-us/articles/115003428165-Margin-Funding-on-Bitfinex | 期限範圍 2-120 天 |
| What is the minimum offer for Funding | https://support.bitfinex.com/hc/en-us/articles/213918949-What-is-the-minimum-offer-for-Funding | 最低金額 $150 |
| What is the Bitfinex Funding Flash Return Rate | https://support.bitfinex.com/hc/en-us/articles/213919009-What-is-the-Bitfinex-Funding-Flash-Return-Rate | FRR 定義（Help Center 版本） |
| What is the Bitfinex Funding FRR Delta | https://support.bitfinex.com/hc/en-us/articles/115003284729-What-is-the-Bitfinex-Funding-FRR-Delta | FRRDELTAFIX / FRRDELTAVAR 行為 |
| How to Earn with Margin Lending | https://blog.bitfinex.com/education/how-to-earn-with-margin-lending-on-bitfinex/ | 官方 Blog |
| Submit Funding Offer (API) | https://docs.bitfinex.com/reference/rest-auth-submit-funding-offer | API 端點 |
| Flag Values | https://docs.bitfinex.com/docs/flag-values | `No Var Rates` 旗標 |
| Public Book | https://docs.bitfinex.com/reference/rest-public-book | funding book 公開深度資料 |

---

### ⚠️ 2026-04-15 驗證聲明

本文檔以下內容已通過 Bitfinex 官方 Support Center、API Docs 與即時公開 API 交叉驗證：
- ✅ Rate 與 Period 都需要 match
- ✅ 若 Bid 要 10 天，需對到 10 天或更長的 Offer
- ✅ 系統會以 `best available rates` 自動保留 funding
- ✅ FRR 與固定利率不能交叉匹配（但 FRR↔FRR、固定↔固定 可成交）
- ✅ 利息計算公式：
  - 出借人：`amount × (rate/100) × (seconds/86400) × 0.85`
  - 借款人：`amount × (rate/100) × (seconds/86400)`
- ✅ 最低借貸金額：$150 USD 等值
- ✅ 借貸期限：2–120 天
- ✅ 手續費：普通 15%，Hidden Offer 18%
- ✅ FRRDELTAFIX：**成交前** 會隨 FRR 更新，**成交後** 固定
- ✅ API 端點：`POST /v2/auth/w/funding/offer/submit`

以下內容僅能視為**高可信推論**，不是 Bitfinex 官方明文：
- ⚠️ 滿足 period 條件後，較優價格（例如較低 offer）會優先成交
- ⚠️ 「最高 bid 配最低 offer」屬 order book 與 `best available rates` 的自然解讀，但官方未公開完整撮合演算法

### 2026-04-15 即時公開 API 快照

抓取時間：`2026-04-15 09:14:35 UTC`

- `GET /v2/ticker/fUSD`
  - `FRR = 0.0004514821917808219`
  - `best bid = 0.000165`, `bid_period = 120`, `bid_size = 20630355.96591695`
  - `best ask = 0.000105`, `ask_period = 5`, `ask_size = 1554057.96882425`
  - `last_price = 0.00015299`
- `GET /v2/book/fUSD/P0?len=25`
  - bid 範例：`[0.000165,120,1,-4947519.86764454]`
  - bid 範例：`[0.000165,30,1,-3441996.67568403]`
  - ask 範例：`[0.000106,5,1,4002]`
  - ask 範例：`[0.00010698,2,2,1500]`

這些即時數據至少證明：
- Funding book 真的同時存在 `rate / period / amount`
- 市場目前呈現典型 order book 結構：bid 在高端、ask 在低端
- 不同 period 的單會同時存在於 book 中，period 確實是撮合條件之一

---

## 十、規則總結

### 出借人（Lender）操作守則

| 項目 | 規則 |
|------|------|
| **掛單類型** | Offer（固定利率）或 FRR 系列 |
| **期限設定** | 設最長天數（最大覆蓋範圍） |
| **利率定價** | 觀察 FRR，設低於 FRR 才能優先成交 |
| **匹配條件** | 借款人請求期限 ≤ 出借人最長期限 |
| **成交優先** | 官方僅明說 `best available rates`；較優價格優先屬高可信推論 |
| **實得利息** | `本金 × (利率/100) × (秒數/86400) × 0.85` |
| **手續費** | 普通 Offer 15%，Hidden Offer 18% |

### 匹配核心邏輯

```
1. 檢查 Rate / Period 是否可匹配
   Period 不足或 Rate 不合 → 不成交

2. 系統以 best available rates 成交
   更細的排序規則官方未完整公開
```

### 關鍵限制

- ❌ FRR 與固定利率**不能**交叉匹配
- ❌ 借款期限**不能超過**出借人設定的最長期限
- ❌ 利率設太高會**匹配不到**（被市場更低利率擠掉）
- ❌ 期限設太短會**匹配不到**（覆蓋範圍不足）

### 實務檢查清單

出借前確認：
- [ ] 利率是否低於/等於市場 FRR？
- [ ] 期限是否夠長（覆蓋目標借款人）？
- [ ] 是否選擇正確的訂單類型（固定利率 vs FRR）？
- [ ] 金額是否 ≥ $150 USD？

---

## 十一、固定利率 vs FRR 比較

### 訂單類型總覽

| 類型 | 市場 | 利率特性 | 適合情境 |
|------|------|---------|---------|
| **固定利率（LIMIT）** | 固定市場 | 明確寫死，不會變 | 一般用戶、懶人策略 |
| **FRR（UI 選項）** | FRR 市場 | 成交當下以 FRR 定價，成交後固定 | 想直接跟市場 FRR |
| **FRRDELTAVAR** | FRR 市場 | 隨 FRR 浮動調整 | 想跟隨市場動態調整 |
| **FRRDELTAFIX** | FRR 市場 | 成交前隨 FRR 更新，成交後固定 | 進階玩家 |

### 固定利率（LIMIT）與 FRR 市場隔離

```
┌─────────────────────────────────────┐
│         FRR 市場                    │
│  FRR / FRRDELTAVAR / FRRDELTAFIX   │
│  （浮動利率）                       │
└─────────────────────────────────────┘
              ✖ 不能交叉匹配
┌─────────────────────────────────────┐
│       固定利率市場（LIMIT）           │
│  固定 Bid  ←→  固定 Offer         │
│  （明確寫死的利率）                  │
└─────────────────────────────────────┘
```

**不能跨市場匹配：**
- ❌ FRR Bid 無法與 固定利率 Offer 成交
- ❌ FRR Offer 無法與 固定利率 Bid 成交
- ❌ 利率就算一模一樣也不行

### lending-bot 屬於哪種？

**lending-bot 使用的是「固定利率（LIMIT）」**

```python
# order_manager.py
body = {
    "type": "LIMIT",        # ← 固定利率
    "symbol": self.symbol,
    "amount": f"{amount:.2f}",
    "rate": daily,           # 年化 % 轉成每日利率
    "period": period_days,
}
```

**lending-bot 的掛單邏輯：**

| 項目 | 方式 |
|------|------|
| 訂單類型 | `LIMIT`（固定利率） |
| 利率計算 | 年化 % → 轉換成每日利率 |
| 期限 | 手動設定（short / long strategy） |
| FRR 用途 | 僅作為**定價參考**，不直接使用 FRR 掛單 |

```python
# user_worker.py - 利率設定參考 FRR
if self._frr_ann_pct > 0:
    return max(self.long_min_rate, self._frr_ann_pct)
```

### 實務意義

| 你的 lending-bot | 說明 |
|-----------------|------|
| 觀察 FRR | ✅ Bot 會抓 FRR 來決定利率 |
| 但掛 LIMIT | ✅ 實際掛出去的是固定利率單 |
| 只能跟固定利率成交 | ✅ 無法與 FRR 市場的人匹配 |

> **重點：lending-bot 屬於「固定利率」市場，只能跟另一個固定利率的借款人/出借人匹配，無法與 FRR 市場的人成交。**
