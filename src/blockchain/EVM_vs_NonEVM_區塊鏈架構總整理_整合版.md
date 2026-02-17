# 🌐 EVM vs Non-EVM 區塊鏈架構總整理（整合版）

## 版本定位

本文件整合以下三份內容：

- `EVM_vs_NonEVM_區塊鏈架構總整理.md`（入門生態與選鏈）
- `EVM_vs_NonEVM_區塊鏈架構總整理_V2_進階版.md`（VM、擴容、遷移成本）
- `EVM_vs_NonEVM_區塊鏈架構總整理_V3_深度工程版.md`（State、Bridge、安全、交易所架構）

適合對象：

- 新手：快速分清 EVM 與 Non-EVM
- 工程師：掌握 VM / State / Rollup / DA / Bridge 全鏈路
- 交易所或基礎設施團隊：評估多鏈錢包與風控設計

---

## 一、先用一句話抓核心

- EVM：工具鏈與生態最成熟，開發遷移成本最低
- Non-EVM：架構多樣、性能上限高，但工具與心智負擔較大

---

## 二、區塊鏈完整分層架構（L1/L2 共通視角）

```text
                ┌──────────────────────┐
                │     Application      │  (DeFi / NFT / GameFi / Social)
                └──────────┬───────────┘
                           │
                ┌──────────┴───────────┐
                │    Execution Layer   │  (EVM / Move VM / SVM)
                └──────────┬───────────┘
                           │
                ┌──────────┴───────────┐
                │    Consensus Layer   │  (PoS / DPoS / BFT)
                └──────────┬───────────┘
                           │
                ┌──────────┴───────────┐
                │      Data Layer      │  (State DB / Trie / DA)
                └──────────────────────┘
```

核心拆解：

- Execution：怎麼算、能不能並行、開發體驗如何
- Consensus：誰決定順序、最終性多快
- Data：狀態如何儲存與驗證、DA 成本如何

---

## 三、VM 與 State 模型對比（真正的架構分水嶺）

### 1. EVM（Ethereum 系）

- Model：Account-based + Global shared state
- Storage：Merkle Patricia Trie
- Contract Language：Solidity 為主
- 優點：生態最大、工具成熟（MetaMask/Hardhat/Foundry）
- 限制：全域狀態競爭明顯，原生並行困難

### 2. Solana / SVM（Rust-based VM）

- Model：Account 分離，交易預先宣告讀寫集合
- 語言：Rust 為主
- 優點：天然並行、高吞吐、低費率
- 限制：開發除錯與運維心智成本高

```text
Transaction:
  Read Accounts  -> A, B
  Write Accounts -> C
若交易間讀寫集合不衝突，可同時執行
```

### 3. Move 系（Sui / Aptos）

- Model：Object/Resource-based
- 特性：資產不可隱式複製，所有權語義更強
- 優點：安全語義清楚，並行化較自然
- 限制：相對 EVM，生態與工具仍在擴張期

```text
EVM:  Balance = number in shared state
Move: Coin    = first-class resource/object
```

---

## 四、擴容路線總覽：L1、L2、Sharding、Parallel EVM

### 1. L1 垂直擴容

- 代表：BSC、Solana、Avalanche
- 作法：提升單鏈吞吐與執行效率
- 取捨：效能上升，去中心化壓力通常也上升

### 2. L2 Rollup（以太坊主流擴容）

```text
User TX
  -> L2 Sequencer 排序
  -> Batch/State Diff
  -> 提交到 Ethereum(L1)
```

#### Optimistic Rollup

- 機制：Fraud Proof + Challenge Period
- 優點：工程成熟、成本較低
- 風險：提款延遲（常見設計約數天級）

#### ZK Rollup

- 機制：Validity Proof
- 優點：無需長挑戰期，安全與最終性路徑更直接
- 風險：Prover 成本高、系統複雜度高

### 3. Sharding

- 觀念：多分片平行處理 + 協調層統合
- 代表思路：NEAR、Ethereum 長期演進方向的一部分

### 4. Parallel EVM（新趨勢）

- 代表：Monad、Sei V2
- 目標：盡量維持 EVM 相容，同時引入平行執行能力

---

## 五、Gas/Fee 與開發者遷移成本

### Gas/Fee 模型（簡化比較）

