# Nonce 白話解析：交易與區塊的差異

**Nonce = Number used once（只用一次的數字）**

Nonce 的核心目的只有一個：

> 讓事件不可重放，或可被驗證。

在區塊鏈中，Nonce 主要有兩種用途：

| 類型 | 用途 |
| --- | --- |
| 交易 Nonce | 防止重放攻擊、決定交易順序 |
| 區塊 Nonce | 挖礦時用來找出符合難度的雜湊值 |

## 目錄

- [交易 Nonce（以 Ethereum 為例）](#交易-nonce以-ethereum-為例)
- [區塊 Nonce（以 Bitcoin 為例）](#區塊-nonce以-bitcoin-為例)
- [交易 Nonce vs 區塊 Nonce](#交易-nonce-vs-區塊-nonce)
- [完整範例（Ethereum 交易）](#完整範例ethereum-交易)
- [實務程式範例（ethers.js）](#實務程式範例ethersjs)
- [常見錯誤與排查](#常見錯誤與排查)
- [工程視角](#工程視角)
- [為什麼 Bitcoin 不需要交易 Nonce？](#為什麼-bitcoin-不需要交易-nonce)
- [超精簡總結](#超精簡總結)

---

## 交易 Nonce（以 Ethereum 為例）

適用於 Ethereum 這類帳戶模型（Account Model）區塊鏈。

### 情境

假設你有一個帳戶：

```text
Alice address: 0xAAA
```

你的帳戶目前狀態：

```text
nonce = 3
```

代表你已經送出過 3 筆交易（從 0 開始算）。

### 你現在要轉帳

你送出一筆交易：

```text
from: Alice
to: Bob
value: 1 ETH
nonce: 3
```

區塊鏈節點會檢查：

```text
帳戶目前 nonce 是否為 3？
```

若是，交易會被接受，然後鏈上把 Alice 的 nonce 更新為：

```text
nonce = 4
```

### 為什麼要這樣設計？

#### 防止重放攻擊

假設有人攔截你的交易並重送同一筆資料（`nonce = 3`）。

此時鏈上 nonce 已更新成 `4`，該交易會被拒絕：

```text
Invalid nonce
```

因此無法重放。

#### 強制交易順序

若你送出以下兩筆交易：

```text
Tx1 nonce=3
Tx2 nonce=4
```

礦工必須先打包 `Tx1` 才能打包 `Tx2`。

也就是每個帳戶都有自己的單調遞增序號（sequence number）。

### 交易流程示意

```text
Alice (nonce=3)
    |
    |  發送 Tx(nonce=3)
    v
Ethereum Node
    |
    |  檢查帳戶 nonce == 3 ?
    |
    +-- yes --> 執行交易
                nonce++
                更新為 4
```

### Confirmed Nonce vs Pending Nonce

在 Ethereum 實務中，通常會同時看到兩種 nonce：

- Confirmed（`latest`）：只計算已上鏈交易。
- Pending（`pending`）：包含記憶體池（mempool）中尚未上鏈的交易。

若你是錢包、交易機器人或批次發送器，通常應以 `pending` 為準，避免重複使用 nonce。

### Nonce Gap（序號缺口）

假設帳戶目前應該送 `nonce=6`，但你先送了 `nonce=7`：

- `nonce=7` 交易會留在 mempool 排隊。
- 直到 `nonce=6` 被打包後，`nonce=7` 才能被處理。

這種現象稱為 nonce gap，常見於多執行緒送單或手動補發交易。

### 替換交易與取消交易（同一個 Nonce）

在 Ethereum 可以用「相同 nonce」發新交易覆蓋舊交易（Replace-by-fee 邏輯）：

- 替換交易：同 nonce、相同用途，但提高費率（`maxFeePerGas` / `maxPriorityFeePerGas`）。
- 取消交易：同 nonce，對自己轉 `0 ETH`，並提高費率，目標是讓新交易先被打包。

重點：同 nonce 的交易，最終只會有一筆成功上鏈。

---

## 區塊 Nonce（以 Bitcoin 為例）

適用於 Bitcoin 這類 UTXO + PoW 鏈。

區塊 Nonce 的用途與交易 Nonce 完全不同。

### 挖礦在做什麼？

礦工會嘗試滿足條件：

```text
hash(block_header) < difficulty_target
```

區塊標頭（block header）結構如下：

```text
[version]
[prev_block_hash]
[merkle_root]
[timestamp]
[difficulty]
[nonce]
```

其中 Nonce 是可持續調整的欄位之一。

### 挖礦實際流程

```text
nonce = 0
hash = SHA256(block_header)
不符合

nonce = 1
hash = SHA256(block_header)
不符合

nonce = 2
...
```

持續嘗試直到出現符合難度條件的結果，例如：

```text
hash = 000000000000abc123...
```

### 示意圖

```text
+---------------------+
| Block Header        |
|---------------------|
| prev_hash           |
| merkle_root         |
| timestamp           |
| difficulty          |
| nonce = 18273645    |
+---------------------+
            |
            v
          SHA256
            |
            v
00000000000abcd1234  (成功)
```

區塊 Nonce 的本質：

> 改變輸入值，讓雜湊輸出改變，並在搜尋空間中暴力枚舉可行解。

### 32-bit Nonce 限制與 extra nonce

Bitcoin 區塊標頭的 nonce 是 32-bit，最大約 `4.29e9`。當 nonce 全部試完仍找不到解時，礦工會：

1. 修改 coinbase 交易中的 extra nonce。
2. 使 Merkle Root 改變。
3. 重新從 nonce=0 開始挖。

因此實際可搜尋空間遠大於單純 32-bit nonce。

---

## 交易 Nonce vs 區塊 Nonce

| 類型 | 交易 Nonce | 區塊 Nonce |
| --- | --- | --- |
| 用途 | 防止重放 | 挖礦 |
| 控制者 | 帳戶持有人 | 礦工 |
| 是否單調遞增 | 是 | 不一定 |
| 是否儲存在狀態中 | 是 | 是（儲存在區塊標頭） |
| 類比 | sequence number | brute-force counter |

---

## 完整範例（Ethereum 交易）

```json
{
  "nonce": 3,
  "gasPrice": "20 gwei",
  "gasLimit": 21000,
  "to": "0xBBB",
  "value": "1 ETH",
  "data": ""
}
```

簽名後可表示為：

```text
raw_tx = RLP_encode(tx) + signature
```

礦工驗證重點：

1. 簽名是否正確
2. Nonce 是否正確
3. 餘額是否足夠

若 Nonce 錯誤，交易直接拒絕。

---

## 實務程式範例（ethers.js）

```ts
import { ethers } from "ethers";

const provider = new ethers.JsonRpcProvider(process.env.RPC_URL);
const wallet = new ethers.Wallet(process.env.PRIVATE_KEY!, provider);

async function sendTx() {
  const nonce = await provider.getTransactionCount(wallet.address, "pending");

  const tx = await wallet.sendTransaction({
    to: "0x000000000000000000000000000000000000dEaD",
    value: ethers.parseEther("0.001"),
    nonce,
    maxFeePerGas: ethers.parseUnits("40", "gwei"),
    maxPriorityFeePerGas: ethers.parseUnits("2", "gwei"),
    gasLimit: 21000
  });

  console.log("tx hash:", tx.hash);
}

sendTx().catch(console.error);
```

實務要點：

- 先取 `pending` nonce，再簽名送出。
- 同一帳戶並行送交易時，要自己做 nonce 鎖（mutex/queue）。
- 交易卡住時，使用同 nonce 並提高費率做替換。

---

## 常見錯誤與排查

| 錯誤訊息 | 常見原因 | 建議處理 |
| --- | --- | --- |
| `nonce too low` | 你使用了已被消耗的 nonce | 重新查 `pending` nonce 後重送 |
| `replacement transaction underpriced` | 同 nonce 替換交易加價幅度不夠 | 提高 `maxFeePerGas` 與 `maxPriorityFeePerGas` |
| `already known` | 送了完全相同的 raw transaction | 可忽略或改 nonce/費率重送 |
| `insufficient funds for gas * price + value` | 餘額不足支付 value + gas | 補足資金或調整金額與費率 |

排查順序建議：

1. 先查帳戶 `latest` 與 `pending` nonce。
2. 再查該 nonce 是否已有 pending 交易。
3. 判斷要等待、替換，或取消該 nonce 的交易。

---

## ASCII 流程圖

### Ethereum 交易 Nonce 流程（含替換交易）

```text
┌──────────────────────────┐
│ 取得 nonce (pending)     │
└────────────┬─────────────┘
             v
┌──────────────────────────┐
│ 建立並簽名交易 Tx(nonce) │
└────────────┬─────────────┘
             v
┌──────────────────────────┐
│ 廣播到 mempool           │
└────────────┬─────────────┘
             v
┌──────────────────────────┐
│ 交易是否快速被打包？     │
└───────┬───────────┬──────┘
        │是         │否
        v           v
┌──────────────┐  ┌────────────────────────────┐
│ nonce + 1    │  │ 同 nonce 提高費率重發       │
│ 下一筆交易   │  │ (replace / cancel)          │
└──────┬───────┘  └─────────────┬──────────────┘
       │                        v
       └───────────────>┌──────────────────────┐
                        │ 新交易被打包後生效    │
                        │ 舊交易失效            │
                        └──────────────────────┘
```

### Bitcoin 區塊 Nonce 搜尋流程

```text
┌──────────────────────────────────┐
│ 組裝候選區塊 (header + txs)      │
└────────────────┬─────────────────┘
                 v
┌──────────────────────────────────┐
│ nonce = 0                        │
└────────────────┬─────────────────┘
                 v
┌──────────────────────────────────┐
│ hash(header) < target ?          │
└───────┬──────────────────┬───────┘
        │是                │否
        v                  v
┌──────────────────┐   ┌───────────────────────┐
│ 找到有效區塊      │   │ nonce++                │
│ 廣播出塊          │   └──────────┬────────────┘
└──────────────────┘              v
                         ┌───────────────────────┐
                         │ nonce 用盡？           │
                         └───────┬────────┬──────┘
                                 │否      │是
                                 v        v
                             (回到 hash)  ┌────────────────────────┐
                                          │ 修改 extra nonce /     │
                                          │ coinbase / merkle root │
                                          │ nonce 重設為 0          │
                                          └──────────┬─────────────┘
                                                     v
                                                  (回到 hash)
```

---

## 工程視角

可把 Ethereum 帳戶想成：

```c
struct Account {
    uint256 balance;
    uint256 nonce;
}
```

每次成功交易後：

```text
account.nonce++
```

這是在防止狀態機（state machine）被 replay，確保每次狀態轉移（state transition）具唯一性。

---

## 為什麼 Bitcoin 不需要交易 Nonce？

因為 Bitcoin 使用 UTXO 模型：

- 每筆輸出只能花一次
- 花掉就消失

它天然能防止 double-spend。

Ethereum 屬於帳戶模型：

- 帳戶持續存在
- 需要 sequence 機制（Nonce）保證順序與唯一性

---

## 實作檢查清單

- 送交易前，先取 `pending` nonce。
- 同帳戶避免多個執行緒同時各自抓 nonce。
- 為每筆 nonce 記錄交易哈希，避免重複送單。
- 設定重試策略時，優先「同 nonce 加價替換」，而不是直接跳下一個 nonce。
- 定期清理卡住的 pending nonce，避免後續交易全部阻塞。

---

## 超精簡總結

### Ethereum 交易 Nonce

> 我是第 N 筆交易，不能重來。

### Bitcoin 區塊 Nonce

> 我要試出符合難度條件的雜湊值。
