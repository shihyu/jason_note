# RNN/LSTM 完整指南 - 用生活比喻理解

## 🎯 核心比喻：看電影 vs 看照片

### 問題：CNN 不會「記憶」

```
CNN 看圖片：
看照片 1：「這是貓」
看照片 2：「這是狗」
看照片 3：「這是鳥」

問題：每張照片都是獨立的，不記得之前看過什麼
```

### RNN：有記憶的神經網路

```
RNN 看電影：
第 1 幕：男主角出場（記住：有個男主角）
第 2 幕：女主角出場（記住：男主角 + 女主角）
第 3 幕：兩人相遇（記住：他們認識了）
第 4 幕：發生衝突（理解：因為之前的劇情）

→ RNN 能「記住」之前的內容，理解上下文！
```

---

## 📖 生活化案例 1：閱讀故事

### 情境：理解句子

```
句子：「我去銀行存錢」

CNN 的理解方式：
看到「銀行」→ 可能是金融機構？可能是河岸？
→ 無法判斷

RNN 的理解方式：
「我」→ 記住：主角
「去」→ 記住：主角要移動
「銀行」→ 結合前文：應該是金融機構
「存錢」→ 確認：是金融機構！
```

### RNN 的工作方式

**比喻**：接力賽

```
第 1 棒：處理「我」→ 交棒給第 2 棒（傳遞記憶）
第 2 棒：處理「去」→ 交棒給第 3 棒（累積記憶）
第 3 棒：處理「銀行」→ 交棒給第 4 棒
第 4 棒：處理「存錢」→ 完成！

每一棒都：
1. 接收前一棒的「記憶」
2. 處理當前輸入
3. 更新記憶
4. 傳給下一棒
```

---

## 🔄 RNN 架構詳解

### 展開圖：時間序列

```
普通神經網路：
輸入 → 隱藏層 → 輸出

RNN（展開）：
時間 t=1:  x₁ → [RNN] → h₁ → y₁
                   ↓
時間 t=2:  x₂ → [RNN] → h₂ → y₂
                   ↓
時間 t=3:  x₃ → [RNN] → h₃ → y₃
                   ↓
              (記憶傳遞)
```

**生活化解釋**：看連續劇

```
第 1 集：看完，記住劇情 → 記憶 h₁
第 2 集：根據 h₁ + 新劇情 → 更新記憶 h₂
第 3 集：根據 h₂ + 新劇情 → 更新記憶 h₃
...
```

### 數學表達

```
h_t = tanh(W_hh × h_{t-1} + W_xh × x_t + b_h)
       ↑     ↑             ↑
       激活   前一時刻記憶   當前輸入

y_t = W_hy × h_t + b_y
```

**生活化解釋**：
- `h_{t-1}`：昨天的日記（前一天的記憶）
- `x_t`：今天發生的事（當前輸入）
- `h_t`：今天的日記（更新後的記憶）
- `y_t`：今天的心情（輸出）

---

## 💻 從零實作：簡單 RNN

### 範例：預測下一個字母