| 架構 | Fee 模型特徵 | 典型體感 |
|---|---|---|
| EVM | 操作級 Gas 計價 | 精細、但高峰期偏貴 |
| Solana | 基礎費 + 優先費 | 常態便宜、延遲低 |
| Move 系 | 類 EVM 計費 + 可並行優勢 | 在特定場景成本可下降 |

### 遷移成本（EVM 開發者視角）

| 路徑 | 難度 |
|---|---|
| EVM -> EVM L2 | ★ |
| EVM -> Move | ★★★ |
| EVM -> Solana | ★★★★ |

---

## 六、生態地圖：EVM 與 Non-EVM 主流鏈

### EVM 兼容鏈（支援 MetaMask，常見 0x 地址）

#### L1 / 側鏈

| 鏈 | 定位 | 核心特點 |
|---|---|---|
| BNB Smart Chain (BSC) | 幣安生態 | 手續費低、用戶量大 |
| Avalanche C-Chain | 高效能合約鏈 | 秒級確認、子網架構 |
| Polygon PoS | 以太坊側鏈 | 生態完整、應用多 |
| Fantom | 高效能公鏈 | 適合高速交易 |
| Cronos | CeFi + DeFi 整合 | Crypto.com 官方鏈 |
| Celo | 行動支付導向 | 碳中和設計 |

#### L2

| 鏈 | 類型 | 特點 |
|---|---|---|
| Arbitrum One | Optimistic Rollup | 生態成熟 |
| Optimism | Optimistic Rollup | OP Stack 核心成員 |
| Base | OP Stack | Coinbase 生態入口 |
| Mantle | 模組化 L2 | DAO 財庫資源充足 |

#### ZK 系

| 鏈 | 類型 | 特點 |
|---|---|---|
| zkSync Era | zkEVM | 安全與低 Gas |
| Linea | zkEVM | ConsenSys 推進 |
| Scroll | zkEVM | 強調以太坊等效 |

### Non-EVM（需專用錢包，地址/簽名規則不同）

#### 高效能單體鏈

| 鏈 | 常見錢包 | 語言/模型 | 特點 |
|---|---|---|---|
| Solana | Phantom | Rust / SVM | 速度快、Meme 活躍 |
| TON | Tonkeeper | Func | Telegram 生態 |
| Cardano | Yoroi | Haskell | 學術導向 |
| NEAR | NEAR Wallet | Rust | 分片設計 |

#### Move 系

| 鏈 | 常見錢包 | 特點 |
|---|---|---|
| Sui | Sui Wallet | Object 資產模型 |
| Aptos | Petra | 高併發導向 |

#### 多鏈互聯生態

| 生態 | 常見錢包 | 特點 |
|---|---|---|
| Cosmos | Keplr | IBC 跨鏈架構 |
| Polkadot | Polkadot.js | 平行鏈共享安全 |

---

## 七、Rollup 與 Data Availability（DA）

Rollup 不只看 TPS，真正要問：

- 資料可用性放在哪裡（L1 DA、外部 DA、委任 DA）？
- Sequencer 是否去中心化？
- 故障時的恢復與退出機制是否可驗證？

工程重點：

- DA 成本常是長期競爭關鍵
- Sequencer 中心化是目前多數 L2 的現實折衷

---

## 八、跨鏈橋安全模型（高風險重災區）

### 1. Lock & Mint

```text
Chain A: Lock Token
Chain B: Mint Wrapped Token
```

- 優點：容易落地、支援快
- 風險：橋合約漏洞、多簽私鑰風險、Wrapped 資產信任問題

### 2. Light Client Bridge

- 機制：目標鏈驗證來源鏈區塊頭/證明
- 優點：安全性更接近原鏈假設
- 成本：計算與實作複雜度高

### 3. 第三方託管 / 委託模型

- 優點：速度快、整合快
- 風險：中心化信任與治理風險最高

---

## 九、交易所多鏈錢包架構（實務設計）

```text
             ┌──────────────┐
             │   API Layer  │
             └──────┬───────┘
                    │
         ┌──────────┴──────────┐
         │   Wallet Service    │
         └──────────┬──────────┘
                    │
      ┌─────────────┼─────────────┐
      │             │             │
   EVM Node      Solana RPC    Cosmos Node
```

關鍵挑戰：

- 地址格式差異（0x vs base58 等）
- 簽名演算法差異（ECDSA / Ed25519）
- Fee 模型與估算邏輯不同
- Confirm / Finality 標準不同
- 鏈上重組、節點異常、橋事件需要獨立風控

