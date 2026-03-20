# Transformer 在交易策略中的應用

## 一句話理解

> Transformer 就像一個「記憶力超強的分析師」，能同時看數百根 K 線的關係，找出隱藏的規律來做交易決策。

---

## Transformer vs 基因演算法（GA）：根本差異

```
┌─────────────────────────────────────────────────────────┐
│              基因演算法 (Genetic Algorithm)                │
│                                                         │
│  第 1 代策略群          交叉/變異           第 N 代策略群   │
│  ┌───┐ ┌───┐ ┌───┐    篩選適者          ┌───┐           │
│  │RSI│ │MA │ │VOL│  ──────────────►     │最佳│           │
│  │>70│ │交叉│ │放大│   淘汰劣者          │組合│           │
│  └───┘ └───┘ └───┘                      └───┘           │
│                                                         │
│  白話：像抽籤試菜單，吃過幾百種組合後，                      │
│        留下最好吃的那幾道。                                │
│  專業術語：參數空間搜索 (Parameter Space Search)           │
│           適應度函數 (Fitness Function)                   │
│           交叉算子 (Crossover Operator)                   │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                  Transformer                            │
│                                                         │
│  歷史數據             自注意力機制            預測/決策    │
│  ┌──┬──┬──┬──┐      (Self-Attention)      ┌────────┐   │
│  │K1│K2│K3│K4│  ──► 每根 K 線都能        ──► │明天漲跌│   │
│  │  │  │  │  │      「看到」所有其他        │買/賣/持│   │
│  └──┴──┴──┴──┘      K 線的資訊             └────────┘   │
│                                                         │
│  白話：像一個讀了十年盤的老手，看到現在的走勢               │
│        就知道「這跟 2020/03 崩盤前好像」。                 │
│  專業術語：序列建模 (Sequence Modeling)                    │
│           注意力權重 (Attention Weights)                  │
│           表示學習 (Representation Learning)              │
└─────────────────────────────────────────────────────────┘
```

**關鍵差異表：**

| 面向 | 基因演算法 (GA) | Transformer |
|------|----------------|-------------|
| 核心思路 | 暴力搜索最佳參數組合 | 學習數據中的模式 (Pattern) |
| 策略形式 | 規則型 (If-Then) | 黑箱型 (端對端預測) |
| 可解釋性 | 高（看得到規則） | 低（需要額外工具解釋） |
| 過擬合風險 | 中（靠驗證集控制） | 高（模型容量大，需正則化） |
| 適應新數據 | 需重新演化 | 可微調 (Fine-tune) |
| 白話比喻 | 用排列組合找最好的食譜 | 培養一個有經驗的廚師 |

---

## 四種主要應用場景

### 1. 時序預測 (Time Series Forecasting)

```
輸入序列 (Input Sequence)
┌─────┬─────┬─────┬─────┬─────┬─────┐
│Day 1│Day 2│Day 3│Day 4│Day 5│Day 6│  ← 每天的特徵向量
│OHLCV│OHLCV│OHLCV│OHLCV│OHLCV│OHLCV│    (開高低收量)
└──┬──┴──┬──┴──┬──┴──┬──┴──┬──┴──┬──┘
   │     │     │     │     │     │
   ▼     ▼     ▼     ▼     ▼     ▼
┌──────────────────────────────────────┐
│    Positional Encoding (位置編碼)     │  ← 告訴模型「誰在前誰在後」
├──────────────────────────────────────┤
│    Multi-Head Self-Attention         │  ← Day1 可以直接關注 Day6
│    (多頭自注意力機制)                  │    不需要像 RNN 一步步傳遞
├──────────────────────────────────────┤
│    Feed-Forward Network              │
│    (前饋神經網路)                      │
├──────────────────────────────────────┤
│    Output: 預測 Day 7 的收盤價         │
└──────────────────────────────────────┘
```

**白話舉例：**
想像你在看一部 120 集的連續劇（120 天的股價）。RNN 像是從第 1 集看到第 120 集，到最後已經忘了第 1 集演什麼。Transformer 則像是能同時攤開所有集數的劇本，直接發現「第 3 集的伏筆在第 118 集回收了」。

**專業用詞：**
- **OHLCV**：Open/High/Low/Close/Volume（開盤價/最高價/最低價/收盤價/成交量）
- **Positional Encoding**（位置編碼）：因為 Transformer 天生不知道順序，需要額外注入時間資訊
- **Long-range Dependency**（長程依賴）：能捕捉相隔很遠的數據點之間的關係