```python
import numpy as np

class SimpleRNN:
    def __init__(self, input_size, hidden_size, output_size):
        """
        簡單 RNN

        比喻：記住故事情節的說書人

        參數：
            input_size: 輸入維度（如：26 個字母）
            hidden_size: 記憶容量（隱藏層大小）
            output_size: 輸出維度（預測下一個字母）
        """
        # 權重初始化
        self.W_xh = np.random.randn(input_size, hidden_size) * 0.01
        self.W_hh = np.random.randn(hidden_size, hidden_size) * 0.01
        self.W_hy = np.random.randn(hidden_size, output_size) * 0.01

        self.b_h = np.zeros(hidden_size)
        self.b_y = np.zeros(output_size)

        self.hidden_size = hidden_size

    def tanh(self, x):
        """激活函數"""
        return np.tanh(x)

    def softmax(self, x):
        """轉換成機率分佈"""
        exp_x = np.exp(x - np.max(x))
        return exp_x / np.sum(exp_x)

    def forward(self, inputs, h_prev=None):
        """
        前向傳播：處理序列

        比喻：逐字閱讀故事，記住情節

        參數：
            inputs: 輸入序列（如：['h', 'e', 'l', 'l', 'o']）
            h_prev: 前一時刻的記憶（初始為 0）

        返回：
            outputs: 每個時刻的預測
            h_last: 最後的記憶狀態
        """
        # 初始化記憶
        if h_prev is None:
            h_prev = np.zeros(self.hidden_size)

        outputs = []
        h = h_prev

        # 逐個處理輸入
        for x_t in inputs:
            # 更新記憶（結合舊記憶 + 新輸入）
            h = self.tanh(
                self.W_xh.T.dot(x_t) +
                self.W_hh.T.dot(h) +
                self.b_h
            )

            # 產生輸出
            y_t = self.W_hy.T.dot(h) + self.b_y
            y_t = self.softmax(y_t)

            outputs.append(y_t)

        return outputs, h

    def predict_next(self, sequence):
        """
        預測下一個字母

        比喻：
        輸入：「hell」
        輸出：「o」（因為通常是 hello）
        """
        outputs, _ = self.forward(sequence)
        last_output = outputs[-1]
        return np.argmax(last_output)


# 測試：學習「hello」模式
def train_hello_rnn():
    """訓練 RNN 學習 'hello' 序列"""

    # 字母表
    chars = 'helo'
    char_to_idx = {ch: i for i, ch in enumerate(chars)}
    idx_to_char = {i: ch for i, ch in enumerate(chars)}

    # 將 'hello' 轉換成 one-hot 編碼
    def char_to_onehot(ch):
        vec = np.zeros(len(chars))
        vec[char_to_idx[ch]] = 1
        return vec

    # 訓練數據：hell → o
    train_input = [char_to_onehot(ch) for ch in 'hell']
    train_target = char_to_idx['o']

    # 創建 RNN
    rnn = SimpleRNN(input_size=4, hidden_size=8, output_size=4)

    # 簡單訓練（只是演示，實際需要反向傳播）
    print("訓練前預測:")
    outputs, _ = rnn.forward(train_input)
    predicted = np.argmax(outputs[-1])
    print(f"輸入: 'hell', 預測: '{idx_to_char[predicted]}'")

    # 訓練後（省略訓練過程）
    print("\n理想情況（訓練後）:")
    print("輸入: 'hell', 預測: 'o' ✓")

train_hello_rnn()
```

---

## ⚠️ RNN 的問題：短期記憶

### 比喻：金魚記憶

```
問題：看長篇小說

第 1 章：記住主角叫「小明」
第 2 章：記住主角遇到「小花」
...
第 50 章：忘記主角叫什麼了！

→ RNN 的「記憶」會衰退
→ 遠距離的信息會被「遺忘」
```

### 技術術語：梯度消失

**比喻**：電話傳話遊戲

```
第 1 人說：「明天早上 8 點在咖啡廳見面」
第 2 人聽到 90%：「明天早上...咖啡廳...」
第 3 人聽到 80%：「明天...咖啡...」
...
第 10 人聽到 10%：「明...」（信息幾乎消失）

RNN 中的梯度也是這樣：
時間步 1 → 步 2 → 步 3 → ... → 步 50
梯度：   1.0 → 0.9 → 0.8 → ... → 0.001
                                  ↑ 幾乎消失
```

---

## 🧠 LSTM：長短期記憶網路

### 核心改進：加入「記事本」

**比喻**：人類的記憶系統

```
RNN = 工作記憶（短期）
「剛剛看到什麼？」
→ 只能記住最近幾秒

LSTM = 工作記憶 + 長期記憶
「重要的事寫到筆記本（Cell State）」
「不重要的事忘掉」
→ 可以記住很久以前的事
```

### LSTM 的三個門：守門員

想像一個圖書館的記憶管理系統：

```
1. 遺忘門（Forget Gate）：
   「這本舊書還需要嗎？」
   → 決定忘記哪些舊記憶

2. 輸入門（Input Gate）：
   「這本新書重要嗎？要收藏嗎？」
   → 決定記住哪些新信息

3. 輸出門（Output Gate）：
   「現在需要哪些資訊？」
   → 決定輸出什麼
```

### 生活化例子：追劇記憶

