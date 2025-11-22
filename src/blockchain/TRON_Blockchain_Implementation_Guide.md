# TRON 區塊鏈底層實現指南

> **純 Python 實現 - 深入理解 TRON 運作原理**  
> 本文檔詳細說明如何使用 HTTP API 和密碼學庫實現 TRON 區塊鏈的核心功能

---

## 📋 目錄

- [概述](#概述)
- [核心功能](#核心功能)
- [技術架構](#技術架構)
- [關鍵流程圖](#關鍵流程圖)
- [模組詳解](#模組詳解)
- [使用範例](#使用範例)
- [安全注意事項](#安全注意事項)

---

## 概述

### 什麼是這個專案？

這是一個教學導向的 TRON 區塊鏈底層實現，**不依賴** `tronpy` 等高階套件，直接使用：
- HTTP API 與節點通信
- 密碼學庫實現簽名和地址生成
- 純 Python 實現所有核心邏輯

### 為什麼要這樣做？

通過底層實現，您可以：
- 深入理解 TRON 的地址生成機制
- 掌握 ECDSA 簽名的完整流程
- 了解智能合約調用的編碼方式
- 學習區塊鏈交易的生命週期

---

## 核心功能

### 1️⃣ 地址管理
- ✅ Base58 ↔ Hex 格式轉換
- ✅ 從私鑰生成公鑰（secp256k1）
- ✅ 從公鑰生成地址（Keccak256）

### 2️⃣ 帳戶查詢
- ✅ 查詢 TRX 餘額
- ✅ 查詢 TRC20 代幣餘額（如 USDT）
- ✅ 查詢帳戶資源（能量、帶寬）

### 3️⃣ 交易處理
- ✅ 建立 TRX 轉賬交易
- ✅ 建立智能合約調用交易
- ✅ ECDSA 簽名（含 Recovery ID）
- ✅ 廣播交易到網路

### 4️⃣ 智能合約
- ✅ 調用只讀函數（如 `balanceOf`）
- ✅ 調用寫入函數（如 `transfer`）
- ✅ 參數編碼（ABI 兼容）

---

## 技術架構

```
┌────────────────────────────────────────────────────────────┐
│                        應用層                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ TronTransfer │  │  TronQuery   │  │     其他     │      │
│  │  (轉賬功能)  │  │  (查詢功能)  │  │   (擴展功能) │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
├────────────────────────────────────────────────────────────┤
│                        核心層                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │KeyGenerator  │  │TransactionSig│  │AddressConvert│      │
│  │(密鑰/地址)   │  │    (簽名)    │  │  (格式轉換)  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
├────────────────────────────────────────────────────────────┤
│                        API 層                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                    TronAPI                          │   │
│  │  (HTTP API 封裝 - 與 TRON 節點通信)                 │   │
│  └─────────────────────────────────────────────────────┘   │
├────────────────────────────────────────────────────────────┤
│                      基礎設施層                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   requests   │  │    ecdsa     │  │   Crypto     │      │
│  │  (HTTP 請求) │  │  (橢圓曲線)  │  │  (Keccak256) │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└────────────────────────────────────────────────────────────┘
```

---

## 關鍵流程圖

### 1. TRON 地址生成流程

```
┌─────────────────────────────────────────────────────────────┐
│                  私鑰 (Private Key)                         │
│                   64 hex 字符 (32 bytes)                    │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 1: ECDSA secp256k1 橢圓曲線運算                       │
│  ───────────────────────────────────────                    │
│  算法: P = d × G                                            │
│    - d: 私鑰（整數）                                        │
│    - G: secp256k1 基點                                      │
│    - P: 公鑰點 (x, y)                                       │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              非壓縮公鑰 (Uncompressed Public Key)           │
│              04 + x(32 bytes) + y(32 bytes)                 │
│                    130 hex 字符 (65 bytes)                  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 2: 去除 '04' 前綴                                     │
│  ───────────────────────                                    │
│  剩餘: x + y (64 bytes)                                     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 3: Keccak-256 哈希                                    │
│  ───────────────────────────                                │
│  H = Keccak256(x || y)                                      │
│  輸出: 32 bytes (64 hex 字符)                               │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 4: 取最後 20 bytes                                    │
│  ─────────────────────────                                  │
│  地址核心 = H[12:32]                                        │
│  40 hex 字符 (20 bytes)                                     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 5: 添加網路前綴 '41'                                  │
│  ────────────────────────────                               │
│  Hex 地址 = '41' + 地址核心                                 │
│  42 hex 字符 (21 bytes)                                     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 6-8: 計算 Base58Check 校驗和                          │
│  ─────────────────────────────────────                      │
│  1. SHA-256(Hex 地址) → hash1                               │
│  2. SHA-256(hash1) → hash2                                  │
│  3. 校驗和 = hash2[0:4]                                     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 9: 連接地址和校驗和                                   │
│  ─────────────────────────────                              │
│  完整數據 = Hex 地址 + 校驗和                               │
│  50 hex 字符 (25 bytes)                                     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 10: Base58 編碼                                       │
│  ───────────────────────                                    │
│  最終地址 = Base58(完整數據)                                │
│  格式: T + [A-Za-z0-9]+ (以 'T' 開頭)                       │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
              TQyZzVEs9qgLy52JAZQc7ZyxJf13ZNUG8u
                   (TRON Base58 地址)
```

### 2. TRX 轉賬完整流程

```
┌─────────────────────────────────────────────────────────────┐
│                       用戶發起轉賬                          │
│  輸入: 私鑰、接收地址、金額                                 │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  階段 1: 地址生成                                           │
│  ───────────────                                            │
│  from_address = KeyGenerator.private_key_to_address()       │
│                                                             │
│  ✓ 從私鑰派生發送者地址                                     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  階段 2: 建立交易 (Create Transaction)                      │
│  ─────────────────────────────────                          │
│  POST /wallet/createtransaction                             │
│  {                                                          │
│    "to_address": "TTqob...",                                │
│    "owner_address": "TQyZz...",                             │
│    "amount": 1000000  // 1 TRX = 10^6 SUN                   │
│  }                                                          │
│                                                             │
│  ← 返回: 未簽名交易 (包含 txID、raw_data)                   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  階段 3: 簽名交易 (Sign Transaction)                        │
│  ───────────────────────────────────                        │
│  3.1 提取 txID (32 bytes)                                   │
│       txID 是交易數據的 SHA-256 哈希                        │
│                                                             │
│  3.2 ECDSA 簽名                                             │
│       signature = ECDSA_sign(txID, private_key)             │
│       → 得到 (r, s) 各 32 bytes                             │
│                                                             │
│  3.3 計算 Recovery ID                                       │
│       嘗試 4 種可能值 (0,1,2,3)                             │
│       找出能正確恢復公鑰的那個                              │
│                                                             │
│  3.4 組合簽名                                               │
│       final_sig = r + s + recovery_id                       │
│       → 65 bytes                                            │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  階段 4: 廣播交易 (Broadcast Transaction)                   │
│  ────────────────────────────────────────                   │
│  POST /wallet/broadcasttransaction                          │
│  {                                                          │
│    "txID": "abc123...",                                     │
│    "raw_data": {...},                                       │
│    "signature": ["65_bytes_hex"]                            │
│  }                                                          │
│                                                             │
│  ← 返回: {"result": true, "txid": "..."}                    │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  階段 5: 交易進入記憶池 (Memory Pool)                       │
│  ────────────────────────────────────────                   │
│  1. 節點驗證交易格式                                        │
│  2. 驗證簽名有效性                                          │
│  3. 檢查帳戶餘額                                            │
│  4. 放入待打包記憶池                                        │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  階段 6: 超級代表打包區塊                                   │
│  ─────────────────────────────                              │
│  1. SR (Super Representative) 從記憶池選取交易              │
│  2. 打包成新區塊                                            │
│  3. 廣播到全網                                              │
│  4. 其他節點驗證並接受                                      │
│                                                             │
│  ⏱ TRON 區塊時間: 3 秒                                      │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  階段 7: 交易確認                                           │
│  ──────────────                                             │
│  區塊數: 1  → 交易上鏈（可見）                              │
│  區塊數: 19 → 固化（不可逆）                                │
│                                                             │
│  查詢: GET /wallet/gettransactioninfobyid                   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
                   ✅ 轉賬完成
```

### 3. USDT (TRC20) 轉賬流程

```
┌─────────────────────────────────────────────────────────────┐
│                   用戶發起 USDT 轉賬                        │
│  輸入: 私鑰、接收地址、USDT 金額、合約地址                  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  步驟 1: 編碼合約函數調用                                   │
│  ──────────────────────────                                 │
│  函數: transfer(address _to, uint256 _value)                │
│                                                             │
│  1.1 函數選擇器                                             │
│      selector = "transfer(address,uint256)"                 │
│                                                             │
│  1.2 編碼參數                                               │
│      ┌─────────────────────────────────────┐                │
│      │ 參數 1: address (32 bytes)          │                │
│      │  - 去除 '41' 前綴                   │                │
│      │  - 左補零到 32 bytes                │                │
│      │  例: 000...0a49b6890465f39...       │                │
│      ├─────────────────────────────────────┤                │
│      │ 參數 2: uint256 (32 bytes)          │                │
│      │  - 金額 × 10^6 (USDT 6 位小數)      │                │
│      │  - 轉為 hex 並左補零到 32 bytes    │                 │
│      │  例: 000...000000000000000f4240     │                │
│      │     (1000000 = 1 USDT)              │                │
│      └─────────────────────────────────────┘                │
│                                                             │
│  1.3 組合參數                                               │
│      parameter = 參數1 + 參數2 (64 bytes)                   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  步驟 2: 建立智能合約調用交易                               │
│  ──────────────────────────────────                         │
│  POST /wallet/triggersmartcontract                          │
│  {                                                          │
│    "owner_address": "TQyZz...",                             │
│    "contract_address": "TR7NH..." (USDT 合約),              │
│    "function_selector": "transfer(address,uint256)",        │
│    "parameter": "000...參數...",                            │
│    "fee_limit": 50000000,  // 50 TRX 上限                   │
│    "call_value": 0         // 不發送 TRX                    │
│  }                                                          │
│                                                             │
│  ← 返回: {                                                  │
│      "result": {"result": true},                            │
│      "transaction": {                                       │
│        "txID": "...",                                       │
│        "raw_data": {...}                                    │
│      }                                                      │
│    }                                                        │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  步驟 3: 簽名交易                                           │
│  ──────────────                                             │
│  (與 TRX 轉賬相同的簽名流程)                                │
│  1. 提取 txID                                               │
│  2. ECDSA 簽名 → (r, s)                                     │
│  3. 計算 Recovery ID                                        │
│  4. 組合為 65 bytes 簽名                                    │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  步驟 4: 廣播交易                                           │
│  ──────────────                                             │
│  POST /wallet/broadcasttransaction                          │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  步驟 5: 智能合約執行                                       │
│  ──────────────────────                                     │
│  5.1 TVM (TRON Virtual Machine) 載入合約                    │
│                                                             │
│  5.2 執行 transfer 函數                                     │
│      - 檢查發送者餘額                                       │
│      - 扣除發送者餘額                                       │
│      - 增加接收者餘額                                       │
│      - 觸發 Transfer 事件                                   │
│                                                             │
│  5.3 消耗資源                                               │
│      - 能量 (Energy): ~14000                                │
│      - 或燒毀 TRX 代替能量                                  │
│                                                             │
│  5.4 寫入狀態                                               │
│      更新鏈上代幣餘額                                       │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
                   ✅ USDT 轉賬完成
```

### 4. ECDSA 簽名與 Recovery ID 計算

```
┌─────────────────────────────────────────────────────────────┐
│                    輸入: txID (32 bytes)                    │
│                    私鑰: d (32 bytes)                       │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  步驟 1: 生成隨機數 k                                       │
│  ────────────────────────                                   │
│  k ∈ [1, n-1]  (n 是曲線階數)                               │
│  必須隨機且每次不同，否則私鑰可被推導                       │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  步驟 2: 計算 R = k × G                                     │
│  ─────────────────────────                                  │
│  R 是橢圓曲線上的點 (rx, ry)                                │
│  G 是 secp256k1 的基點                                      │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  步驟 3: 計算 r = rx mod n                                  │
│  ────────────────────────────                               │
│  r 是簽名的第一個分量 (32 bytes)                            │
│  如果 r = 0，重新生成 k                                     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  步驟 4: 計算 s                                             │
│  ──────────────                                             │
│  e = int(txID)  // 將 txID 視為整數                         │
│  s = k^(-1) × (e + r × d) mod n                             │
│                                                             │
│  其中:                                                      │
│    - k^(-1) 是 k 的模逆元                                   │
│    - d 是私鑰                                               │
│    - n 是曲線階數                                           │
│                                                             │
│  s 是簽名的第二個分量 (32 bytes)                            │
│  如果 s = 0，重新生成 k                                     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  步驟 5: 計算 Recovery ID (0-3)                             │
│  ──────────────────────────────                             │
│  Recovery ID 由兩個因素決定:                                │
│                                                             │
│  Bit 0 (最低位): 公鑰 y 坐標的奇偶性                        │
│  ┌──────────────────────────────────┐                       │
│  │ if y % 2 == 0: bit_0 = 0         │                       │
│  │ if y % 2 == 1: bit_0 = 1         │                       │
│  └──────────────────────────────────┘                       │
│                                                             │
│  Bit 1 (次低位): r 是否超過曲線階數                         │
│  ┌──────────────────────────────────┐                       │
│  │ if r < n: bit_1 = 0              │                       │
│  │ if r >= n: bit_1 = 1 (罕見)      │                       │
│  └──────────────────────────────────┘                       │
│                                                             │
│  recovery_id = bit_1 × 2 + bit_0                            │
│                                                             │
│  通常情況: recovery_id ∈ {0, 1}                             │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  步驟 6: 驗證簽名 (可選，用於檢查)                          │
│  ─────────────────────────────────                          │
│  對每個可能的 recovery_id:                                  │
│                                                             │
│  6.1 從 r 構造 x 坐標                                       │
│      x = r (或 r + n，如果 bit_1 = 1)                       │
│                                                             │
│  6.2 從 x 計算 y 坐標                                       │
│      曲線方程: y² = x³ + 7 (mod p)                          │
│      y = sqrt(y²) mod p                                     │
│      根據 bit_0 選擇 y 或 -y                                │
│                                                             │
│  6.3 構造點 R = (x, y)                                      │
│                                                             │
│  6.4 恢復公鑰                                               │
│      Q = r^(-1) × (s×R - e×G)                               │
│                                                             │
│  6.5 比對公鑰                                               │
│      如果 Q == 實際公鑰，找到正確的 recovery_id             │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  步驟 7: 組合最終簽名                                       │
│  ───────────────────────                                    │
│  signature = r || s || recovery_id                          │
│            = 32 + 32 + 1 = 65 bytes                         │
│                                                             │
│  Hex 格式: 130 個字符                                       │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
            ✅ 簽名完成，可用於廣播交易
```

---

## 模組詳解

### 常數定義模組

#### TronNetwork - 網路配置

```python
class TronNetwork:
    """TRON 網路配置常數"""
    
    # API 端點
    NILE_API = "https://nile.trongrid.io"      # Nile 測試網
    MAINNET_API = "https://api.trongrid.io"    # 主網
    
    # USDT 合約地址
    USDT_CONTRACT_MAINNET = "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"
    USDT_CONTRACT_NILE = "TXYZopYRdj2D9XRtbG411XZZ3kM5VkAeBf"
    
    # 地址前綴
    ADDRESS_PREFIX = "41"  # TRON 主網地址的 hex 前綴
```

**說明:**
- `NILE_API`: 測試網端點，用於開發和測試
- `MAINNET_API`: 主網端點，真實資產環境
- `USDT_CONTRACT_*`: TRC20 USDT 智能合約地址
- `ADDRESS_PREFIX`: 所有 TRON 主網地址的 hex 格式都以 "41" 開頭

#### CryptoConstants - 密碼學常數

```python
class CryptoConstants:
    """密碼學相關常數"""
    
    # secp256k1 橢圓曲線參數
    CURVE = SECP256k1
    CURVE_ORDER = SECP256k1.order           # n = 曲線的階
    FIELD_PRIME = SECP256k1.curve.p()       # p = 有限域的模數
    
    # 公鑰格式
    UNCOMPRESSED_PUBKEY_PREFIX = b"\x04"     # 非壓縮: 04 + x + y
    COMPRESSED_PUBKEY_EVEN_PREFIX = b"\x02"  # 壓縮: 02 + x (y偶數)
    COMPRESSED_PUBKEY_ODD_PREFIX = b"\x03"   # 壓縮: 03 + x (y奇數)
```

**技術背景:**

1. **secp256k1 曲線**
   - 比特幣、以太坊、TRON 都使用此曲線
   - 方程: y² = x³ + 7 (mod p)
   - 階數 n ≈ 2²⁵⁶，提供 128 位安全強度

2. **公鑰格式**
   - 非壓縮: 65 bytes (04 + x + y)，完整保留坐標
   - 壓縮: 33 bytes (02/03 + x)，節省空間，可從 x 推導 y

---

### 地址轉換模組

#### AddressConverter - 地址格式轉換

TRON 地址有兩種表示方式:

1. **Base58 格式** (用戶友好)
   - 以 'T' 開頭
   - 包含校驗和，可檢測輸入錯誤
   - 例: `TQyZzVEs9qgLy52JAZQc7ZyxJf13ZNUG8u`

2. **Hex 格式** (機器處理)
   - 以 '41' 開頭（主網標識）
   - 42 字符（21 bytes）
   - 例: `41a49b6890465f39fce73b18e5c9c5fd9136c70e38`

**轉換方法:**

```python
# Hex → Base58
base58_addr = AddressConverter.hex_to_base58("41a49b6890...")

# Base58 → Hex
hex_addr = AddressConverter.base58_to_hex("TQyZzVEs9qg...")
hex_addr_no_prefix = AddressConverter.base58_to_hex("TQyZzVEs9qg...", include_prefix=False)
```

---

### 密鑰與地址生成模組

#### KeyGenerator - 地址生成

**核心方法:**

1. **private_key_to_public_key()**
   - 輸入: 私鑰 (64 hex 字符)
   - 輸出: 公鑰 (130/66 hex 字符)
   - 算法: ECDSA secp256k1

2. **private_key_to_address()**
   - 輸入: 私鑰
   - 輸出: Base58 地址
   - 流程: 私鑰 → 公鑰 → Keccak256 → Base58Check

**安全考慮:**

```python
# ❌ 危險：硬編碼私鑰
private_key = "9930882e47d2b4d4d671435278edc06ba970184a436fba212f8c31a22f1fd7b2"

# ✅ 安全：使用環境變數
import os
private_key = os.environ.get('TRON_PRIVATE_KEY')
if not private_key:
    raise ValueError("請設置 TRON_PRIVATE_KEY 環境變數")
```

---

### HTTP API 封裝模組

#### TronAPI - 節點通信

**主要端點:**

| 端點 | 方法 | 用途 |
|------|------|------|
| `/wallet/getaccount` | POST | 查詢帳戶資訊 |
| `/wallet/createtransaction` | POST | 建立 TRX 轉賬 |
| `/wallet/triggersmartcontract` | POST | 調用智能合約（寫入）|
| `/wallet/triggerconstantcontract` | POST | 查詢智能合約（只讀）|
| `/wallet/broadcasttransaction` | POST | 廣播已簽名交易 |
| `/wallet/gettransactioninfobyid` | POST | 查詢交易資訊 |

**使用範例:**

```python
# 初始化 API
api = TronAPI(TronNetwork.NILE_API, api_key="your-api-key")

# 查詢餘額
balance = api.get_account_balance("TQyZzVEs9qgLy52JAZQc7ZyxJf13ZNUG8u")
print(f"餘額: {balance} TRX")

# 查詢 USDT 餘額
result = api.trigger_constant_contract(
    contract_address=TronNetwork.USDT_CONTRACT_NILE,
    function_selector="balanceOf(address)",
    parameter="000000000000000000000000a49b6890465f39fce73b18e5c9c5fd9136c70e38",
    owner_address="TQyZzVEs9qgLy52JAZQc7ZyxJf13ZNUG8u"
)
```

---

### 交易簽名模組

#### TransactionSigner - ECDSA 簽名

**簽名結構:**

```
┌────────────────────┬────────────────────┬──────────────┐
│        r           │         s          │ recovery_id  │
│    (32 bytes)      │    (32 bytes)      │   (1 byte)   │
└────────────────────┴────────────────────┴──────────────┘
         ECDSA 簽名分量                      恢復標識
```

**Recovery ID 的作用:**

Recovery ID 允許從簽名恢復公鑰，這樣交易中不需要包含完整公鑰，節省空間。

**數學原理:**

給定簽名 (r, s) 和消息 e，可以恢復公鑰 Q:

```
Q = r^(-1) × (s×R - e×G)
```

其中:
- R 是從 r 構造的橢圓曲線點
- G 是基點
- recovery_id 幫助確定正確的 R 和 y 坐標

---

### 高階功能模組

#### TronTransfer - 轉賬封裝

**TRX 轉賬:**

```python
txid = TronTransfer.transfer_trx(
    api=api,
    private_key_hex="your_private_key",
    to_address="TTqobYiHixykLYyA3WxmCLVCMCySHfigyE",
    amount_trx=1.0,
    verbose=True
)
```

**USDT 轉賬:**

```python
txid = TronTransfer.transfer_usdt(
    api=api,
    private_key_hex="your_private_key",
    to_address="TTqobYiHixykLYyA3WxmCLVCMCySHfigyE",
    amount_usdt=10.0,
    contract_address=TronNetwork.USDT_CONTRACT_NILE,
    verbose=True
)
```

**參數編碼 (TRC20):**

TRC20 代幣轉賬需要編碼 `transfer(address,uint256)` 函數:

```
參數格式 (總共 64 bytes):
┌────────────────────────────────────────┐
│  地址 (address) - 32 bytes             │
│  000000000000000000000000a49b6890...   │
│  └─ 左補零到 32 bytes                  │
├────────────────────────────────────────┤
│  金額 (uint256) - 32 bytes             │
│  00000000000000000000000000000f4240    │
│  └─ 1000000 (1 USDT)，左補零           │
└────────────────────────────────────────┘
```

#### TronQuery - 查詢封裝

**查詢 USDT 餘額:**

```python
balance = TronQuery.check_usdt_balance(
    api=api,
    address="TQyZzVEs9qgLy52JAZQc7ZyxJf13ZNUG8u",
    contract_address=TronNetwork.USDT_CONTRACT_NILE
)
print(f"USDT 餘額: {balance:.6f} USDT")
```

---

## 使用範例

### 完整工作流程

```python
import os
from tron_impl import *

# 1. 初始化 API（使用測試網）
api = TronAPI(TronNetwork.NILE_API)

# 2. 從環境變數讀取私鑰（安全做法）
private_key = os.environ.get('TRON_PRIVATE_KEY')
if not private_key:
    raise ValueError("請設置 TRON_PRIVATE_KEY 環境變數")

# 3. 生成地址
my_address = KeyGenerator.private_key_to_address(private_key)
print(f"我的地址: {my_address}")

# 4. 查詢餘額
trx_balance = api.get_account_balance(my_address)
usdt_balance = TronQuery.check_usdt_balance(
    api, my_address, TronNetwork.USDT_CONTRACT_NILE
)
print(f"TRX 餘額: {trx_balance:.6f} TRX")
print(f"USDT 餘額: {usdt_balance:.6f} USDT")

# 5. TRX 轉賬
txid = TronTransfer.transfer_trx(
    api=api,
    private_key_hex=private_key,
    to_address="TTqobYiHixykLYyA3WxmCLVCMCySHfigyE",
    amount_trx=1.0
)
print(f"TRX 轉賬交易: https://nile.tronscan.org/#/transaction/{txid}")

# 6. USDT 轉賬
txid = TronTransfer.transfer_usdt(
    api=api,
    private_key_hex=private_key,
    to_address="TTqobYiHixykLYyA3WxmCLVCMCySHfigyE",
    amount_usdt=10.0,
    contract_address=TronNetwork.USDT_CONTRACT_NILE
)
print(f"USDT 轉賬交易: https://nile.tronscan.org/#/transaction/{txid}")
```

### 地址生成詳細示範

```python
# 示範地址生成的每一步
private_key = "9930882e47d2b4d4d671435278edc06ba970184a436fba212f8c31a22f1fd7b2"

# 使用 show_steps=True 顯示詳細過程
address = KeyGenerator.private_key_to_address(private_key, show_steps=True)

# 輸出將包含:
# - 每一步的計算結果
# - 中間數據的長度驗證
# - 格式檢查
# - 完整的推導過程
```

---

## 安全注意事項

### 🔴 關鍵安全規則

1. **絕不在代碼中硬編碼私鑰**
   ```python
   # ❌ 危險
   private_key = "9930882e47d2b4d4d671435278edc06ba970184a436fba212f8c31a22f1fd7b2"
   
   # ✅ 安全
   private_key = os.environ.get('TRON_PRIVATE_KEY')
   ```

2. **絕不將私鑰提交到版本控制**
   - 使用 `.gitignore` 排除包含私鑰的文件
   - 使用環境變數或密鑰管理服務

3. **區分測試網和主網**
   ```python
   # 測試網 - 可以自由實驗
   api = TronAPI(TronNetwork.NILE_API)
   
   # 主網 - 謹慎操作，涉及真實資產
   api = TronAPI(TronNetwork.MAINNET_API)
   ```

4. **驗證交易參數**
   - 確認接收地址正確
   - 確認轉賬金額正確
   - 在主網操作前先在測試網驗證

5. **私鑰儲存建議**
   - 使用硬體錢包（Ledger, Trezor）
   - 使用加密的密鑰管理服務
   - 使用環境變數（開發環境）
   - 永遠不要截圖或複製到不安全的地方

### 🛡️ 代碼安全檢查清單

- [ ] 移除所有硬編碼的私鑰
- [ ] 配置 `.gitignore` 排除敏感文件
- [ ] 使用環境變數管理私鑰
- [ ] 在測試網充分測試
- [ ] 設置適當的 `fee_limit` 避免過高手續費
- [ ] 驗證接收地址的有效性
- [ ] 實現交易確認檢查機制

---

## 技術深入探討

### secp256k1 橢圓曲線

**曲線方程:**
```
y² ≡ x³ + 7 (mod p)
```

**參數:**
- **p** (有限域模數): 2²⁵⁶ - 2³² - 977
- **n** (曲線階數): 非常接近 2²⁵⁶ 的質數
- **G** (基點): 標準化的起始點

**為什麼選擇 secp256k1?**
1. 高效率的計算
2. 128 位安全強度
3. 行業標準（比特幣、以太坊）
4. 良好的數學特性

### Keccak-256 vs SHA-256

| 特性 | Keccak-256 | SHA-256 |
|------|------------|---------|
| 用於 | 地址生成 | 交易哈希、校驗和 |
| 輸出 | 256 bits | 256 bits |
| 標準 | SHA-3 候選（原始版本）| FIPS 180-4 |
| TRON 使用 | ✅ 地址派生 | ✅ 簽名、校驗 |

### Base58 vs Base58Check

**Base58:**
- 移除易混淆字符: 0, O, I, l
- 僅用於編碼，無錯誤檢測

**Base58Check:**
- Base58 + 4 bytes 校驗和
- 可檢測輸入錯誤
- TRON 地址使用 Base58Check

**校驗和計算:**
```
checksum = SHA256(SHA256(data))[0:4]
```

---

## 常見問題 (FAQ)

### Q1: TRX 和 SUN 的關係？

**A:** 1 TRX = 1,000,000 SUN

SUN 是 TRON 的最小單位，類似於比特幣的 Satoshi。
所有鏈上金額都以 SUN 為單位。

### Q2: 為什麼需要 Recovery ID？

**A:** Recovery ID 允許從簽名恢復公鑰，這樣:
- 交易中不需要包含完整公鑰（節省空間）
- 節點可以驗證簽名者身份
- 減少交易大小（降低手續費）

### Q3: TRC20 代幣轉賬為什麼需要能量？

**A:** TRC20 代幣轉賬需要調用智能合約，消耗計算資源:
- **能量 (Energy)**: 約 14,000 - 65,000
- **獲取方式**: 
  1. 質押 TRX 獲得能量
  2. 燒毀 TRX 代替能量（約 420 SUN = 1 能量）

### Q4: 什麼是固化 (Solidified)？

**A:** TRON 的確認機制:
- **1 個區塊**: 交易上鏈（可見）
- **19 個區塊**: 交易固化（不可逆）
- **時間**: 約 1 分鐘（19 × 3 秒）

### Q5: 測試網和主網的差異？

| 特性 | 測試網 (Nile) | 主網 |
|------|---------------|------|
| 代幣價值 | 無價值 | 真實資產 |
| 獲取測試幣 | 水龍頭免費領取 | 需要購買 |
| API 端點 | nile.trongrid.io | api.trongrid.io |
| 適用場景 | 開發、測試 | 生產環境 |

---

## 擴展資源

### 官方文檔
- [TRON 開發者文檔](https://developers.tron.network/)
- [TronGrid API 文檔](https://developers.tron.network/docs/tron-grid-intro)
- [TRC20 代幣標準](https://github.com/tronprotocol/TIPs/blob/master/tip-20.md)

### 工具和服務
- [Nile 測試網水龍頭](https://nileex.io/join/getJoinPage)
- [TronScan 區塊鏈瀏覽器](https://tronscan.org/)
- [TronLink 錢包](https://www.tronlink.org/)

### 相關標準
- [EIP-55: 混合大小寫校驗和地址編碼](https://eips.ethereum.org/EIPS/eip-55)
- [BIP-32: 分層確定性錢包](https://github.com/bitcoin/bips/blob/master/bip-0032.mediawiki)
- [BIP-39: 助記詞](https://github.com/bitcoin/bips/blob/master/bip-0039.mediawiki)

---

## 版本歷史

### v2.0 (2025-01-22)
- ✅ 重構代碼結構，模組化設計
- ✅ 添加詳細的中文註釋
- ✅ 實現 TRX 和 USDT 轉賬
- ✅ 完善錯誤處理
- ✅ 添加使用示範

### v1.0 (2024-XX-XX)
- ✅ 初始版本
- ✅ 基本地址生成功能
- ✅ 簡單的 API 封裝

---

## 授權與免責聲明

### 使用許可
本專案採用 MIT 授權，可自由使用、修改和分發。

### 免責聲明
- 本專案僅供**教學和學習**用途
- 在生產環境使用前請**充分測試**
- 作者不對使用本代碼造成的任何損失負責
- 請遵守當地法律法規

### 安全提醒
- 🔴 **永遠不要在公開場合分享私鑰**
- 🔴 **在主網操作前務必在測試網驗證**
- 🔴 **定期備份重要數據**
- 🔴 **使用硬體錢包保護大額資產**

---

## 貢獻指南

歡迎提交問題和改進建議！

### 如何貢獻
1. Fork 本專案
2. 創建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 開啟 Pull Request

### 代碼風格
- 遵循 PEP 8 規範
- 使用有意義的變數名稱
- 添加清晰的註釋（中文）
- 包含單元測試


## 完整程式碼

### 依賴安裝

```bash
pip install requests base58 ecdsa pycryptodome --break-system-packages
```

### 完整實現代碼

```python
"""
TRON 區塊鏈底層實現 - 純 Python 版本
=====================================

本程式直接使用 HTTP API 和密碼學庫實現 TRON 區塊鏈的核心功能，
不依賴 tronpy 等高階套件，幫助深入理解 TRON 的底層運作原理。

主要功能：
1. 地址格式轉換 (Base58 ↔ Hex)
2. 從私鑰生成公鑰和地址
3. 查詢帳戶餘額 (TRX 和 TRC20 代幣)
4. 建立、簽名、廣播交易
5. TRX 和 USDT (TRC20) 轉賬

作者：AI Assistant
版本：2.0 (重構版)
最後更新：2025-01-22
"""

import hashlib
from typing import Dict, Any, Optional
import os

import base58
import requests
from Crypto.Hash import keccak
from ecdsa import SECP256k1, SigningKey
from ecdsa.util import sigencode_string
from ecdsa.numbertheory import square_root_mod_prime
from ecdsa.ellipticcurve import Point


# ============================================
# 常數定義
# ============================================


class TronNetwork:
    """TRON 網路配置常數"""

    # API 端點
    NILE_API = "https://nile.trongrid.io"  # Nile 測試網
    MAINNET_API = "https://api.trongrid.io"  # 主網

    # USDT 合約地址
    USDT_CONTRACT_MAINNET = "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"  # 主網 USDT
    USDT_CONTRACT_NILE = "TXYZopYRdj2D9XRtbG411XZZ3kM5VkAeBf"  # 測試網 USDT

    # 地址前綴
    ADDRESS_PREFIX = "41"  # TRON 主網地址的 hex 前綴


class CryptoConstants:
    """密碼學相關常數"""

    # secp256k1 橢圓曲線參數
    CURVE = SECP256k1
    CURVE_ORDER = SECP256k1.order  # 曲線的階
    FIELD_PRIME = SECP256k1.curve.p()  # 有限域的模數

    # 公鑰格式
    UNCOMPRESSED_PUBKEY_PREFIX = b"\x04"  # 非壓縮公鑰前綴
    COMPRESSED_PUBKEY_EVEN_PREFIX = b"\x02"  # 壓縮公鑰前綴 (y 為偶數)
    COMPRESSED_PUBKEY_ODD_PREFIX = b"\x03"  # 壓縮公鑰前綴 (y 為奇數)

    # 長度常數
    PRIVATE_KEY_LENGTH = 64  # 私鑰長度 (hex 字符)
    PUBLIC_KEY_UNCOMPRESSED_LENGTH = 130  # 非壓縮公鑰長度 (hex 字符)
    PUBLIC_KEY_COMPRESSED_LENGTH = 66  # 壓縮公鑰長度 (hex 字符)
    ADDRESS_HEX_LENGTH = 42  # 帶前綴的 hex 地址長度
    ADDRESS_CORE_LENGTH = 40  # 不帶前綴的 hex 地址長度
    SIGNATURE_LENGTH = 65  # ECDSA 可恢復簽名長度 (bytes)


# ============================================
# 地址轉換工具
# ============================================


class AddressConverter:
    """
    TRON 地址格式轉換工具

    支援 Base58 和 Hex 格式之間的相互轉換。
    """

    @staticmethod
    def hex_to_base58(hex_address: str) -> str:
        """將 Hex 格式地址轉換為 Base58 格式"""
        # 移除 0x 前綴（如果存在）
        if hex_address.startswith(("0x", "0X")):
            hex_address = hex_address[2:]

        # 統一轉為小寫
        hex_address = hex_address.lower()

        # 檢查並處理 41 前綴
        if hex_address.startswith("41"):
            if len(hex_address) != CryptoConstants.ADDRESS_HEX_LENGTH:
                raise ValueError(
                    f"帶 41 前綴的地址長度應為 {CryptoConstants.ADDRESS_HEX_LENGTH} 字符"
                )
        else:
            if len(hex_address) != CryptoConstants.ADDRESS_CORE_LENGTH:
                raise ValueError(
                    f"不帶 41 前綴的地址長度應為 {CryptoConstants.ADDRESS_CORE_LENGTH} 字符"
                )
            hex_address = TronNetwork.ADDRESS_PREFIX + hex_address

        # 驗證是否為有效的 hex 字符串
        try:
            address_bytes = bytes.fromhex(hex_address)
        except ValueError as e:
            raise ValueError(f"無效的 hex 字符串: {hex_address}") from e

        # Base58Check 編碼
        base58_address = base58.b58encode_check(address_bytes).decode()

        # 驗證結果
        if not base58_address.startswith("T"):
            raise ValueError(f"轉換結果不是有效的 TRON 主網地址: {base58_address}")

        return base58_address

    @staticmethod
    def base58_to_hex(base58_address: str, include_prefix: bool = True) -> str:
        """將 Base58 格式地址轉換為 Hex 格式"""
        try:
            decoded = base58.b58decode_check(base58_address)
            hex_address = decoded.hex()

            if not hex_address.startswith("41"):
                raise ValueError(f"不是有效的 TRON 主網地址: {hex_address}")

            if include_prefix:
                return hex_address
            else:
                return hex_address[2:]

        except Exception as e:
            raise ValueError(f"Base58 解碼失敗: {e}") from e


# ============================================
# 密鑰與地址生成
# ============================================


class KeyGenerator:
    """TRON 密鑰和地址生成工具"""

    @staticmethod
    def private_key_to_public_key(
        private_key_hex: str, compressed: bool = False
    ) -> str:
        """從私鑰生成公鑰"""
        if len(private_key_hex) != CryptoConstants.PRIVATE_KEY_LENGTH:
            raise ValueError(f"私鑰長度應為 {CryptoConstants.PRIVATE_KEY_LENGTH} 字符")

        try:
            private_key_bytes = bytes.fromhex(private_key_hex)
        except ValueError as e:
            raise ValueError("無效的 hex 字符串") from e

        signing_key = SigningKey.from_string(
            private_key_bytes, curve=CryptoConstants.CURVE
        )
        verifying_key = signing_key.get_verifying_key()

        public_key_bytes = verifying_key.to_string()
        x_bytes = public_key_bytes[:32]
        y_bytes = public_key_bytes[32:]

        if compressed:
            y_int = int.from_bytes(y_bytes, byteorder="big")
            prefix = (
                CryptoConstants.COMPRESSED_PUBKEY_EVEN_PREFIX
                if y_int % 2 == 0
                else CryptoConstants.COMPRESSED_PUBKEY_ODD_PREFIX
            )
            public_key = prefix + x_bytes
        else:
            public_key = CryptoConstants.UNCOMPRESSED_PUBKEY_PREFIX + public_key_bytes

        return public_key.hex()

    @staticmethod
    def private_key_to_address(private_key_hex: str, show_steps: bool = False) -> str:
        """從私鑰生成 TRON 地址"""
        if show_steps:
            print("=" * 70)
            print("TRON 地址生成流程")
            print("=" * 70)
            print(f"\n私鑰: {private_key_hex}\n")

        # Step 1: 生成非壓縮公鑰
        public_key_hex = KeyGenerator.private_key_to_public_key(
            private_key_hex, compressed=False
        )
        if show_steps:
            print(f"【Step 1】公鑰: {public_key_hex}\n")

        # Step 2: 去掉 "04" 前綴
        public_key_no_prefix = public_key_hex[2:]
        if show_steps:
            print(f"【Step 2】去前綴: {public_key_no_prefix}\n")

        # Step 3: Keccak256 哈希
        keccak_hash = keccak.new(digest_bits=256)
        keccak_hash.update(bytes.fromhex(public_key_no_prefix))
        keccak_digest = keccak_hash.hexdigest()
        if show_steps:
            print(f"【Step 3】Keccak256: {keccak_digest}\n")

        # Step 4: 取最後 20 bytes
        address_core = keccak_digest[-40:]
        if show_steps:
            print(f"【Step 4】地址核心: {address_core}\n")

        # Step 5: 添加 "41" 前綴
        address_with_prefix = TronNetwork.ADDRESS_PREFIX + address_core
        if show_steps:
            print(f"【Step 5】Hex 地址: {address_with_prefix}\n")

        # Step 6-8: 計算校驗和
        sha256_first = hashlib.sha256(bytes.fromhex(address_with_prefix)).hexdigest()
        sha256_second = hashlib.sha256(bytes.fromhex(sha256_first)).hexdigest()
        checksum = sha256_second[:8]
        if show_steps:
            print(f"【Step 6-8】校驗和: {checksum}\n")

        # Step 9: 連接地址和校驗和
        address_with_checksum = address_with_prefix + checksum
        if show_steps:
            print(f"【Step 9】完整數據: {address_with_checksum}\n")

        # Step 10: Base58 編碼
        address_base58 = base58.b58encode(bytes.fromhex(address_with_checksum)).decode()
        if show_steps:
            print(f"【Step 10】Base58 地址: {address_base58}\n")
            print("=" * 70)

        return address_base58


# ============================================
# HTTP API 封裝
# ============================================


class TronAPI:
    """TRON HTTP API 封裝類別"""

    def __init__(self, api_url: str, api_key: Optional[str] = None):
        """初始化 TRON API 客戶端"""
        self.api_url = api_url
        self.headers = {"Content-Type": "application/json"}

        if api_key:
            self.headers["TRON-PRO-API-KEY"] = api_key

    def post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """發送 POST 請求到 TRON 節點"""
        url = f"{self.api_url}{endpoint}"
        response = requests.post(url, json=data, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def get(self, endpoint: str) -> Dict[str, Any]:
        """發送 GET 請求到 TRON 節點"""
        url = f"{self.api_url}{endpoint}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def get_account(self, address: str) -> Dict[str, Any]:
        """查詢帳戶資訊"""
        data = {"address": address, "visible": True}
        return self.post("/wallet/getaccount", data)

    def get_account_balance(self, address: str) -> float:
        """查詢 TRX 餘額"""
        account = self.get_account(address)
        balance_sun = account.get("balance", 0)
        return balance_sun / 1_000_000

    def trigger_constant_contract(
        self,
        contract_address: str,
        function_selector: str,
        parameter: str,
        owner_address: str,
    ) -> Dict[str, Any]:
        """調用智能合約（只讀）"""
        data = {
            "owner_address": owner_address,
            "contract_address": contract_address,
            "function_selector": function_selector,
            "parameter": parameter,
            "visible": True,
        }
        return self.post("/wallet/triggerconstantcontract", data)

    def create_transaction(
        self, to_address: str, owner_address: str, amount: float
    ) -> Dict[str, Any]:
        """建立 TRX 轉賬交易"""
        data = {
            "to_address": to_address,
            "owner_address": owner_address,
            "amount": int(amount * 1_000_000),
            "visible": True,
        }
        return self.post("/wallet/createtransaction", data)

    def trigger_smart_contract(
        self,
        contract_address: str,
        function_selector: str,
        parameter: str,
        fee_limit: int,
        owner_address: str,
    ) -> Dict[str, Any]:
        """調用智能合約（寫入）"""
        data = {
            "owner_address": owner_address,
            "contract_address": contract_address,
            "function_selector": function_selector,
            "parameter": parameter,
            "fee_limit": fee_limit,
            "call_value": 0,
            "visible": True,
        }
        return self.post("/wallet/triggersmartcontract", data)

    def broadcast_transaction(
        self, signed_transaction: Dict[str, Any]
    ) -> Dict[str, Any]:
        """廣播已簽名的交易到網路"""
        return self.post("/wallet/broadcasttransaction", signed_transaction)

    def get_transaction_info(self, txid: str) -> Dict[str, Any]:
        """查詢交易資訊"""
        data = {"value": txid}
        return self.post("/wallet/gettransactioninfobyid", data)


# ============================================
# 交易簽名
# ============================================


class TransactionSigner:
    """TRON 交易簽名工具"""

    @staticmethod
    def sign_transaction(
        transaction: Dict[str, Any], private_key_hex: str
    ) -> Dict[str, Any]:
        """對交易進行簽名"""
        txid = transaction.get("txID")
        if not txid:
            raise ValueError("交易資料中沒有 txID")

        txid_bytes = bytes.fromhex(txid)

        private_key_bytes = bytes.fromhex(private_key_hex)
        signing_key = SigningKey.from_string(
            private_key_bytes, curve=CryptoConstants.CURVE
        )

        signature = signing_key.sign_digest(txid_bytes, sigencode=sigencode_string)

        recovery_id = TransactionSigner._calculate_recovery_id(
            txid_bytes, signature, signing_key
        )

        signature_with_recovery = signature + bytes([recovery_id])

        transaction["signature"] = [signature_with_recovery.hex()]

        return transaction

    @staticmethod
    def _calculate_recovery_id(
        message_hash: bytes, signature: bytes, signing_key: SigningKey
    ) -> int:
        """計算 ECDSA 簽名的 Recovery ID"""
        r = int.from_bytes(signature[:32], byteorder="big")
        s = int.from_bytes(signature[32:64], byteorder="big")

        verifying_key = signing_key.get_verifying_key()
        correct_point = verifying_key.pubkey.point

        p = CryptoConstants.FIELD_PRIME
        n = CryptoConstants.CURVE_ORDER

        for recovery_id in range(4):
            try:
                x = r
                if recovery_id >= 2:
                    x = r + n
                    if x >= p:
                        continue

                y_squared = (pow(x, 3, p) + 7) % p
                y = square_root_mod_prime(y_squared, p)

                if (y % 2 == 0) != (recovery_id % 2 == 0):
                    y = p - y

                R = Point(CryptoConstants.CURVE.curve, x, y, n)

                e = int.from_bytes(message_hash, byteorder="big")
                r_inv = pow(r, -1, n)

                recovered_point = r_inv * (
                    s * R + (-e % n) * CryptoConstants.CURVE.generator
                )

                if (
                    recovered_point.x() == correct_point.x()
                    and recovered_point.y() == correct_point.y()
                ):
                    return recovery_id

            except Exception:
                continue

        y = correct_point.y()
        return 1 if y % 2 == 1 else 0


# ============================================
# 高階功能封裝
# ============================================


class TronTransfer:
    """TRON 轉賬功能封裝"""

    @staticmethod
    def transfer_trx(
        api: TronAPI,
        private_key_hex: str,
        to_address: str,
        amount_trx: float,
        verbose: bool = True,
    ) -> Optional[str]:
        """轉賬 TRX"""
        if verbose:
            print("\n" + "=" * 60)
            print("開始 TRX 轉賬")
            print("=" * 60)

        from_address = KeyGenerator.private_key_to_address(private_key_hex)

        if verbose:
            print(f"\n發送方: {from_address}")
            print(f"接收方: {to_address}")
            print(f"金額: {amount_trx} TRX")

        if verbose:
            print("\n[1/3] 建立交易...")

        transaction = api.create_transaction(to_address, from_address, amount_trx)

        if "Error" in transaction:
            if verbose:
                print(f"❌ 建立交易失敗: {transaction}")
            return None

        if verbose:
            print(f"✓ 交易已建立")
            print(f"  交易ID: {transaction['txID']}")

        if verbose:
            print("\n[2/3] 簽名交易...")

        signed_txn = TransactionSigner.sign_transaction(transaction, private_key_hex)

        if verbose:
            print("✓ 交易已簽名")

        if verbose:
            print("\n[3/3] 廣播交易...")

        result = api.broadcast_transaction(signed_txn)

        if result.get("result"):
            if verbose:
                print("✓ 交易已廣播成功")
                print(f"\n交易ID: {transaction['txID']}")
                print("=" * 60)
            return transaction["txID"]
        else:
            if verbose:
                print(f"❌ 廣播失敗: {result}")
            return None

    @staticmethod
    def transfer_usdt(
        api: TronAPI,
        private_key_hex: str,
        to_address: str,
        amount_usdt: float,
        contract_address: str,
        verbose: bool = True,
    ) -> Optional[str]:
        """轉賬 USDT (TRC20 代幣)"""
        if verbose:
            print("\n" + "=" * 60)
            print("開始 USDT (TRC20) 轉賬")
            print("=" * 60)

        from_address = KeyGenerator.private_key_to_address(private_key_hex)

        if verbose:
            print(f"\n發送方: {from_address}")
            print(f"接收方: {to_address}")
            print(f"金額: {amount_usdt} USDT")

        if verbose:
            print("\n[1/4] 編碼合約參數...")

        to_hex = AddressConverter.base58_to_hex(to_address, include_prefix=False)
        to_param = to_hex.zfill(64)

        amount_raw = int(amount_usdt * 1_000_000)
        amount_param = hex(amount_raw)[2:].zfill(64)

        parameter = to_param + amount_param

        if verbose:
            print(f"✓ 參數編碼完成")

        if verbose:
            print("\n[2/4] 建立交易...")

        transaction = api.trigger_smart_contract(
            contract_address=contract_address,
            function_selector="transfer(address,uint256)",
            parameter=parameter,
            fee_limit=50_000_000,
            owner_address=from_address,
        )

        if "Error" in transaction or "result" not in transaction:
            if verbose:
                print(f"❌ 建立交易失敗: {transaction}")
            return None

        if "transaction" not in transaction:
            if verbose:
                print(f"❌ 交易結構異常: {transaction}")
            return None

        actual_txn = transaction["transaction"]

        if verbose:
            print(f"✓ 交易已建立")
            print(f"  交易ID: {actual_txn['txID']}")

        if verbose:
            print("\n[3/4] 簽名交易...")

        signed_txn = TransactionSigner.sign_transaction(actual_txn, private_key_hex)

        if verbose:
            print("✓ 交易已簽名")

        if verbose:
            print("\n[4/4] 廣播交易...")

        result = api.broadcast_transaction(signed_txn)

        if result.get("result"):
            if verbose:
                print("✓ 交易已廣播成功")
                print(f"\n交易ID: {actual_txn['txID']}")
                print("=" * 60)
            return actual_txn["txID"]
        else:
            if verbose:
                print(f"❌ 廣播失敗: {result}")
            return None


class TronQuery:
    """TRON 查詢功能封裝"""

    @staticmethod
    def check_usdt_balance(api: TronAPI, address: str, contract_address: str) -> float:
        """查詢 USDT (TRC20) 餘額"""
        addr_hex = AddressConverter.base58_to_hex(address, include_prefix=False)
        parameter = addr_hex.zfill(64)

        result = api.trigger_constant_contract(
            contract_address=contract_address,
            function_selector="balanceOf(address)",
            parameter=parameter,
            owner_address=address,
        )

        if "constant_result" in result and result["constant_result"]:
            balance_hex = result["constant_result"][0]
            balance_raw = int(balance_hex, 16)
            return balance_raw / 1_000_000

        return 0.0


# ============================================
# 使用範例
# ============================================


def main():
    """主程式 - 示範所有功能的使用方式"""
    print("=" * 70)
    print("TRON 區塊鏈底層實現 - 純 Python 版本")
    print("=" * 70)

    # 1. 地址轉換測試
    print("\n【測試 1】地址格式轉換")
    print("-" * 70)

    test_base58 = "TQyZzVEs9qgLy52JAZQc7ZyxJf13ZNUG8u"
    test_hex = "41a49b6890465f39fce73b18e5c9c5fd9136c70e38"

    print(f"Base58 地址: {test_base58}")
    converted_hex = AddressConverter.base58_to_hex(test_base58)
    print(f"轉為 Hex: {converted_hex}")
    print(f"驗證: {'✓ 通過' if converted_hex == test_hex else '✗ 失敗'}")

    # 2. 從私鑰生成地址
    print("\n【測試 2】從私鑰生成地址")
    print("-" * 70)

    # ⚠️ 警告：請使用環境變數，不要硬編碼私鑰！
    test_private_key = os.environ.get('TRON_TEST_PRIVATE_KEY', '')
    
    if not test_private_key:
        print("⚠️ 未設置 TRON_TEST_PRIVATE_KEY 環境變數")
        print("跳過私鑰相關測試...")
        return

    test_address = KeyGenerator.private_key_to_address(test_private_key)
    print(f"生成的地址: {test_address}")

    # 3. 初始化 API 連接
    print("\n【測試 3】連接到 TRON 網路")
    print("-" * 70)

    api = TronAPI(TronNetwork.NILE_API, api_key=None)
    print("✓ 已連接到 Nile 測試網")

    # 4. 查詢帳戶餘額
    print("\n【測試 4】查詢帳戶餘額")
    print("-" * 70)

    trx_balance = api.get_account_balance(test_address)
    print(f"地址: {test_address}")
    print(f"TRX 餘額: {trx_balance:.6f} TRX")

    usdt_balance = TronQuery.check_usdt_balance(
        api, test_address, TronNetwork.USDT_CONTRACT_NILE
    )
    print(f"USDT 餘額: {usdt_balance:.6f} USDT")

    print("\n" + "=" * 70)
    print("測試完成!")
    print("=" * 70)


if __name__ == "__main__":
    main()
```

### 使用說明

#### 1. 設置環境變數（安全做法）

**Linux/macOS:**
```bash
export TRON_TEST_PRIVATE_KEY="your_private_key_here"
export TRON_API_KEY="your_api_key_here"  # 可選
```

**Windows (PowerShell):**
```powershell
$env:TRON_TEST_PRIVATE_KEY="your_private_key_here"
$env:TRON_API_KEY="your_api_key_here"  # 可選
```

**Python 代碼中使用:**
```python
import os

private_key = os.environ.get('TRON_TEST_PRIVATE_KEY')
if not private_key:
    raise ValueError("請設置 TRON_TEST_PRIVATE_KEY 環境變數")

api_key = os.environ.get('TRON_API_KEY')  # 可選
api = TronAPI(TronNetwork.NILE_API, api_key=api_key)
```

#### 2. 基本使用範例

```python
from tron_impl import *
import os

# 初始化
api = TronAPI(TronNetwork.NILE_API)
private_key = os.environ.get('TRON_TEST_PRIVATE_KEY')

# 生成地址
my_address = KeyGenerator.private_key_to_address(private_key)

# 查詢餘額
balance = api.get_account_balance(my_address)
print(f"餘額: {balance} TRX")

# TRX 轉賬
txid = TronTransfer.transfer_trx(
    api, private_key, "TTqobYiHixykLYyA3WxmCLVCMCySHfigyE", 1.0
)
print(f"交易ID: {txid}")
```

#### 3. 安全檢查清單

保存為 `.py` 文件前，請確認：

- [ ] 移除所有硬編碼的私鑰
- [ ] 使用環境變數管理敏感信息
- [ ] 添加 `.env` 到 `.gitignore`
- [ ] 在測試網充分測試
- [ ] 設置合理的 fee_limit
- [ ] 驗證地址格式正確性
- [ ] 實現錯誤處理機制

---

## 致謝

感謝以下專案和資源:
- [TRON Protocol](https://tron.network/)
- [ecdsa Python 庫](https://github.com/warner/python-ecdsa)
- [PyCryptodome](https://www.pycryptodome.org/)
- [base58 Python 庫](https://github.com/keis/base58)

---