建議：

- 做統一 `Wallet Service` 抽象層
- 每條鏈獨立 adapter + 風險參數
- 監控系統拆成「鏈健康 / 交易生命週期 / 資產對帳」三層

---

## 十、共識與性能（工程化極簡表）

| 類別 | 代表 | 特點 |
|---|---|---|
| PoS | Ethereum | 安全穩定、去中心化權衡完整 |
| DPoS | BSC | 高效率、治理相對集中 |
| BFT 系 | Cosmos | 快速最終性 |
| Tower BFT | Solana | 高吞吐與低延遲 |

| 架構 | 並行性 | 狀態模型 | 開發難度 |
|---|---|---|---|
| EVM | 低 | Global shared state | 低 |
| Solana/SVM | 高 | Account 分離 | 高 |
| Move | 中高 | Object/Resource | 中高 |

---

## 十一、快速選擇指南

### 如果你要快速上手、用 MetaMask、做 DeFi/NFT

- 先走 EVM：Ethereum / Arbitrum / Base / BSC / Polygon

### 如果你要追求高性能或低費率互動

- 看 Solana、Sui、Aptos（需接受新工具鏈與新心智模型）

### 如果你是交易所/基礎設施團隊

- 優先處理多鏈錢包抽象與跨鏈安全，不要先追 TPS 數字

### 如果你要做長期技術投資

- 主修 EVM + 補一條 Non-EVM（Solana 或 Move 系）

---

## 十二、最終總結（前置版）

區塊鏈競爭的真正核心不是單一 TPS，而是四件事：

- Execution 的可擴展性（是否可並行）
- Consensus 的最終性與穩定性
- Data Availability 的長期成本
- Cross-chain 的安全邊界

---

## 十三、選鏈決策矩陣（可加權）

評分說明：每項 1-5 分，總分 = `sum(weight_i * score_i)`。

| 維度 | 權重範例（交易所） | 權重範例（DApp 團隊） | 評分要點 |
|---|---:|---:|---|
| 安全性（歷史事故/客戶端成熟） | 0.25 | 0.20 | 共識穩定、重大事故頻率 |
| 最終性/延遲 | 0.20 | 0.20 | 入帳速度、重組風險 |
| 成本（Gas + 基礎設施） | 0.15 | 0.20 | 鏈上費用、節點/RPC 成本 |
| 生態流動性（TVL/交易深度） | 0.15 | 0.20 | 主流協議與資產可得性 |
| 維運複雜度（節點/索引器） | 0.15 | 0.10 | DevOps 與故障處置成本 |
| 開發效率（SDK/工具鏈） | 0.10 | 0.10 | 語言、測試、除錯成熟度 |

參考判斷：

- 交易所權重通常偏安全與最終性
- 應用團隊權重通常偏成本與生態流動性

---

## 十四、最終性與入帳策略（充值/提幣）

核心原則：`風險越高的鏈，入帳確認數越高`。

| 鏈類型 | 入帳策略 | 提幣風控 | 回滾處置 |
|---|---|---|---|
| Ethereum L1 / 成熟 PoS | 低到中確認數 | 大額二次風控 | 少見，保留人工覆核 |
| EVM 側鏈/高性能鏈 | 中確認數 | 限額 + 時間窗 | 出現重組時自動凍結地址 |
| L2 Rollup | 區分 L2 最終與 L1 最終 | 分層限額 | Sequencer 異常切換慢路徑 |
| 新鏈/小生態鏈 | 高確認數 | 白名單 + 低限額起步 | 預設高風險模式 |

落地建議：

- 入帳系統維護「鏈別風險等級」參數表
- 充值顯示「交易已上鏈 / 交易已最終」雙狀態
- 任何跨鏈資產先做來源橋型別標註

---

## 十五、L2 信任模型矩陣

| L2 類型 | Sequencer | Proof 模型 | DA 位置 | Upgrade 權限風險 | 退出路徑 |
|---|---|---|---|---|---|
| Optimistic Rollup | 常見中心化排序 | Fraud Proof | 常見落 L1 | 需檢查多簽/治理 | 挑戰期後可退出 |
| ZK Rollup | 常見中心化排序 | Validity Proof | 常見落 L1 | 需檢查合約升級權 | 通常較快確認 |
| Validium/外部 DA 類 | 可能中心化 | Validity/混合 | 外部 DA | DA 與治理風險疊加 | 依設計差異大 |