---

### 2. 多因子選股 (Multi-Factor Stock Selection)

```
                        因子 = "單字"
                        股票 = "句子"

股票 A 的因子序列：
┌────────┬────────┬────────┬────────┬────────┐
│ ROE    │ 營收   │ 本益比  │ 法人   │ 融資   │
│ 25%    │ 成長20%│ PE=12  │ 買超   │ 減少   │
└───┬────┴───┬────┴───┬────┴───┬────┴───┬────┘
    │        │        │        │        │
    ▼        ▼        ▼        ▼        ▼
┌──────────────────────────────────────────────┐
│           Transformer Encoder                 │
│                                              │
│  Self-Attention 發現：                        │
│  「ROE 高 + 法人買超 + 融資減少」              │
│   這三個因子一起出現時，特別重要！              │
│   (= 注意力權重高)                            │
│                                              │
│  類似 NLP 中理解                              │
│  「銀行」在「河岸」vs「金融」語境的不同含義     │
└──────────────────┬───────────────────────────┘
                   ▼
            ┌──────────────┐
            │ 評分：0.87    │  ← 高分 = 值得買入
            │ (買入信號)     │
            └──────────────┘
```

**白話舉例：**
傳統選股像是拿一張清單逐項打勾（ROE > 15% ? 勾！PE < 20 ? 勾！）。Transformer 選股則像是一個老手看完所有數據後說：「這幾個指標**一起**看才有意義，光看單一指標會被騙。」它學會了因子之間的**交互作用 (Interaction Effect)**。

**專業用詞：**
- **Embedding**（嵌入向量）：把每個因子轉成模型能理解的數字表示
- **Cross-Attention**（交叉注意力）：讓不同因子之間互相參照
- **Alpha Factor**（超額報酬因子）：能帶來超越大盤報酬的因子

---

### 3. 情緒分析 (Sentiment Analysis)

```
原始文本                    Transformer 處理流程
─────────                  ──────────────────

「台積電法說會釋出           Tokenization (分詞)
  正面展望，但外資              │
  卻大量賣超」                  ▼
                          ┌──────────────────┐
                          │ [正面展望] [但]    │
                          │ [外資] [大量賣超]  │
                          └────────┬─────────┘
                                   │
                          Self-Attention 發現：
                          「但」這個轉折詞讓
                          「正面展望」的影響力
                           被大幅削弱
                                   │
                                   ▼
                          ┌──────────────────┐
                          │ 情緒分數：-0.3    │
                          │ (偏空，因為行動    │
                          │  比言語更重要)     │
                          └──────────────────┘
                                   │
                                   ▼
                          交易信號：減碼 / 觀望
```

**白話舉例：**
就像你跟朋友說「這家餐廳東西很好吃，**但是**好貴」。人類聽得出這是偏負面的評價。Transformer 也學會了「但是」後面的內容通常更重要，所以它不會被前半段的正面詞彙騙到。

**專業用詞：**
- **NLP（Natural Language Processing）**：自然語言處理
- **Tokenization**（分詞）：把文本切成模型能處理的最小單位
- **Sentiment Score**（情緒分數）：量化市場情緒的數值，通常 -1（極度悲觀）到 +1（極度樂觀）
- **Alternative Data**（替代數據）：新聞、社群媒體等非傳統金融數據

---

### 4. 強化學習結合 (Transformer + Reinforcement Learning)

```
這是最接近「自動產生交易策略」的做法

┌──────────────────────────────────────────────────────┐
│                    交易環境 (Environment)              │
│  ┌────────────────────────────────────────────────┐  │
│  │ 市場狀態 (State)                                │  │
│  │ • 過去 N 天的 OHLCV                             │  │
│  │ • 當前持倉、資金                                 │  │
│  │ • 技術指標 (RSI, MACD, 布林通道...)              │  │
│  └───────────────────┬────────────────────────────┘  │
│                      │                               │
│                      ▼                               │
│  ┌────────────────────────────────────────────────┐  │
│  │ Transformer (策略網路 / Policy Network)         │  │
│  │                                                │  │
│  │ 用 Self-Attention 分析所有歷史狀態              │  │
│  │ 輸出動作機率分布：                               │  │
│  │   買入 30% | 賣出 10% | 持有 60%               │  │
│  └───────────────────┬────────────────────────────┘  │
│                      │                               │
│                      ▼                               │
│              ┌──────────────┐                        │
│              │ 執行動作      │                        │
│              │ (Action)     │                        │
│              └──────┬───────┘                        │
│                     │                                │
│                     ▼                                │
│              ┌──────────────┐                        │
│              │ 獲得獎勵      │  ← 賺錢 = 正獎勵      │
│              │ (Reward)     │    賠錢 = 負獎勵       │
│              └──────┬───────┘    (含交易成本)        │
│                     │                                │
│                     ▼                                │
│              反覆訓練數千回合                          │
│              (Episodes)                              │
│              直到學會穩定獲利                          │
└──────────────────────────────────────────────────────┘
```

