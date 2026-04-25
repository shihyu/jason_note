# Bitfinex 放貸策略與匹配規則

> 資料來源：Bitfinex 官方文件、API Docs、支援中心
> 整理時間：2026-04-23

---

## 一、核心運作機制

Bitfinex 的保證金放貸（Margin Funding）是一個 **點對點（P2P）借貸市場**，連接：
- **放貸方（Lender）**：提供資金，賺取利息
- **借貸方（Borrower）**：借入資金進行槓桿交易

**關鍵元件：**
| 元件 | 說明 |
|------|------|
| Funding Wallet | 專用錢包，用於提供保證金借貸 |
| Funding Order Book | 掛單帳本，記錄所有待成交的借貸報價 |
| 自動撮合 | 當借貸双方的報價匹配時，資金自動提供並開始計息 |

---

## 二、利率類型（Rate Types）

### 2.1 Flash Return Rate（FRR）
Bitfinex 的專利自動利率機制，根據所有活躍借貸報價的加權平均即時計算「公平利率」，每小時更新一次以避免突發波動。

### 2.2 利率選項

| 利率類型 | 說明 |
|----------|------|
| **LIMIT** | 手動設定固定利率（如 0.01 = 1%） |
| **FRR** | 以撮合時市場利率為準，整個借款期間固定 |
| **FRRDELTAFIX** | FRR + 偏移量，撮合後利率靜態不變 |
| **FRRDELTAVAR** | FRR + 偏移量，撮合後利率隨 FRR **動態更新**（偏移量必須為正） |

### 2.3 利息計算公式

```
放貸方收益：amount × rate% × (seconds/86400) × 0.85   （扣除 15% 費用）
借貸方費用：amount × rate% × (seconds/86400)
```

**收益入帳時間**：約 UTC 01:30 每日

---

## 三、匹配規則（Matching Rules）

### 3.1 撮合條件

借方與貸方報價必須同時滿足以下條件才能撮合：

#### 1. 利率匹配（Rate Matching）
- 固定利率（LIMIT）**只能**與固定利率撮合
- FRR 系列報價**無法**與固定利率撮合
- 較低利率的報價**優先**被撮合（rate-priority）

#### 2. 期限匹配（Period Compatibility）
| 參數 | 數值 |
|------|------|
| 最短期限 | **2 天** |
| 最長期限 | **120 天** |
| 期限要求 | 放貸方的最大期限 **必須 ≥** 借方的請求期限 |

**範例**：借方請求 10 天，則放貸方必須設定 ≥10 天

### 3.2 FRR 行為特性
- FRR 報價會自動調整，但**不保證立即撮合**
- 僅當市場借貸利率 **≥ FRR 水準**時才會成交

---

## 四、放貸策略（Lending Strategies）

### 4.1 策略選擇矩陣

| 目標 | 推薦方式 |
|------|----------|
| 懶人設定 | FRR 或 FRRDELTAVAR，自動追蹤市場利率 |
| 可預期收入 | FRR + 固定利差，期限 7-30 天 |
| 更高報酬 | FRR + 浮動利差（如 +0.002% 至 +0.005%） |
| 快速撮合 | FRR 或低固定利率 |
| 保留流動性 | 短期限（2-15 天），拆分成小額報價 |

### 4.2 期限策略
- **較長期限**：通常利率較高，但流動性受限
- **較短期限**：流動性佳，但需更頻繁調整

### 4.3 自動化工具
Bitfinex 原生「Lending Pro」已於 **2024 年 8 月停用**，目前常用第三方自動借貸機器人：
- **Fuly.ai**
- **EarnUSD**

> ⚠️ 這些工具僅需 **「讀取」+「交易」** 權限的 API Key，**不需提現權限**。

### 4.4 建議最低金額
約 **$150 USD 等值**以上較具效益

---

## 五、報價參數（Funding Offer Parameters）

| 參數 | 說明 |
|------|------|
| **Amount** | 可提供的資金數量 |
| **Period** | 期限：2-120 天 |
| **Rate** | 利率（手動或 FRR 系列） |
| **RENEW flag** | 資金歸還時自動續借 |
| **NO_CLOSE flag** | 當倉位關閉時是否同步關閉借貸 |
| **HIDDEN** | 隱藏報價（費用 18%，而非 15%） |

---

## 六、風險與費用

### 6.1 費用結構

| 類型 | 費率 |
|------|------|
| 標準放貸收益 | **15%** 費用 |
| 隱藏報價 | **18%** 費用 |
| 最低計費 | 即使 1 小時內歸還，仍 **收取 1 小時費用** |
| 精度要求 | 收益金額需 **至少 8 位小數** |

### 6.2 風險保護機制
- 所有借貸皆有 **借款人倉位抵押**
- Bitfinex 僅在倉位需融資但借貸帳本已耗盡時，才作為**最後貸款方**
- 自動 **清算機制** 保護放貸方免受違約影響

### 6.3 主要風險
- 市場下跌時的 **利率波動**
- 極端行情下的 **流動性約束**
- 借款人被清算時影響借款可用性
- 資金在借款期滿或借款人還款前**無法動用**

---

## 七、官方資源

| 資源 | 連結 |
|------|------|
| Bitfinex 支援中心 - Margin Funding | https://support.bitfinex.com/hc/en-us/articles/115003428165-Margin-Funding-on-Bitfinex |
| Bitfinex API v2 文件 | https://docs.bitfinex.com/ |
| Bitfinex API Reference - Submit Funding Offer | https://docs.bitfinex.com/reference/rest-auth-submit-funding-offer |
| Bitfinex Blog - Margin Lending 教學 | https://blog.bitfinex.com/education/how-to-earn-with-margin-lending-on-bitfinex/ |
| What is Margin Funding（支援文章） | https://support.bitfinex.com/hc/en-us/articles/214441185-What-is-Margin-Funding |

---

*本文件由 AI 根據 Bitfinex 官方公開資訊整理，僅供參考，不構成投資建議。*