審核清單：

- Sequencer 是否有去中心化 roadmap
- Prover 是否單點供應
- DA 不可用時是否可強制退出
- Upgrade key 是否有 timelock + 多方治理

---

## 十六、Bridge 威脅模型與控制

| 攻擊面 | 典型問題 | 控制措施 |
|---|---|---|
| Bridge 合約 | 驗證邏輯漏洞、重放攻擊 | 形式化驗證、限權、暫停開關 |
| 驗證者/多簽 | 私鑰外洩、治理劫持 | HSM/MPC、門檻簽、分權治理 |
| 預言機/訊息層 | 偽造訊息、延遲攻擊 | 多來源驗證、重放保護、序號檢查 |
| Wrapped 資產 | 抵押不足、脫鉤 | 鏈上儲備證明、即時對帳告警 |

執行建議：

- 橋資產單獨風險分層，不與原生資產同風控
- 異常事件時先停入帳再評估是否停提幣
- 建立橋事件演練（key compromise、鏈停擺、DA 不可用）

---

## 十七、MEV 與排序權（Execution 現實層）

| 生態 | 排序權來源 | 常見 MEV 型態 | 工程對策 |
|---|---|---|---|
| EVM L1/L2 | Builder/Sequencer | Sandwich、Backrun、Liquidation | 私有交易流、slippage 保護 |
| Solana | 高速區塊排序 | 搶跑、清算競爭 | 優先費策略、交易分片提交 |
| 應用層 | 自家撮合/路由 | 路由洩漏、價格滑點 | RFQ、批次撮合、延遲保護 |

重點：

- MEV 不是例外，是默認市場結構
- 架構設計需先定義「可接受 MEV 邊界」

---

## 十八、運維與成本模型（Infra TCO）

| 項目 | EVM 系 | Solana/高性能鏈 | Move 系 |
|---|---|---|---|
| 節點成本 | 中 | 高 | 中高 |
| RPC 壓力 | 中高 | 高 | 中 |
| 索引器複雜度 | 中 | 高 | 中高 |
| 版本升級風險 | 中 | 高 | 中 |

TCO 公式（實務簡化）：

`總成本 = 節點 + RPC + 索引器 + 監控告警 + 值班人力 + 事故損失`

落地建議：

- 關鍵鏈至少雙活 RPC + 異地備援
- 讀寫分離（查詢走索引器，送單走專用 RPC）
- 對高流量鏈做尖峰限流與自動降級

---

## 十九、多鏈錢包實作細節（交易生命週期）

| 主題 | 常見坑 | 實作建議 |
|---|---|---|
| Nonce 管理（EVM） | 併發下 nonce 衝突 | 單地址序列化或 nonce locker |
| Fee Bump | 長時間 pending | 超時自動加價重送 |
| 廣播策略 | 單 RPC 黑洞 | 多 RPC 扇出 + 去重 |
| 重組補償 | 已入帳後回滾 | 延後最終入帳 + 反向沖正流程 |
| 簽名域隔離 | 錯鏈簽名重放 | chainId/domain separation 強制校驗 |

建議狀態機：

`created -> signed -> broadcasted -> seen -> confirmed -> finalized`

---

## 二十、SRE 監控指標與 SLO

必備指標：

- 鏈健康：出塊間隔、節點同步高度差、分叉率
- 交易管線：送單成功率、pending 時長、最終確認時長 P95/P99
- 資產安全：入帳卡單數、橋資產脫鉤率、對帳差額
- 成本效率：單筆交易平均成本、失敗重送率

告警分級：

- P1：入帳中斷、節點全面失聯、橋資產異常
- P2：確認延遲異常飆升、重送率飆升
- P3：成本偏高、局部 RPC 異常

SLO 範例：

- `充值可用性 >= 99.95%`
- `提幣廣播成功率 >= 99.9%`
- `高風險鏈入帳誤判 = 0`

---

## 二十一、最終總結（工程實戰版）

做鏈選型與架構決策時，請固定用以下順序：

1. 先定義安全與最終性邊界  
2. 再評估 DA 與橋模型  
3. 最後才是 TPS 與敘事熱度

這樣能同時降低事故率、維運成本與錯誤入帳風險。