**白話舉例：**
想像訓練一個打電動的 AI。遊戲畫面就是「盤面」，按鍵就是「買/賣/持有」，得分就是「賺多少錢」。AI 一開始亂按（隨機交易），但玩了幾萬局後，它摸出了一套贏錢的操作手法。這個「大腦」就是 Transformer。

**與基因演算法對比：**
- GA 產生的策略：`如果 RSI > 70 且 MA5 > MA20 則買入` → 人看得懂
- Transformer + RL 產生的策略：一個神經網路權重矩陣 → 人看不懂，但可能更強

**專業用詞：**
- **DRL（Deep Reinforcement Learning）**：深度強化學習
- **Policy Network**（策略網路）：決定在每個狀態下該採取什麼動作的神經網路
- **Reward Shaping**（獎勵設計）：如何定義「好的交易行為」，例如考慮夏普比率而非單純報酬
- **Episode**（回合）：一次完整的模擬交易過程（如模擬一整年）
- **Action Space**（動作空間）：模型可以選擇的所有動作集合

---

## 常見疑惑 Q&A

### Q1: Transformer 不是拿來做翻譯/ChatGPT 的嗎？怎麼能做交易？

```
NLP 領域                          金融領域
────────                         ────────
句子 = 一串文字 token              K 線 = 一串時間點的特徵向量
理解上下文語意                     理解價格走勢的前後關係
預測下一個字                       預測下一個時間點的價格/動作

    兩者的數學結構完全一樣！
    都是「序列 → 序列」的問題
```

**白話：** Transformer 不在乎它處理的是文字還是數字，它只看到「一排東西」，然後學習這排東西之間的關係。股價序列對它來說，跟一段英文句子沒有本質區別。

---

### Q2: 哪種方法比較適合散戶？

| 方法 | 難度 | 資料需求 | 算力需求 | 散戶可行性 |
|------|------|---------|---------|-----------|
| GA 暴力搜參數 | 中 | 低 | 低 | 高 - 用 Python 幾百行就能跑 |
| Transformer 預測 | 高 | 中 | 中 | 中 - 需要 GPU，但 Colab 免費可用 |
| Transformer + RL | 很高 | 高 | 高 | 低 - 需要大量調參和算力 |
| 情緒分析 | 中 | 需爬蟲 | 低 | 中 - 可用預訓練模型 |

---

### Q3: Transformer 做交易真的能賺錢嗎？

**誠實的答案：** 不保證。主要挑戰：

1. **過擬合 (Overfitting)**：模型可能只是「背答案」，在歷史數據上表現很好，但實盤慘賠
2. **市場非定態 (Non-stationary)**：市場規則會變，2020 年有效的模式到 2025 年可能失效
3. **交易成本 (Transaction Cost)**：模型可能頻繁交易，手續費吃掉利潤
4. **滑價 (Slippage)**：回測假設你能以收盤價成交，但實際上不一定

```
                    回測績效
                    ↑
                    │    ╱ 回測報酬（看起來很美）
                    │   ╱
                    │  ╱
                    │ ╱─────── 扣除交易成本
                    │╱
                    ├──────── 加上滑價影響
                    │╲
                    │ ╲────── 考慮過擬合
                    │  ╲
                    │   ╲  實際報酬（現實很骨感）
                    └──────────────────────► 時間
```

---

## FinLab + Transformer 實戰整合

### 整體架構：資料流全景圖

