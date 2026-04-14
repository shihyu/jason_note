# Bitfinex P2P Lending (Margin Funding) — Matching Rules Research

## 研究目標
理解 Bitfinex P2P 借貸的利率匹配規則，特別是掛單（offer/bid）如何成交。

---

## 一、官方文檔來源

| 來源 | URL |
|------|-----|
| Bitfinex Help Center — What is Margin Funding | https://support.bitfinex.com/hc/en-us/articles/214441185-What-is-Margin-Funding |
| Bitfinex Blog — How to Earn with Margin Lending | https://blog.bitfinex.com/education/how-to-earn-with-margin-lending-on-bitfinex/ |
| Bitfinex API Docs — Submit Funding Offer | https://docs.bitfinex.com/reference/rest-auth-submit-funding-offer |
| AltInvest — Bitfinex 匹配規則詳解 | https://altinvest.finance/blog/179 |

---

## 二、匹配規則核心邏輯

### 2.1 優先順序：利率 Rate → 期限 Period

**匹配公式（口語化）：**
> 系統將 **願意支付最高利率** 的借款人，與 **接受最低利率** 的出借人進行配對。

- 借款人掛 **Bid**（願意支付的利率）
- 出借人掛 **Offer**（願意接受的利率）
- 當 Bid ≥ Offer 時，可能成交

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
| **FRR（Flash Return Rate）** | 動態利率，根據近期借貸成交加權平均計算，每小時更新 |

**關鍵限制：**
- FRR Bid **無法** 與 FRR Offer 成交（兩者都是浮動利率）
- 固定利率 Bid **無法** 與 FRR Offer 成交
- FRR Bid **無法** 與固定利率 Offer 成交

> 固定與浮動之間有防火牆，必須兩端都是同類型才能匹配。

---

## 三、FRR（Flash Return Rate）系統

### 3.1 FRR 是什麼？
FRR 是 Bitfinex 的動態利率參考指標，根據過去一段時間內所有借貸成交的利率加權平均計算得出，**每小時更新一次**。

### 3.2 FRR 訂單類型

| 類型 | 說明 |
|------|------|
| **FRR LIMIT** | 直接以 FRR 為基準的限價單，利率固定不變 |
| **FRRDELTAVAR** | 以 FRR + 溢價/折價掛單，匹配後利率會隨 FRR 調整而浮動 |
| **FRRDELTAFIX** | 以 FRR + 溢價/折價掛單，**匹配當下** 的 FRR 為準，此後固定不變 |

---

## 四、利息計算公式

### 4.1 出借人（Provider）實際所得

```
實際所得 = 本金 × 利率 × (秒數 / 86400) × 0.85
```

其中 **0.85** = 85% 為你拿到的比例（Bitfinex 收取 15% 手續費）。

### 4.2 隱藏訂單（Hidden Offer）手續費
Hidden Offer 的 Bitfinex 手續費為 **18%**，而非 15%。

### 4.3 最低借貸金額
Bitfinex 借貸的最低門檻為 **$150 USD 等值**。

### 4.4 借貸期限範圍
可借期限為 **2 天 ～ 120 天**。

---

## 五、關鍵 Matching Rules 摘要（頁面 P2-P120 對應）

### P2 提及：Rate + Period 雙重匹配
- 系統不只看利率，還要滿足期限相容性
- Bid 的期限必須被 Offer 的最長期限覆蓋

### P5 提及：FRR 分類不能混搭
- FRR 與固定利率之間有強制隔離牆

### P10 提及：利息 = 本金 × 日利率 × 實際天數
- 精確到秒級計算

### P15 提及：手續費层级
- 普通Offer：15%
- Hidden Offer：18%

---

## 六、實例說明

### 情境：出借人（ Lender）掛單
```
Offer: 0.05% / 天, 最長 30 天, $1,000 USD
```

### 情境：借款人（ Borrower）掛單
```
Bid: 0.06% / 天, 請求 15 天, $1,000 USD
```

### 匹配判斷
1. ✅ 利率：0.06% ≥ 0.05%（借款人願付 ≥ 出借人願收）
2. ✅ 期限：15天 ≤ 30天（出借人願借最長30天，覆盖15天）
3. ✅ FRR類型：需雙方同為固定或同為FRR（此例為固定，匹配成功）

**結果：成交！日利率 0.05%，15天結算。**

---

## 七、相關 API 端點

| 操作 | API 端點 |
|------|---------|
| 提交出借 Offer | `POST /v2/auth/submit/offer/funding` |
| 提交借款 Bid | `POST /v2/auth/submit/offer/funding` |
| 查詢 Funding 市場數據 | `GET /v2/auth/r/funding/offers/{symbol}` |
| 查詢 FRR | `GET /v2/auth/r/funding/credits` |

---

## 八、資料來源可信度

| 來源 | 類型 | 可信度 |
|------|------|--------|
| Bitfinex Help Center | 官方 | ⭐⭐⭐ 高 |
| Bitfinex Blog | 官方 | ⭐⭐⭐ 高 |
| Bitfinex API Docs | 官方 | ⭐⭐⭐ 高 |
| AltInvest Blog | 第三方 | ⭐⭐ 中（需交叉驗證） |

---

*最後更新：2026-04-14*
*研究目的：下游任務需整合進結構化 markdown 文件*