```
情境：你在追一部 100 集的連續劇

第 1 集：
- 男主角出場（重要！記到「長期記憶」）✓
- 路人甲走過（不重要，忘掉）✗

第 50 集：
- 遺忘門：「還記得男主角嗎？」（需要！保留）
- 輸入門：「女配角黑化了」（重要！記住）
- 輸出門：「現在需要什麼資訊？」（輸出：男主角 + 女配角黑化）

第 100 集：
- 依然記得第 1 集的男主角！（長期記憶）✓
```

---

## 🏗️ LSTM 架構詳解

### 數學表達（用生活化解釋）

```python
# 1. 遺忘門：決定忘記多少舊記憶
f_t = sigmoid(W_f × [h_{t-1}, x_t] + b_f)
      ↑
      0 = 完全忘記，1 = 完全保留

比喻：
「昨天的筆記還需要嗎？」
- 如果是重要事件 → f_t ≈ 1（保留）
- 如果是無關緊要 → f_t ≈ 0（忘記）


# 2. 輸入門：決定記住多少新信息
i_t = sigmoid(W_i × [h_{t-1}, x_t] + b_i)
C̃_t = tanh(W_C × [h_{t-1}, x_t] + b_C)

比喻：
「今天的新聞要記嗎？」
- 如果重要 → i_t ≈ 1（記住）
- 如果不重要 → i_t ≈ 0（忽略）


# 3. 更新長期記憶（Cell State）
C_t = f_t * C_{t-1} + i_t * C̃_t
      ↑              ↑
      保留的舊記憶    加入的新記憶

比喻：
新筆記 = (保留的舊筆記) + (新寫的內容)


# 4. 輸出門：決定輸出什麼
o_t = sigmoid(W_o × [h_{t-1}, x_t] + b_o)
h_t = o_t * tanh(C_t)

比喻：
「現在需要回憶什麼？」
從筆記本中提取需要的資訊
```

### 視覺化：LSTM 單元

```
         ┌──────────────────────────────┐
         │      Cell State (C_t)       │  ← 長期記憶（筆記本）
         │    ╔════════════════╗        │
x_t ───→ │    ║  遺忘門  輸入門 ║ ───→  │ ───→ h_t
h_{t-1}→ │    ║   ↓      ↓    ║        │     (輸出)
         │    ║   忘記？ 記住？ ║        │
         │    ║      ↓          ║        │
         │    ║    輸出門        ║        │
         │    ╚════════════════╝        │
         └──────────────────────────────┘
```

---

## 💻 完整實作：LSTM