```
┌─────────────────────────────────────────────────────────────────┐
│                     FinLab 資料層 (Data Layer)                   │
│                                                                 │
│  finlab.data.get('price:收盤價')          ← 日頻 OHLCV          │
│  finlab.data.get('monthly_revenue:當月營收') ← 月頻基本面        │
│  finlab.data.get('price_earning_ratio:本益比') ← 估值指標        │
│  finlab.data.get('institutional_investors:外資買賣超') ← 籌碼面  │
│  finlab.data.get('etl:adj_close')         ← 還原除權息收盤價     │
│                                                                 │
│  輸出格式：FinlabDataFrame (index=日期, columns=股票代號)         │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                  特徵工程層 (Feature Engineering)                 │
│                                                                 │
│  1. 對齊頻率：月營收 → resample 到日頻（前向填充 ffill）          │
│  2. 計算衍生特徵：報酬率、波動率、技術指標                        │
│  3. 組裝特徵張量：(股票數 × 時間窗口 × 特徵數)                   │
│  4. 標準化 (Normalization)：Z-score 或 Min-Max                   │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Transformer 模型層 (Model Layer)                │
│                                                                 │
│  輸入：過去 60 天的多維特徵序列                                   │
│  輸出：未來 5 天的預測報酬 / 漲跌機率 / 選股評分                  │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│               FinLab 回測層 (Backtest Layer)                     │
│                                                                 │
│  Transformer 預測結果 → 轉換成 FinlabDataFrame 的選股條件         │
│  → finlab.backtest.sim() 回測                                   │
│  → 績效報告（CAGR、Sharpe、MaxDrawdown）                        │
└─────────────────────────────────────────────────────────────────┘
```

**白話：** FinLab 負責「搬食材」（抓資料）和「試吃評分」（回測），Transformer 負責「炒菜」（學規律做預測）。兩者各司其職。

---

### 場景 A：用 Transformer 預測股價，FinLab 回測

這是最直覺的結合方式：模型預測漲跌，FinLab 驗證能不能賺錢。

```python
import finlab
from finlab import data
import pandas as pd
import numpy as np
import torch
import torch.nn as nn

finlab.login('YOUR_API_KEY')

# =========================================
# Step 1: 用 FinLab 取得乾淨的台股數據
# =========================================

close = data.get('price:收盤價')          # FinlabDataFrame, shape: (日期, 股票代號)
high  = data.get('price:最高價')
low   = data.get('price:最低價')
vol   = data.get('price:成交股數')

# FinLab 的好處：自動處理除權息、停牌、下市
adj_close = data.get('etl:adj_close')     # 還原除權息後的收盤價

# =========================================
# Step 2: 特徵工程 — 把原始數據變成模型吃得下的格式
# =========================================

# 計算技術指標（用 FinlabDataFrame 的語法糖）
returns_1d  = adj_close.pct_change(1)     # 日報酬率
returns_5d  = adj_close.pct_change(5)     # 週報酬率
volatility  = returns_1d.rolling(20).std()  # 20 日波動率
ma_ratio    = adj_close / adj_close.rolling(20).mean()  # 股價 / 20MA 比值

# 加入基本面（FinLab 自動對齊不同頻率的數據！）
revenue = data.get('monthly_revenue:當月營收')
rev_yoy = revenue.pct_change(12)          # 營收年增率（月頻，FinLab 自動 ffill 到日頻）

# 加入籌碼面
foreign_buy = data.get('institutional_investors:外資買賣超')
```

```
特徵組裝示意圖：把多張 FinlabDataFrame 堆疊成 3D 張量

        股票 2330 的特徵矩陣（60天 × 6特徵）
        ┌─────────────────────────────────────────┐
        │ 日期    │報酬率│波動率│MA比│營收YoY│外資│  │
        ├─────────┼──────┼──────┼────┼───────┼────┤  │
        │ Day -60 │ 0.02 │ 0.15 │1.03│ 0.25  │ +5 │  │
        │ Day -59 │-0.01 │ 0.14 │1.02│ 0.25  │ -2 │  │
        │  ...    │ ...  │ ...  │... │  ...  │... │  │
        │ Day -1  │ 0.03 │ 0.18 │0.98│ 0.30  │+10 │  │
        └─────────────────────────────────────────┘
            ↑
            這就是 Transformer 的輸入序列
            序列長度 = 60（回看窗口）
            每個 token 的維度 = 6（特徵數）
```

