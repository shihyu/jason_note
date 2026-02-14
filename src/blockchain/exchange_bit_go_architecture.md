# 加密貨幣交易所 × BitGo 託管架構完整說明

> 文件目的：說明交易所使用第三方託管服務（如 BitGo）時的完整運作模式、資金流設計、風控機制與工程實務架構。

---

## 一、整體系統架構

```text
User App
   │
   ▼
Exchange Backend
────────────────────────
• User Account Ledger
• Risk Engine
• Withdraw Queue
• Reconciliation Service
• Liquidity Monitor
────────────────────────
   │  (REST API)
   ▼
Custodian (BitGo)
────────────────────────
• Hot Wallet
• Warm Wallet
• Cold Custody
• Policy Engine (Approval / Multi‑sig / MPC)
────────────────────────
   │
   ▼
Blockchain Network
```

核心責任分工：

- 交易所：帳本、風控、流動性管理、提款審核
- 託管方：私鑰安全、鏈上簽名、交易廣播

---

## 二、入金流程（Deposit Flow）

### 1. 建立地址

- 交易所後端呼叫 API 建立地址
- 每位用戶一個地址，或「地址 + Memo」（依鏈種）

```text
Backend → Custodian API → createAddress()
```

---

### 2. 用戶轉帳

```text
User → Blockchain → Custodian Wallet
```

- 託管方監聽鏈上交易
- 等待確認數（confirmations）
- 透過 webhook 通知交易所

---

### 3. 帳本入帳

```text
Webhook → Backend → Credit User Ledger
```

重要原則：

- Webhook 不可作為唯一依據
- 必須定期做鏈上對帳（on-chain reconciliation）

---

## 三、提幣流程（Withdraw Flow）

```text
User
 │
 ▼
Exchange Backend
 │  ├─ KYC / AML 檢查
 │  ├─ 風控模型
 │  ├─ 餘額驗證
 │  ├─ 提款限額判斷
 │
 ▼
Withdraw Queue
 │
 ▼
Call Custodian send()
 │
 ▼
Policy Engine
 │  ├─ Auto Approval
 │  ├─ Manual Approval
 │  └─ Multi‑sig / MPC
 │
 ▼
Broadcast → Blockchain
```

交易所掌握：是否允許提款

託管方掌握：如何安全簽名與廣播

---

## 四、錢包分層設計（資金配置模型）

| 層級 | 建議比例 | 功能 |
|------|----------|------|
| Hot Wallet | 3–5% | 即時提款 |
| Warm Wallet | 10–15% | 補充熱錢包 |
| Cold Custody | 80%+ | 長期資產存管 |

設計目標：

- 熱錢包保持低暴露
- 冷錢包保持高安全
- 兼顧提款流動性

---

## 五、熱錢包補倉機制

```python
if hot_balance < threshold:
    trigger internal transfer from cold
```

實務考量：

- 多重簽章或人工審批
- 補倉延遲數十分鐘至數小時
- 需預測提款尖峰

關鍵能力：流動性預測模型

---

## 六、手續費與提款優化

### 1. Batch Withdraw（提款併單）

- 合併多筆提款
- 降低 Gas 成本
- 提高鏈上效率

---

### 2. 動態手續費模型

- 依 mempool 擁塞程度
- 依目標確認時間
- 避免過度支付

---

### 3. 提款限速與冷卻

```text
若變更密碼 / 2FA → 暫停提款 24 小時
```

- 防止帳號被盜後立即轉出

---

## 七、風控與合規設計

### 地址風險評分

- 黑名單地址阻擋
- 可疑行為模式偵測
- 高風險地址人工審查

---

### 提款限制機制

- 每日 / 每筆上限
- 不同等級差異化
- 異常提款頻率監控

---

## 八、私鑰控制模式

### 模式 A：全託管

- 私鑰由託管方持有
- 交易所透過 API 操作

優點：
- 合規容易
- 具保險覆蓋
- 降低內部風險

缺點：
- 成本較高
- 依賴第三方

---

### 模式 B：2-of-3 Multi‑sig

```text
Key A → Custodian
Key B → Exchange HSM
Key C → 備援機構
```

- 單方無法獨立動用資產
- 交易所仍保有部分控制權

---

## 九、Reconciliation（關鍵控制點）

每日或即時比對：

```text
Ledger Total
    == Custodian Wallet Balance
    == On-chain Balance
```

若忽略此步驟，將產生系統性風險。

---

## 十、主要風險與對策

| 風險 | 解法 |
|------|------|
| 私鑰被盜 | Multi‑sig / MPC |
| 內部人員盜領 | Policy Approval |
| 熱錢包被耗盡 | 提款限速 + 低比例配置 |
| Webhook 偽造 | HMAC 驗證 |
| 手續費暴漲 | 動態 Fee 模型 |

---

## 十一、大型交易所進階優化

- 分鏈獨立 wallet cluster
- 熱錢包分片（Sharding）
- 多區域 RPC 節點
- 自建 mempool 監控
- 行為風險 AI 模型
- 即時流動性壓力測試

---

## 十二、核心總結

> 交易所負責：帳本、風控、資金調度、合規流程  
> 託管方負責：私鑰安全、簽名機制、鏈上交易執行

真正的技術難點不在於呼叫 API，
而在於：

- 流動性預測
- 風險控管
- 系統對帳
- 災難復原設計

這些能力，才是交易所長期穩定運作的關鍵。