```python
class LSTM:
    def __init__(self, input_size, hidden_size, output_size):
        """
        LSTM 網路

        比喻：有筆記本的說書人（可以記住很久以前的事）

        參數：
            input_size: 輸入維度
            hidden_size: 隱藏層/記憶容量
            output_size: 輸出維度
        """
        # 遺忘門參數
        self.W_f = np.random.randn(input_size + hidden_size, hidden_size) * 0.01
        self.b_f = np.zeros(hidden_size)

        # 輸入門參數
        self.W_i = np.random.randn(input_size + hidden_size, hidden_size) * 0.01
        self.b_i = np.zeros(hidden_size)

        self.W_C = np.random.randn(input_size + hidden_size, hidden_size) * 0.01
        self.b_C = np.zeros(hidden_size)

        # 輸出門參數
        self.W_o = np.random.randn(input_size + hidden_size, hidden_size) * 0.01
        self.b_o = np.zeros(hidden_size)

        # 輸出層參數
        self.W_y = np.random.randn(hidden_size, output_size) * 0.01
        self.b_y = np.zeros(output_size)

        self.hidden_size = hidden_size

    def sigmoid(self, x):
        """Sigmoid：輸出 0-1 之間（門控信號）"""
        return 1 / (1 + np.exp(-np.clip(x, -500, 500)))

    def tanh(self, x):
        """tanh：輸出 -1 到 1"""
        return np.tanh(x)

    def forward_step(self, x_t, h_prev, C_prev):
        """
        單個時間步的前向傳播

        比喻：處理當前時刻的輸入，更新記憶

        參數：
            x_t: 當前輸入（今天的新聞）
            h_prev: 前一時刻的輸出（工作記憶）
            C_prev: 前一時刻的 Cell State（長期記憶/筆記本）

        返回：
            h_t: 當前輸出
            C_t: 更新後的 Cell State
        """
        # 拼接輸入
        concat = np.concatenate([h_prev, x_t])

        # 1. 遺忘門：「要忘記多少舊記憶？」
        f_t = self.sigmoid(concat.dot(self.W_f) + self.b_f)

        # 2. 輸入門：「要記住多少新信息？」
        i_t = self.sigmoid(concat.dot(self.W_i) + self.b_i)
        C_tilde = self.tanh(concat.dot(self.W_C) + self.b_C)

        # 3. 更新 Cell State（長期記憶）
        C_t = f_t * C_prev + i_t * C_tilde
        #     ↑             ↑
        #     保留的舊記憶   新記憶

        # 4. 輸出門：「要輸出什麼？」
        o_t = self.sigmoid(concat.dot(self.W_o) + self.b_o)
        h_t = o_t * self.tanh(C_t)

        return h_t, C_t

    def forward(self, inputs, h_init=None, C_init=None):
        """
        處理整個序列

        比喻：從頭到尾看完一部小說
        """
        # 初始化
        if h_init is None:
            h_init = np.zeros(self.hidden_size)
        if C_init is None:
            C_init = np.zeros(self.hidden_size)

        h = h_init
        C = C_init
        outputs = []

        # 逐步處理
        for x_t in inputs:
            h, C = self.forward_step(x_t, h, C)

            # 計算輸出
            y_t = h.dot(self.W_y) + self.b_y
            outputs.append(y_t)

        return outputs, h, C


# 測試：文本生成
def test_lstm_text_generation():
    """
    測試 LSTM 生成文本

    比喻：訓練 AI 寫詩
    """
    # 簡單例子：學習 "hello" 序列
    vocab = ['h', 'e', 'l', 'o']
    char_to_idx = {ch: i for i, ch in enumerate(vocab)}
    idx_to_char = {i: ch for i, ch in enumerate(vocab)}

    # One-hot 編碼
    def char_to_vec(ch):
        vec = np.zeros(len(vocab))
        vec[char_to_idx[ch]] = 1
        return vec

    # 訓練序列："hell" → "o"
    train_input = [char_to_vec(ch) for ch in "hell"]

    # 創建 LSTM
    lstm = LSTM(input_size=4, hidden_size=16, output_size=4)

    print("LSTM 預測測試：")
    outputs, _, _ = lstm.forward(train_input)

    print("輸入序列: 'hell'")
    print("LSTM 的記憶變化:")
    for i, output in enumerate(outputs):
        predicted_idx = np.argmax(output)
        print(f"  步驟 {i+1}: 看到 '{['h','e','l','l'][i]}' → "
              f"預測下一個可能是 '{idx_to_char[predicted_idx]}'")

test_lstm_text_generation()
```

---

## 🎯 實戰案例

### 案例 1：情感分析

```python
"""
任務：判斷電影評論是正面還是負面

範例：
輸入：「這部電影太棒了，演員演技精湛！」
輸出：正面（95% 信心）

輸入：「浪費時間，劇情無聊透頂。」
輸出：負面（92% 信心）
"""

class SentimentLSTM:
    def __init__(self, vocab_size, embedding_dim=128, hidden_size=64):
        """情感分析 LSTM"""
        # 詞嵌入層（把單詞轉成向量）
        self.embedding = np.random.randn(vocab_size, embedding_dim) * 0.01

        # LSTM 層
        self.lstm = LSTM(
            input_size=embedding_dim,
            hidden_size=hidden_size,
            output_size=2  # 2 類：正面/負面
        )

    def predict_sentiment(self, word_indices):
        """
        預測情感

        比喻：
        1. 逐字閱讀評論
        2. 理解整體情緒
        3. 判斷正負面
        """
        # 1. 將單詞轉成向量
        word_vectors = [self.embedding[idx] for idx in word_indices]

        # 2. LSTM 處理序列
        outputs, _, _ = self.lstm.forward(word_vectors)

        # 3. 使用最後的輸出做分類
        final_output = outputs[-1]
        sentiment = "正面" if final_output[0] > final_output[1] else "負面"
        confidence = max(final_output) / sum(final_output) * 100

        return sentiment, confidence

# 使用範例
vocab_size = 10000  # 假設詞彙表有 10000 個詞
model = SentimentLSTM(vocab_size)

# 假設這是「這部電影太棒了」的詞索引
review = [1523, 982, 3421, 567, 8901]
sentiment, confidence = model.predict_sentiment(review)
print(f"情感: {sentiment} ({confidence:.1f}% 信心)")
```