```python
# =========================================
# Step 3: 組裝 PyTorch Dataset
# =========================================

def build_dataset(stock_id, lookback=60, horizon=5):
    """
    為單一股票建立訓練資料

    Args:
        stock_id: 股票代號，如 '2330'
        lookback: 回看天數（= Transformer 的序列長度）
        horizon:  預測天數（未來幾天的報酬）

    Returns:
        X: shape (樣本數, lookback, 特徵數) — 模型輸入
        y: shape (樣本數,) — 未來 horizon 天的報酬率
    """
    # 把各特徵 DataFrame 對齊、取出單一股票
    features = pd.DataFrame({
        'returns': returns_1d[stock_id],
        'volatility': volatility[stock_id],
        'ma_ratio': ma_ratio[stock_id],
        'rev_yoy': rev_yoy[stock_id],
        'foreign': foreign_buy[stock_id],
    }).dropna()

    # 標準化（重要！Transformer 對數值尺度敏感）
    features = (features - features.rolling(252).mean()) / features.rolling(252).std()
    features = features.dropna()

    # 未來 horizon 天的報酬作為標籤
    future_ret = adj_close[stock_id].pct_change(horizon).shift(-horizon)

    X_list, y_list = [], []
    for i in range(lookback, len(features) - horizon):
        X_list.append(features.iloc[i-lookback:i].values)
        y_list.append(future_ret.iloc[i])

    return np.array(X_list), np.array(y_list)

X, y = build_dataset('2330', lookback=60, horizon=5)
# X.shape = (樣本數, 60, 5)
# y.shape = (樣本數,)
```

```
時間軸上的滑動窗口 (Sliding Window)：

Day:  1   2   3  ...  60  61  62  ...  120  121
      ├──── 樣本 1 ────┤►y1
          ├──── 樣本 2 ────┤►y2
              ├──── 樣本 3 ────┤►y3
                                ...
                        ├──── 樣本 N ────┤►yN

每個樣本 = 60 天的特徵矩陣
每個 y   = 第 61~65 天的累積報酬率
```

```python
# =========================================
# Step 4: Transformer 模型定義
# =========================================

class StockTransformer(nn.Module):
    """
    用 Transformer Encoder 做股價預測

    白話：就是把一段時間的行情數據丟進去，
         模型自己學哪些天的哪些特徵最重要，
         然後輸出一個預測值。
    """
    def __init__(self, d_feature=5, d_model=64, nhead=4, num_layers=2, dropout=0.1):
        super().__init__()

        # 把原始特徵投影到模型維度
        self.input_proj = nn.Linear(d_feature, d_model)

        # 位置編碼：告訴模型「第幾天」
        self.pos_encoding = nn.Parameter(torch.randn(1, 200, d_model) * 0.02)

        # Transformer Encoder
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,          # 多頭注意力的頭數
            dim_feedforward=128,  # FFN 隱藏層大小
            dropout=dropout,
            batch_first=True
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)

        # 輸出頭：預測未來報酬
        self.output_head = nn.Sequential(
            nn.Linear(d_model, 32),
            nn.ReLU(),
            nn.Linear(32, 1)     # 輸出 1 個數字 = 預測報酬率
        )

    def forward(self, x):
        # x shape: (batch, seq_len, d_feature)
        x = self.input_proj(x)                          # → (batch, seq_len, d_model)
        x = x + self.pos_encoding[:, :x.size(1), :]     # 加上位置資訊
        x = self.transformer(x)                          # Self-Attention 魔法發生處
        x = x[:, -1, :]                                  # 取最後一天的隱藏狀態
        return self.output_head(x).squeeze(-1)           # → (batch,) 預測報酬
```

```
模型內部資料流：

輸入: (batch=32, seq_len=60, features=5)
          │
    ┌─────▼──────┐
    │ Linear 5→64│  Input Projection (特徵投影)
    └─────┬──────┘
          │ + Positional Encoding
    ┌─────▼──────────────────────────┐
    │ Transformer Encoder Layer × 2  │
    │                                │
    │  ┌──────────────────────┐      │
    │  │ Multi-Head Attention │      │  ← Day 1 可以直接看 Day 60
    │  │ (4 heads × 16 dim)  │      │
    │  └──────────┬───────────┘      │
    │  ┌──────────▼───────────┐      │
    │  │ Feed-Forward Network │      │
    │  │ 64 → 128 → 64       │      │
    │  └──────────┬───────────┘      │
    └─────────────┼──────────────────┘
          ┌───────▼────────┐
          │ 取最後一天的輸出 │  ← 濃縮了 60 天所有資訊
          └───────┬────────┘
          ┌───────▼────────┐
          │ Linear 64→32→1 │  Output Head
          └───────┬────────┘
                  ▼
          預測報酬: 0.023 (= 預計漲 2.3%)
```

