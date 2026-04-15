# Bitfinex 借貸市場 — 借款方 vs 出借方 配對規則

> 所有資訊均來自 Bitfinex 官方 Help Center（support.bitfinex.com），不摻雜任何第三方或自行推論的內容。

---

## 一、配對成功的兩個必要條件

| 條件 | 說明 | 官方原文 |
|------|------|----------|
| **利率（Rate）必須相同** | 借款方（Bids）與出借方（Offers）雙方提出的利率必須完全一致 | *"For funding Bids and Offers to match, both the Rate and Period need to match."* |
| **期限（Period）必須相容** | 借款方指定的期限必須小於或等於出借方接受的期限 | *"if a Bid is looking for a period of 10 days, it must match with an Offer with a period of 10 days or greater."* |

> 來源：[What is Margin Funding - Bitfinex Support](https://support.bitfinex.com/hc/en-us/articles/214441185-What-is-Margin-Funding)

---

## 二、利率類型

| 利率類型 | 說明 |
|----------|------|
| **固定利率（Fixed Rate）** | 手動輸入特定利率值 |
| **FRR（Flash Return Rate）** | 以市場所有固定利率加權平均計算，每小時更新一次 |
| **FRR Delta Variable** | FRR ± 差值，匹配後利率仍隨 FRR 自動更新 |
| **FRR Delta Fixed** | FRR ± 差值，匹配前隨 FRR 變動，匹配後利率固定 |

> 官方關鍵限定：*"a fixed rate bid/offer cannot match with a Flash Return Rate (FRR) offer/bid."*
>
> 來源：[What is Margin Funding](https://support.bitfinex.com/hc/en-us/articles/214441185-What-is-Margin-Funding)

### 利率類型配對限制（官方已確認）

| 組合 | 能否配對 | 官方來源 |
|------|:-------:|---------|
| 固定利率 ↔ FRR | ❌ 不可 | *"a fixed rate bid/offer cannot match with a Flash Return Rate (FRR) offer/bid"* |

---

## 三、FRR vs FRR Delta 詳解

### FRR（Flash Return Rate）
- 以所有活躍固定利率訂單的加權平均計算
- 每小時更新一次
- 用途：讓資金提供方可使用浮動利率

### FRR Delta Variable
- 利率 = 當下 FRR + 你指定的差值（Delta）
- **匹配前**：利率隨 FRR 自動更新
- **匹配後**：利率仍隨 FRR 自動更新

### FRR Delta Fixed
- 利率 = 當下 FRR + 你指定的差值（Delta）
- **匹配前**：利率隨 FRR 變動
- **匹配後**：利率固定，不再隨 FRR 更新

### 官方 API 補充
- 官方 API 文件中，`FRRDELTAVAR` 與 `FRRDELTAFIX` 是可提交的 funding offer type
- 官方 API 文件另寫明：若要提交 **FRR offer**，可使用 `type = FRRDELTAVAR` 並將 `rate = 0`

> 來源：[What is the Bitfinex Funding Flash Return Rate](https://support.bitfinex.com/hc/en-us/articles/213919009-What-is-the-Bitfinex-Funding-Flash-Return-Rate)
> 來源：[What is the Bitfinex Funding FRR Delta](https://support.bitfinex.com/hc/en-us/articles/115003284729-What-is-the-Bitfinex-Funding-FRR-Delta)
> 來源：[New Offer - Bitfinex API Docs](https://docs.bitfinex.com/reference/ws-auth-input-offer-new)

---

## 四、期限（Period）規則

| 項目 | 規則 |
|------|------|
| **最短期限** | 2 天 |
| **最長期限** | 120 天 |
| **配對邏輯** | 借款方指定期限 ≤ 出借方接受期限 |

> 實例：借款方要求 10 天期 → 可以匹配出借方 10 天、15 天、30 天的訂單
>
> 來源：[What is Margin Funding](https://support.bitfinex.com/hc/en-us/articles/214441185-What-is-Margin-Funding)

---

## 五、金額規則

| 項目 | 規則 |
|------|------|
| **最低單筆出借金額** | $150（或等值其他貨幣） |
| **成交型態** | 官方 API 文件顯示 funding offer 可能為 `PARTIALLY FILLED`，代表可部分成交，未成交餘額可保留為剩餘數量或被取消 |

> 來源：[What is the minimum offer for Funding](https://support.bitfinex.com/hc/en-us/articles/213918949-What-is-the-minimum-offer-for-Funding)
> 來源：[Offer Status - Bitfinex API Docs](https://docs.bitfinex.com/v1/reference/rest-auth-offer-status)
> 來源：[Historical Offers - Bitfinex API Docs](https://docs.bitfinex.com/reference/ws-auth-historical-offers)

---

## 六、實例對照

### ✅ 可配對

| 借款方（Bid） | 出借方（Offer） | 結果 | 原因 |
|---------------|-----------------|------|------|
| 固定利率 0.05%，期限 10 天 | 固定利率 0.05%，期限 15 天 | ✅ 配對 | 利率相同、10天 ≤ 15天 |

### ❌ 不可配對 — 利率類型衝突

| 借款方（Bid） | 出借方（Offer） | 結果 | 原因 |
|---------------|-----------------|------|------|
| 固定利率 0.05% | FRR | ❌ 無法配對 | 固定利率 ≠ FRR（官方已有明確說明） |

### ❌ 不可配對 — 期限不足

| 借款方（Bid） | 出借方（Offer） | 結果 | 原因 |
|---------------|-----------------|------|------|
| 期限 30 天 | 期限 20 天 | ❌ 無法配對 | 30天 > 20天 |

---

## 七、⚠️ 未有官方明確說明的問題

以下問題**官方文件尚未明確回答**，需要直接聯繫 Bitfinex Support 確認：

1. **`FRRDELTAVAR` 與 `FRRDELTAFIX` 彼此之間，除了一般 Rate / Period 規則外，是否還有額外配對限制？**
   - 官方文件未明講

2. **固定利率是否也不能與所有 variable-rate funding offers 配對？**
   - 官方 Help Center 明確寫到「固定利率不能與 FRR 配對」
   - 官方 `No Var Rates` flag 寫到可排除 `variable rate funding offers`
   - 但 Help Center 沒有把 `FRRDELTAVAR / FRRDELTAFIX` 的配對矩陣完整列出

**建議**：若要最高確定性，請直接聯繫 [Bitfinex Support](https://cs.bitfinex.com/) 確認以上問題。