### 案例 2：機器翻譯

```python
"""
任務：英文翻譯成中文

範例：
輸入：「I love you」
輸出：「我愛你」

架構：編碼器-解碼器（Encoder-Decoder）
"""

class TranslationModel:
    def __init__(self):
        """翻譯模型"""
        # 編碼器 LSTM（理解英文）
        self.encoder = LSTM(input_size=100, hidden_size=256, output_size=256)

        # 解碼器 LSTM（生成中文）
        self.decoder = LSTM(input_size=100, hidden_size=256, output_size=5000)

    def translate(self, english_sentence):
        """
        翻譯流程

        比喻：
        1. 編碼器：理解英文句子的「意思」
        2. 解碼器：用中文表達這個「意思」
        """
        # 1. 編碼：理解英文
        _, h_enc, C_enc = self.encoder.forward(english_sentence)
        # h_enc, C_enc：英文句子的「意思」壓縮在這裡

        # 2. 解碼：生成中文
        # 從 <START> 標記開始
        decoder_input = [self.start_token]
        h_dec, C_dec = h_enc, C_enc  # 繼承編碼器的記憶

        chinese_words = []
        for _ in range(50):  # 最多生成 50 個詞
            outputs, h_dec, C_dec = self.decoder.forward(
                decoder_input, h_dec, C_dec
            )

            # 預測下一個中文詞
            next_word_idx = np.argmax(outputs[-1])

            if next_word_idx == self.end_token:
                break  # 遇到 <END> 標記

            chinese_words.append(next_word_idx)
            decoder_input = [self.idx_to_vec(next_word_idx)]

        return chinese_words

# 比喻總結：
# 編碼器 = 懂英文的人，把意思記在腦中
# 解碼器 = 懂中文的人，把腦中的意思用中文說出來
```

### 案例 3：股票價格預測

```python
"""
任務：根據過去 30 天的股價，預測明天的價格

輸入：[100, 102, 101, 105, 103, ..., 120]（30 天股價）
輸出：122（預測明天價格）
"""

class StockPredictionLSTM:
    def __init__(self):
        """股價預測 LSTM"""
        self.lstm = LSTM(
            input_size=1,      # 每天只有一個數字（收盤價）
            hidden_size=64,
            output_size=1      # 預測一個數字（明天價格）
        )

    def predict_next_day(self, price_history):
        """
        預測明天股價

        比喻：
        LSTM 記住「股價趨勢」
        - 最近在上漲？（看漲）
        - 最近在下跌？（看跌）
        - 有週期性波動？（考慮週期）
        """
        # 標準化（轉換成 0-1 範圍）
        min_price = min(price_history)
        max_price = max(price_history)
        normalized = [(p - min_price) / (max_price - min_price)
                      for p in price_history]

        # 轉換成 LSTM 輸入格式
        inputs = [np.array([p]) for p in normalized]

        # LSTM 預測
        outputs, _, _ = self.lstm.forward(inputs)
        normalized_pred = outputs[-1][0]

        # 反標準化
        predicted_price = normalized_pred * (max_price - min_price) + min_price

        return predicted_price

# 使用
model = StockPredictionLSTM()
past_30_days = [100, 102, 101, 105, 103, 107, 110, ...]  # 30 個價格
tomorrow_price = model.predict_next_day(past_30_days)
print(f"預測明天股價: ${tomorrow_price:.2f}")
```

---

## 🚀 進階變體

### 1. GRU（Gated Recurrent Unit）

**比喻**：LSTM 的簡化版

```
LSTM：3 個門（遺忘、輸入、輸出）
GRU：2 個門（重置、更新）

優點：
- 參數更少（訓練更快）
- 效果相近

適用：
- 數據量不大時
- 需要快速訓練時
```

### 2. 雙向 LSTM（Bidirectional LSTM）

**比喻**：前後文都看

```
普通 LSTM：從左到右閱讀
「我愛___」→ 預測「你」

雙向 LSTM：同時從左到右、從右到左
「我愛___，你也愛我」
→ 同時看前文和後文
→ 預測更準確
```