```python
# =========================================
# Step 5: 訓練 → 預測 → 轉回 FinLab 格式回測
# =========================================

# --- 訓練（簡化版）---
model = StockTransformer(d_feature=5)
optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
loss_fn = nn.MSELoss()

# 時間序列切割（不能隨機切！要用時間前後切）
split = int(len(X) * 0.7)
X_train, X_test = X[:split], X[split:]
y_train, y_test = y[:split], y[split:]

# 訓練迴圈（實際需要更多 epoch 和 early stopping）
for epoch in range(50):
    pred = model(torch.FloatTensor(X_train))
    loss = loss_fn(pred, torch.FloatTensor(y_train))
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

# --- 對所有股票做預測，組裝成 FinlabDataFrame ---
stock_list = ['2330', '2317', '2454', '2881', '2882']  # 示例

predictions = {}
for sid in stock_list:
    X_s, _ = build_dataset(sid)
    with torch.no_grad():
        pred = model(torch.FloatTensor(X_s[-1:]))  # 用最新數據預測
        predictions[sid] = pred.item()

# 轉成 FinLab 能用的選股條件
# 核心技巧：Transformer 的預測結果 → FinlabDataFrame → backtest.sim()
```

---

### 場景 B：Transformer 多因子選股 + FinLab 回測

```
這是最適合 FinLab 生態的用法：
Transformer 當「智慧選股器」，FinLab 當「回測引擎」

┌──────────────── 每月月底 ──────────────────┐
│                                            │
│  FinLab 取數據                              │
│  ├─ 基本面：ROE、營收成長、毛利率            │
│  ├─ 估值面：本益比、股價淨值比               │
│  ├─ 技術面：月報酬率、波動率、RSI            │
│  └─ 籌碼面：外資買賣超、融資餘額             │
│           │                                │
│           ▼                                │
│  組裝成特徵向量（每檔股票一個向量）           │
│  ┌────────────────────────────────┐        │
│  │ 2330: [0.25, 0.15, 12, ...]   │        │
│  │ 2317: [0.18, 0.08, 15, ...]   │        │
│  │ 2454: [0.30, 0.22, 28, ...]   │        │
│  │ ...                           │        │
│  └────────────┬───────────────────┘        │
│               ▼                            │
│  Transformer 打分                           │
│  ┌────────────────────────────────┐        │
│  │ 2330: 0.82 分 ★                │        │
│  │ 2317: 0.45 分                  │        │
│  │ 2454: 0.91 分 ★★               │        │  ← 分數 = 預期報酬
│  │ ...                           │        │
│  └────────────┬───────────────────┘        │
│               ▼                            │
│  選前 N 名 → 產生 FinLab position           │
│  position['2454'] = True                   │
│  position['2330'] = True                   │
│               │                            │
└───────────────┼────────────────────────────┘
                ▼
        finlab.backtest.sim(position, ...)
        → 績效報告
```