**使用場景**：
- 文本分類（需要看完整句子）
- 命名實體識別
- 機器翻譯（編碼器部分）

### 3. 多層 LSTM（Stacked LSTM）

**比喻**：多級理解

```
第 1 層 LSTM：理解「單詞」
第 2 層 LSTM：理解「短語」
第 3 層 LSTM：理解「句子」
第 4 層 LSTM：理解「段落」

就像人類閱讀：
字 → 詞 → 句 → 段 → 文章主題
```

---

## 📊 RNN vs LSTM vs GRU 比較

| 特性 | RNN | LSTM | GRU |
|------|-----|------|-----|
| **記憶能力** | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **訓練速度** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| **參數數量** | 少 | 多 | 中 |
| **梯度消失** | 嚴重 | 解決 | 解決 |
| **適用序列長度** | 短（<10） | 長（100+） | 中長（50+） |

**選擇建議**：
- 🥇 **首選**：LSTM（長序列、重要任務）
- 🥈 **備選**：GRU（中等序列、快速原型）
- 🥉 **教學**：RNN（理解原理）

---

## 🎓 實務技巧

### 1. 序列填充（Padding）

**問題**：序列長度不一

```
句子 1：「我愛你」（3 個詞）
句子 2：「這部電影真的非常精彩」（7 個詞）

→ 無法批次處理
```

**解決**：填充到相同長度

```python
def pad_sequences(sequences, max_len=None):
    """
    填充序列

    比喻：排隊時補空位

    輸入：
    [[1, 2, 3],           # 短句子
     [4, 5, 6, 7, 8, 9]]  # 長句子

    輸出（填充到 6）：
    [[1, 2, 3, 0, 0, 0],  # 補 0
     [4, 5, 6, 7, 8, 9]]
    """
    if max_len is None:
        max_len = max(len(seq) for seq in sequences)

    padded = []
    for seq in sequences:
        if len(seq) < max_len:
            # 填充 0
            seq = seq + [0] * (max_len - len(seq))
        else:
            # 截斷
            seq = seq[:max_len]
        padded.append(seq)

    return np.array(padded)
```

### 2. 梯度裁剪（Gradient Clipping）

**問題**：梯度爆炸

```python
def clip_gradients(gradients, max_norm=5.0):
    """
    裁剪梯度

    比喻：限速（避免開太快）

    如果梯度太大（>5.0），就縮小到 5.0
    """
    total_norm = np.sqrt(sum(np.sum(g**2) for g in gradients))

    if total_norm > max_norm:
        scale = max_norm / total_norm
        gradients = [g * scale for g in gradients]

    return gradients
```

### 3. 注意力機制（Attention）

**問題**：長序列資訊壓縮損失

```
翻譯長句子：
「今天天氣很好，我和朋友去了公園，看到很多人在放風箏」

編碼器：把 18 個詞壓縮成一個向量
→ 資訊損失！
```

**解決**：注意力機制

```
解碼器生成每個詞時，動態「注意」編碼器不同位置

翻譯「天氣」時 → 注意「今天天氣很好」
翻譯「公園」時 → 注意「去了公園」
翻譯「風箏」時 → 注意「放風箏」

→ 不損失資訊！
```

---

## 🔗 總結

### RNN 家族的演進

```
1986: RNN（基礎）
   ↓ 問題：梯度消失
1997: LSTM（長期記憶）★ 重大突破
   ↓ 改進：簡化結構
2014: GRU（簡化版 LSTM）
   ↓ 加強：雙向理解
2015: Bidirectional LSTM
   ↓ 革命：注意力機制
2017: Transformer（取代 RNN）→ 下一章節
```

### 核心思想

1. **RNN**：有記憶的神經網路
2. **LSTM**：用「門」控制記憶（長期記憶）
3. **GRU**：簡化版 LSTM（更快）

### 適用場景

- ✅ **文本處理**：情感分析、機器翻譯
- ✅ **時間序列**：股票預測、天氣預測
- ✅ **語音識別**：語音轉文字
- ✅ **視頻分析**：動作識別

### 下一步學習

- **Transformer**：取代 RNN 的新架構（GPT、BERT 的基礎）
- **注意力機制**：讓模型「專注」重點
- **Sequence-to-Sequence**：編碼器-解碼器架構

---

*最後更新: 2025-11-26*