```python
# =========================================
# 完整範例：Transformer 多因子月頻選股
# =========================================

import finlab
from finlab import data
from finlab.backtest import sim

finlab.login('YOUR_API_KEY')

# --- 取 FinLab 數據 ---
close    = data.get('price:收盤價')
roe      = data.get('fundamental_features:ROA稅後息前')  # 季頻，FinLab 自動對齊
rev      = data.get('monthly_revenue:當月營收')
rev_yoy  = rev.pct_change(12)                            # 營收年增率
pe       = data.get('price_earning_ratio:本益比')
foreign  = data.get('institutional_investors:外資買賣超')

# --- 月底取樣，組裝特徵 ---
features_monthly = {
    'roe': roe.resample('M').last(),
    'rev_yoy': rev_yoy.resample('M').last(),
    'pe': pe.resample('M').last(),
    'momentum': close.pct_change(20).resample('M').last(),
    'foreign_cum': foreign.rolling(20).sum().resample('M').last(),
}

# --- 對每個月、每檔股票，用 Transformer 打分 ---
# （這裡用 Cross-Sectional Transformer：同一時間點，
#   比較所有股票之間的相對關係）

class CrossSectionalTransformer(nn.Module):
    """
    橫截面 Transformer：
    不是看一檔股票的時間序列，
    而是看同一時間點所有股票的因子，
    學習「哪些因子組合代表會漲的股票」

    白話：像老師改考卷，
         看完全班的答案後給每個人排名，
         而不是只看一個人的答案。
    """
    def __init__(self, d_feature=5, d_model=32, nhead=4, num_layers=1):
        super().__init__()
        self.proj = nn.Linear(d_feature, d_model)
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model, nhead=nhead,
            dim_feedforward=64, batch_first=True
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers)
        self.head = nn.Linear(d_model, 1)

    def forward(self, x):
        # x: (1, num_stocks, d_feature) — 一個月所有股票的因子
        x = self.proj(x)
        x = self.transformer(x)   # 股票之間互相 attend
        return self.head(x).squeeze(-1)  # (1, num_stocks) 分數

# --- 預測結果 → FinLab position ---
# 每月選分數最高的 10 檔股票
# position 是一個 FinlabDataFrame (bool)，True = 持有

position = close > 0  # 初始化為全 False 的同型 DataFrame
position[:] = False

for month_end in features_monthly['roe'].index:
    # 組裝該月的特徵矩陣
    feat_matrix = pd.DataFrame({
        k: v.loc[month_end] for k, v in features_monthly.items()
    }).dropna()

    if len(feat_matrix) < 20:
        continue

    # Transformer 打分
    with torch.no_grad():
        scores = model(torch.FloatTensor(feat_matrix.values).unsqueeze(0))

    # 選前 10 名
    top_stocks = feat_matrix.index[scores.squeeze().argsort(descending=True)[:10]]

    if month_end in position.index:
        position.loc[month_end, top_stocks] = True

# --- FinLab 回測！---
report = sim(
    position,
    resample='M',           # 月頻換股
    position_limit=0.1,     # 單檔上限 10%
    fee_ratio=1.425/1000,   # 手續費
    stop_loss=0.08,         # 停損 8%
    trade_at_price='open',  # 隔日開盤價成交
    name='Transformer 多因子選股'
)
```

---

### 場景 C：Transformer 情緒分析 + FinLab 訊號融合

```
新聞/社群               Transformer (NLP)            FinLab 數據
─────────              ──────────────────           ──────────

「台積電法說          ┌──────────────────┐
  展望樂觀」    ─────►│ 情緒分數: +0.7   │
                      └────────┬─────────┘
                               │
「外資連續           ┌──────────▼─────────────────────────┐
  賣超三天」         │       訊號融合層                     │
                     │                                    │
FinLab 籌碼面 ──────►│  情緒 +0.7 × 權重 0.3              │
  外資買賣超         │  + 籌碼面 -0.5 × 權重 0.3           │
                     │  + 技術面 +0.2 × 權重 0.2           │
FinLab 技術面 ──────►│  + 基本面 +0.8 × 權重 0.2           │
  RSI / MACD         │  = 綜合分數 +0.25                  │
                     │                                    │
FinLab 基本面 ──────►│  +0.25 > 閾值 0.1 → 買入           │
  營收 / ROE         └────────────┬───────────────────────┘
                                  │
                                  ▼
                          finlab.backtest.sim()
```

---

### 實務注意事項

#### FinLab 數據頻率對齊（最容易踩的坑）

```
問題：不同數據的更新頻率不同！

日頻 ──── 收盤價、成交量、外資買賣超
月頻 ──── 月營收（每月 10 號公布上月）
季頻 ──── ROE、EPS（財報公布後才有）

         1/1  1/10  1/15  2/1  2/10  2/15  3/1
收盤價    ✓     ✓     ✓    ✓    ✓     ✓    ✓     ← 每天都有
月營收    ×     ✓12月  ×    ×    ✓1月   ×    ×     ← 每月才更新
ROE      ×     ×     ×    ×    ×     ×    ×     ← 季報才更新

FinLab 的解法：自動前向填充 (Forward Fill, ffill)
月營收在 1/10 公布後，1/11~2/9 都沿用這個值
→ 這就是 FinlabDataFrame 自動對齊的好處！

但要注意：
⚠️  前瞻偏差 (Look-ahead Bias)：
    月營收 1/10 才公布，你的模型不能在 1/5 就用到！
    FinLab 已經處理了這個問題，但自己處理數據時要小心。
```

#### Transformer 超參數建議（台股適用）

```
┌─────────────────────────────────────────────────────┐
│              推薦超參數配置                           │
│                                                     │
│  序列長度 (Sequence Length):                         │
│    日頻預測 → 60 天（約 3 個月的交易日）              │
│    月頻選股 → 12 個月                                │
│                                                     │
│  模型大小:                                           │
│    d_model = 32~64    （台股樣本少，別太大）          │
│    nhead = 4          （注意力頭數）                  │
│    num_layers = 1~2   （層數少 = 不容易過擬合）       │
│    dropout = 0.1~0.3  （台股數據少，dropout 要高）    │
│                                                     │
│  訓練:                                               │
│    batch_size = 32                                   │
│    lr = 1e-3 ~ 1e-4                                 │
│    早停 (Early Stopping) = 必須用！                  │
│    驗證集 = 用時間切割，不能隨機切！                   │
│                                                     │
│  ⚠️ 台股 vs 美股的差異：                             │
│    台股：~1700 檔，成交量集中在大型股                  │
│    美股：~5000 檔，數據更豐富                         │
│    → 台股用更小的模型 + 更強的正則化                   │
└─────────────────────────────────────────────────────┘
```

#### 訓練/驗證/測試集的正確切法

```
                    ❌ 錯誤切法（隨機切割）
    ┌──┬──┬──┬──┬──┬──┬──┬──┬──┬──┐
    │訓│測│訓│驗│訓│測│訓│驗│訓│測│  ← 未來數據混入訓練集！
    └──┴──┴──┴──┴──┴──┴──┴──┴──┴──┘

                    ✅ 正確切法（時間序列切割）
    ┌──────────────┬────────┬──────┐
    │   訓練集      │ 驗證集  │測試集│
    │  2015~2020   │ 2021   │ 2022│
    └──────────────┴────────┴──────┘

                    ✅✅ 更好的切法（Walk-Forward Validation, 滾動驗證）

    第1輪: ├─訓練 2015~2018─┤驗證 2019┤
    第2輪: ├─訓練 2015~2019──┤驗證 2020┤
    第3輪: ├─訓練 2015~2020───┤驗證 2021┤
    第4輪: ├─訓練 2015~2021────┤驗證 2022┤
           最終用所有驗證結果的平均來評估模型
```

**專業用詞：**
- **Walk-Forward Validation**（滾動前進驗證）：模擬真實交易場景的驗證方式
- **Look-ahead Bias**（前瞻偏差）：不小心用到未來資訊，導致回測績效虛高
- **Survivorship Bias**（倖存者偏差）：只用現在還在的股票訓練，忽略已下市的股票
- **Feature Leakage**（特徵洩漏）：標籤資訊不小心混進特徵中

---

### 三種場景的比較

| 面向 | 場景 A：預測股價 | 場景 B：多因子選股 | 場景 C：情緒分析 |
|------|-----------------|-------------------|-----------------|
| FinLab 角色 | 取 OHLCV + 回測 | 取多維因子 + 回測 | 取量化數據做融合 |
| Transformer 輸入 | 時間序列 (60天×特徵) | 橫截面 (全部股票×因子) | 文本 + 數據 |
| 輸出 | 預測報酬率 | 股票評分/排名 | 情緒分數 |
| 換股頻率 | 日頻/週頻 | 月頻 | 事件驅動 |
| 難度 | 中 | 中高 | 高（需 NLP） |
| 推薦先做 | ★★★ 最容易入門 | ★★ 最適合 FinLab 生態 | ★ 進階玩法 |

---

## 延伸閱讀方向

| 方向 | 說明 | 關鍵字搜尋 |
|------|------|-----------|
| 從頭訓練預測模型 | 用 PyTorch 建一個簡單的 Transformer 預測股價 | `Temporal Fusion Transformer`, `TFT stock` |
| 用現成框架回測 | 用 GA 或 ML 產生策略後回測 | `Backtrader`, `Zipline`, `FinRL` |
| 論文入門 | 了解學術界怎麼做 | `Transformer for financial time series` |
| 實作 RL 交易 | 端對端強化學習交易 | `FinRL`, `Stable-Baselines3` |
