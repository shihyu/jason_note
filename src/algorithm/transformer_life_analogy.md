# Transformer 完整指南 - 用生活比喻理解

## 🎯 核心比喻：圖書館 vs 閱讀小說

### RNN/LSTM 的問題：必須按順序讀

```
RNN/LSTM 看小說：
第 1 頁 → 第 2 頁 → 第 3 頁 → ... → 第 100 頁
        ↓         ↓         ↓
      記憶1     記憶2     記憶3

問題：
❌ 必須按順序讀（無法跳頁）
❌ 讀完第 1 頁才能讀第 2 頁（無法並行）
❌ 第 1 頁的資訊可能被遺忘（梯度消失）
```

### Transformer：可以同時看所有頁面

```
Transformer 看小說：
┌─────┬─────┬─────┬─────┐
│第1頁│第2頁│第3頁│...  │  同時看
└─────┴─────┴─────┴─────┘
   ↓     ↓     ↓     ↓
   └─────┼─────┼─────┘
         ↓
    「注意力機制」
    自動找出重要關聯

優點：
✅ 並行處理（GPU 友好，超快）
✅ 長距離依賴不衰減（第 1 頁和第 100 頁同樣清晰）
✅ 自動找出關聯（不需要人工設計）
```

---

## 📚 生活化案例 1：搜尋引擎

### 比喻：Google 搜尋

```
你在 Google 搜尋：「2024 奧運 金牌」

傳統方法（RNN）：
逐字處理 → 「2024」→「奧運」→「金牌」
→ 慢，而且可能忘記「2024」

Transformer 方法：
1. 同時看三個詞
2. 自動理解「2024」修飾「奧運」
3. 「金牌」是查詢重點
4. 快速找到最相關的結果

這就是「注意力機制」！
```

### 注意力機制：關聯性計算

**情境**：理解句子「The animal didn't cross the street because it was too tired」

```
問題：「it」指的是什麼？

Transformer 的做法：
1. 計算「it」和每個詞的「關聯分數」

   it ←→ The      : 0.02（低）
   it ←→ animal   : 0.87（高！）
   it ←→ didn't   : 0.01
   it ←→ cross    : 0.03
   it ←→ street   : 0.15
   it ←→ because  : 0.05
   it ←→ was      : 0.08
   it ←→ too      : 0.04
   it ←→ tired    : 0.45（高）

2. 結論：「it」最相關的是「animal」
   → it = animal（動物太累了）
```

---

## 🔍 注意力機制詳解

### 核心概念：Query、Key、Value

**比喻**：YouTube 推薦系統

```
你（Query）：「我想看有趣的貓咪影片」
    ↓ 比對
YouTube 影片庫（Keys）：
- 影片 1（Key）：「貓咪跳舞」     → 相關度 0.95（高！）
- 影片 2（Key）：「狗狗玩球」     → 相關度 0.30
- 影片 3（Key）：「貓咪睡覺」     → 相關度 0.88（高）
- 影片 4（Key）：「新聞報導」     → 相關度 0.02

推薦給你（Values）：
主要推薦影片 1（貓咪跳舞）
次要推薦影片 3（貓咪睡覺）

這就是「注意力」：
Query（需求） × Keys（候選） → 找出最相關的 Values
```

### 數學表達（生活化）

```python
# 1. 計算相似度分數
scores = Query × Keys^T
         ↑
    「我想看貓咪」和「影片標題」的相似度

# 2. 歸一化（轉成機率）
attention_weights = softmax(scores / √d_k)
                           ↑
                    除以 √d_k 避免分數過大

# 3. 加權平均
output = attention_weights × Values
         ↑
    根據相關度，組合影片內容
```

### 視覺化

```
     Query              Keys               Values
    「我想看貓」         「標題」            「影片內容」
        │                │                    │
        └────×───────────┘                    │
             │                                │
             ↓                                │
        [0.95, 0.30, 0.88, 0.02]              │
             │ (相關度)                        │
             │                                │
             └────────────×──────────────────┘
                          ↓
                    推薦結果（加權組合）
```

---

## 🏗️ Transformer 完整架構

### 整體結構：編碼器-解碼器

```
輸入句子（英文）          輸出句子（中文）
    ↓                          ↑
┌─────────┐              ┌─────────┐
│ 編碼器  │─────────────→│ 解碼器  │
│(Encoder)│  (傳遞語義)   │(Decoder)│
└─────────┘              └─────────┘
理解輸入                  生成輸出
```

### 編碼器（Encoder）：理解輸入

**比喻**：閱讀理解專家

```
輸入：「I love you」

編碼器做的事：
1. 詞嵌入（Word Embedding）
   I → [0.2, 0.5, 0.1, ...]
   love → [0.8, 0.3, 0.9, ...]
   you → [0.1, 0.7, 0.4, ...]

2. 位置編碼（Positional Encoding）
   加上「位置資訊」
   I（位置1） love（位置2） you（位置3）

3. 多頭自注意力（Multi-Head Self-Attention）
   「I」看向所有詞 → 理解「我是主語」
   「love」看向所有詞 → 理解「愛是動詞」
   「you」看向所有詞 → 理解「你是賓語」

4. 前饋網路（Feed-Forward）
   進一步處理資訊

5. 重複 N 次（通常 6 層）
   每層理解更深入

輸出：句子的「深度理解」（向量表示）
```

### 解碼器（Decoder）：生成輸出

**比喻**：寫作專家

```
任務：把「I love you」翻譯成中文

解碼器做的事：
1. 接收編碼器的「理解」

2. 生成第 1 個字：
   看到「<START>」
   + 編碼器的理解
   → 預測：「我」（90% 信心）

3. 生成第 2 個字：
   看到「<START> 我」
   + 編碼器的理解
   → 預測：「愛」（85% 信心）

4. 生成第 3 個字：
   看到「<START> 我 愛」
   + 編碼器的理解
   → 預測：「你」（92% 信心）

5. 生成結束標記：
   看到「<START> 我 愛 你」
   → 預測：「<END>」

最終輸出：「我愛你」
```

---

## 💻 核心組件實作

### 1. 自注意力機制（Self-Attention）

```python
import numpy as np

class SelfAttention:
    def __init__(self, d_model):
        """
        自注意力機制

        比喻：讓句子中的每個詞互相「看」對方

        參數：
            d_model: 向量維度
        """
        self.d_model = d_model

        # Query、Key、Value 的轉換矩陣
        self.W_q = np.random.randn(d_model, d_model) * 0.01
        self.W_k = np.random.randn(d_model, d_model) * 0.01
        self.W_v = np.random.randn(d_model, d_model) * 0.01

    def softmax(self, x):
        """Softmax"""
        exp_x = np.exp(x - np.max(x, axis=-1, keepdims=True))
        return exp_x / np.sum(exp_x, axis=-1, keepdims=True)

    def forward(self, X):
        """
        前向傳播

        比喻：
        X = 句子中的所有詞向量
        每個詞都要「看」其他所有詞

        參數：
            X: 輸入序列 (seq_len, d_model)

        返回：
            output: 加入注意力後的表示
        """
        # 1. 計算 Query、Key、Value
        Q = X.dot(self.W_q)  # (seq_len, d_model)
        K = X.dot(self.W_k)  # (seq_len, d_model)
        V = X.dot(self.W_v)  # (seq_len, d_model)

        # 2. 計算注意力分數
        # Q × K^T：每個詞和其他詞的相關度
        scores = Q.dot(K.T)  # (seq_len, seq_len)

        # 3. 縮放（避免梯度消失）
        scores = scores / np.sqrt(self.d_model)

        # 4. Softmax（轉成機率分佈）
        attention_weights = self.softmax(scores)  # (seq_len, seq_len)

        # 5. 加權平均 Values
        output = attention_weights.dot(V)  # (seq_len, d_model)

        return output, attention_weights


# 測試
def test_self_attention():
    """測試自注意力"""

    # 假設句子：「I love you」（3 個詞）
    # 每個詞用 4 維向量表示
    sentence = np.array([
        [0.1, 0.2, 0.3, 0.4],  # I
        [0.5, 0.6, 0.7, 0.8],  # love
        [0.9, 1.0, 1.1, 1.2]   # you
    ])

    # 創建自注意力層
    attention = SelfAttention(d_model=4)

    # 計算注意力
    output, weights = attention.forward(sentence)

    print("注意力權重：")
    print("(每一行代表一個詞「看」其他詞的注意力)")
    print(weights)
    print("\n解釋：")
    print("第 1 行：'I' 對 [I, love, you] 的注意力")
    print("第 2 行：'love' 對 [I, love, you] 的注意力")
    print("第 3 行：'you' 對 [I, love, you] 的注意力")

test_self_attention()
```

**輸出範例**：
```
注意力權重：
[[0.33  0.34  0.33]   ← 'I' 的注意力分佈
 [0.32  0.35  0.33]   ← 'love' 的注意力分佈
 [0.31  0.34  0.35]]  ← 'you' 的注意力分佈

解釋：
'you' 對自己的注意力最高（0.35）
這表示在理解 'you' 時，它自身的資訊最重要
```

### 2. 多頭注意力（Multi-Head Attention）

**比喻**：多角度理解

```
單頭注意力（1 個專家）：
只從「語義相似度」角度理解

多頭注意力（8 個專家）：
專家 1：看「語義相似度」
專家 2：看「語法結構」（主謂賓）
專家 3：看「情感色彩」
專家 4：看「時態關係」
...
專家 8：看「其他特徵」

最後：綜合所有專家意見
```

```python
class MultiHeadAttention:
    def __init__(self, d_model, num_heads):
        """
        多頭注意力

        比喻：多個專家從不同角度理解

        參數：
            d_model: 模型維度（如 512）
            num_heads: 頭數（如 8）
        """
        self.num_heads = num_heads
        self.d_model = d_model

        # 每個頭的維度
        self.d_k = d_model // num_heads

        # 創建多個注意力頭
        self.heads = [SelfAttention(self.d_k) for _ in range(num_heads)]

        # 輸出投影
        self.W_o = np.random.randn(d_model, d_model) * 0.01

    def forward(self, X):
        """
        前向傳播

        比喻：
        1. 把輸入分給各個專家
        2. 每個專家獨立分析
        3. 綜合所有專家意見
        """
        # 1. 分割輸入給各個頭
        # (seq_len, d_model) → (seq_len, num_heads, d_k)
        seq_len = X.shape[0]
        X_split = X.reshape(seq_len, self.num_heads, self.d_k)

        # 2. 每個頭獨立計算注意力
        head_outputs = []
        for i, head in enumerate(self.heads):
            X_head = X_split[:, i, :]  # (seq_len, d_k)
            output, _ = head.forward(X_head)
            head_outputs.append(output)

        # 3. 拼接所有頭的輸出
        concat = np.concatenate(head_outputs, axis=-1)  # (seq_len, d_model)

        # 4. 線性投影
        output = concat.dot(self.W_o)

        return output

# 比喻總結：
# 單頭 = 1 個專家從 1 個角度看
# 多頭 = 8 個專家從 8 個角度看 → 理解更全面
```

### 3. 位置編碼（Positional Encoding）

**問題**：Transformer 無法區分順序

```
「我愛你」和「你愛我」
在 Transformer 中是「同一個」詞袋
→ 需要加入「位置資訊」
```

**解決**：位置編碼

```python
def positional_encoding(max_len, d_model):
    """
    位置編碼

    比喻：給每個位置一個「身份證」

    參數：
        max_len: 最大序列長度
        d_model: 模型維度

    返回：
        PE: 位置編碼矩陣 (max_len, d_model)
    """
    PE = np.zeros((max_len, d_model))

    for pos in range(max_len):
        for i in range(0, d_model, 2):
            # 使用正弦和餘弦函數
            PE[pos, i] = np.sin(pos / (10000 ** (i / d_model)))
            if i + 1 < d_model:
                PE[pos, i + 1] = np.cos(pos / (10000 ** (i / d_model)))

    return PE

# 使用
pos_enc = positional_encoding(max_len=100, d_model=512)

# 加到詞嵌入上
word_embedding = get_word_embedding("hello")  # (512,)
position = 5  # 第 5 個位置
final_embedding = word_embedding + pos_enc[position]

# 現在 Transformer 知道這個詞在第 5 個位置了！
```

**為什麼用正弦/餘弦？**

```
優點：
1. 值域固定（-1 到 1）
2. 可以處理任意長度的序列
3. 相對位置關係清晰
   （位置 5 和位置 6 的編碼很相似）
```

### 4. 前饋網路（Feed-Forward Network）

**比喻**：深度思考

```
注意力機制：「我看到了什麼」（觀察）
前饋網路：「這代表什麼意思」（思考）
```

```python
class FeedForward:
    def __init__(self, d_model, d_ff):
        """
        前饋網路

        比喻：深度思考層

        參數：
            d_model: 輸入輸出維度（如 512）
            d_ff: 隱藏層維度（如 2048，通常是 d_model 的 4 倍）
        """
        self.W1 = np.random.randn(d_model, d_ff) * 0.01
        self.b1 = np.zeros(d_ff)
        self.W2 = np.random.randn(d_ff, d_model) * 0.01
        self.b2 = np.zeros(d_model)

    def relu(self, x):
        """ReLU 激活函數"""
        return np.maximum(0, x)

    def forward(self, x):
        """
        前向傳播

        比喻：
        輸入 → 擴展思考（升維到 2048）→ 整合結論（降維回 512）
        """
        # 第一層：擴展
        hidden = self.relu(x.dot(self.W1) + self.b1)

        # 第二層：整合
        output = hidden.dot(self.W2) + self.b2

        return output
```

---

## 🎨 完整 Transformer 實作

### 編碼器層（Encoder Layer）

```python
class EncoderLayer:
    def __init__(self, d_model, num_heads, d_ff):
        """
        Transformer 編碼器層

        組件：
        1. 多頭自注意力
        2. 殘差連接 + 層標準化
        3. 前饋網路
        4. 殘差連接 + 層標準化
        """
        self.attention = MultiHeadAttention(d_model, num_heads)
        self.feed_forward = FeedForward(d_model, d_ff)

    def layer_norm(self, x):
        """層標準化"""
        mean = np.mean(x, axis=-1, keepdims=True)
        std = np.std(x, axis=-1, keepdims=True)
        return (x - mean) / (std + 1e-8)

    def forward(self, x):
        """
        前向傳播

        比喻：
        1. 自注意力：「看看句子中其他詞」
        2. 前饋網路：「深度思考」
        3. 殘差連接：「保留原始資訊」
        """
        # 1. 多頭自注意力
        attn_output = self.attention.forward(x)

        # 2. 殘差連接 + 層標準化
        x = self.layer_norm(x + attn_output)

        # 3. 前饋網路
        ff_output = self.feed_forward.forward(x)

        # 4. 殘差連接 + 層標準化
        x = self.layer_norm(x + ff_output)

        return x
```

### 解碼器層（Decoder Layer）

```python
class DecoderLayer:
    def __init__(self, d_model, num_heads, d_ff):
        """
        Transformer 解碼器層

        組件：
        1. 掩碼自注意力（Masked Self-Attention）
        2. 交叉注意力（Cross-Attention）
        3. 前饋網路
        """
        self.masked_attention = MultiHeadAttention(d_model, num_heads)
        self.cross_attention = MultiHeadAttention(d_model, num_heads)
        self.feed_forward = FeedForward(d_model, d_ff)

    def forward(self, x, encoder_output, mask=None):
        """
        前向傳播

        比喻：
        1. 看自己生成的內容（不能偷看未來）
        2. 看編碼器的理解（輸入句子的意思）
        3. 思考下一個詞
        """
        # 1. 掩碼自注意力（只能看「已生成」的部分）
        masked_attn = self.masked_attention.forward(x)
        x = x + masked_attn

        # 2. 交叉注意力（看編碼器的輸出）
        cross_attn = self.cross_attention.forward(encoder_output)
        x = x + cross_attn

        # 3. 前饋網路
        ff_output = self.feed_forward.forward(x)
        x = x + ff_output

        return x
```

### 完整 Transformer

```python
class Transformer:
    def __init__(self, src_vocab_size, tgt_vocab_size,
                 d_model=512, num_heads=8, num_layers=6, d_ff=2048):
        """
        完整 Transformer

        比喻：
        編碼器 = 閱讀理解專家（理解輸入）
        解碼器 = 寫作專家（生成輸出）

        參數：
            src_vocab_size: 源語言詞彙量（如英文 10000 詞）
            tgt_vocab_size: 目標語言詞彙量（如中文 5000 詞）
            d_model: 模型維度
            num_heads: 注意力頭數
            num_layers: 編碼器/解碼器層數
            d_ff: 前饋網路隱藏層維度
        """
        # 詞嵌入層
        self.src_embedding = np.random.randn(src_vocab_size, d_model) * 0.01
        self.tgt_embedding = np.random.randn(tgt_vocab_size, d_model) * 0.01

        # 位置編碼
        self.pos_encoding = positional_encoding(max_len=5000, d_model=d_model)

        # 編碼器（6 層）
        self.encoder_layers = [
            EncoderLayer(d_model, num_heads, d_ff)
            for _ in range(num_layers)
        ]

        # 解碼器（6 層）
        self.decoder_layers = [
            DecoderLayer(d_model, num_heads, d_ff)
            for _ in range(num_layers)
        ]

        # 輸出層
        self.output_layer = np.random.randn(d_model, tgt_vocab_size) * 0.01

    def encode(self, src_tokens):
        """
        編碼：理解輸入句子

        比喻：閱讀並理解英文句子
        """
        # 1. 詞嵌入
        x = self.src_embedding[src_tokens]

        # 2. 加上位置編碼
        x = x + self.pos_encoding[:len(src_tokens)]

        # 3. 通過編碼器層
        for layer in self.encoder_layers:
            x = layer.forward(x)

        return x

    def decode(self, tgt_tokens, encoder_output):
        """
        解碼：生成輸出句子

        比喻：根據英文理解，寫出中文
        """
        # 1. 詞嵌入
        x = self.tgt_embedding[tgt_tokens]

        # 2. 加上位置編碼
        x = x + self.pos_encoding[:len(tgt_tokens)]

        # 3. 通過解碼器層
        for layer in self.decoder_layers:
            x = layer.forward(x, encoder_output)

        # 4. 輸出層（預測下一個詞）
        logits = x.dot(self.output_layer)

        return logits

    def translate(self, src_sentence, max_len=50):
        """
        翻譯句子

        比喻：
        輸入英文 → 理解 → 生成中文
        """
        # 1. 編碼輸入
        encoder_output = self.encode(src_sentence)

        # 2. 逐步解碼生成
        tgt_tokens = [START_TOKEN]  # 從 <START> 開始

        for _ in range(max_len):
            # 解碼
            logits = self.decode(tgt_tokens, encoder_output)

            # 預測下一個詞
            next_token = np.argmax(logits[-1])

            # 如果是結束標記，停止
            if next_token == END_TOKEN:
                break

            tgt_tokens.append(next_token)

        return tgt_tokens[1:]  # 去掉 <START>

# 使用範例
transformer = Transformer(
    src_vocab_size=10000,  # 英文詞彙
    tgt_vocab_size=5000,   # 中文詞彙
)

# 翻譯「I love you」→「我愛你」
english = [45, 892, 234]  # 假設這是 "I love you" 的 token IDs
chinese = transformer.translate(english)
print(f"翻譯結果: {chinese}")
```

---

## 🚀 Transformer 的應用

### 1. GPT（生成式預訓練 Transformer）

**架構**：只用解碼器（Decoder-only）

```
任務：文本生成

輸入：「今天天氣」
輸出：「很好」

輸入：「今天天氣很好」
輸出：「，適合出遊」

→ 持續生成文本
```

**比喻**：接龍遊戲

```
你說：「從前有座山」
GPT：「山上有座廟」
你說：「從前有座山，山上有座廟」
GPT：「廟裡有個老和尚」
...
```

### 2. BERT（雙向編碼器表示）

**架構**：只用編碼器（Encoder-only）

```
任務：理解文本（不生成）

應用：
- 情感分析：「這部電影很棒」→ 正面
- 問答系統：「台北在哪？」→ 「台灣北部」
- 文本分類：「蘋果發布新手機」→ 科技類
```

**比喻**：閱讀理解專家

```
BERT 像學生做閱讀理解：
1. 讀完整篇文章
2. 理解文章意思
3. 回答問題
（但不會「寫作文」）
```

### 3. T5（Text-to-Text Transfer Transformer）

**架構**：完整 Transformer（Encoder-Decoder）

```
任務：萬能文本轉換

翻譯：「translate English to Chinese: I love you」
     → 「我愛你」

摘要：「summarize: [長文章]」
     → 「[摘要]」

問答：「question: What is AI? context: [文章]」
     → 「人工智慧是...」
```

**比喻**：瑞士刀（萬能工具）

---

## 📊 Transformer vs RNN/LSTM

| 特性 | RNN/LSTM | Transformer |
|------|----------|-------------|
| **並行性** | ❌ 必須順序處理 | ✅ 完全並行 |
| **訓練速度** | ⭐⭐ 慢 | ⭐⭐⭐⭐⭐ 快 |
| **長距離依賴** | ⭐⭐ 會衰減 | ⭐⭐⭐⭐⭐ 不衰減 |
| **記憶體需求** | ⭐⭐⭐⭐ 小 | ⭐⭐ 大（O(n²)） |
| **可解釋性** | ⭐⭐ 難 | ⭐⭐⭐⭐ 注意力可視化 |
| **短序列（<100）** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **長序列（>1000）** | ⭐⭐ | ⭐⭐⭐⭐⭐ |

**選擇建議**：
- ✅ **Transformer**：現代 NLP 首選（GPT、BERT）
- 🔄 **RNN/LSTM**：資源受限、實時處理

---

## 🎓 實務技巧

### 1. 注意力視覺化

```python
def visualize_attention(attention_weights, src_words, tgt_words):
    """
    視覺化注意力權重

    比喻：看翻譯時「對齊」哪些詞
    """
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(10, 10))

    # 繪製熱力圖
    im = ax.imshow(attention_weights, cmap='Blues')

    # 設定標籤
    ax.set_xticks(range(len(src_words)))
    ax.set_yticks(range(len(tgt_words)))
    ax.set_xticklabels(src_words)
    ax.set_yticklabels(tgt_words)

    # 旋轉標籤
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")

    # 標題
    ax.set_title("Attention Weights")
    ax.set_xlabel("Source (English)")
    ax.set_ylabel("Target (Chinese)")

    plt.colorbar(im)
    plt.tight_layout()
    plt.savefig('attention_visualization.png', dpi=150)
    plt.show()

# 使用
src = ['I', 'love', 'you']
tgt = ['我', '愛', '你']
# attention_weights: (3, 3) 矩陣
visualize_attention(attention_weights, src, tgt)
```

### 2. 學習率預熱（Warmup）

**問題**：Transformer 訓練初期不穩定

**解決**：學習率預熱

```python
def transformer_lr_schedule(step, d_model, warmup_steps=4000):
    """
    Transformer 學習率調度

    比喻：
    - 前期（warmup）：慢慢加速（學習率遞增）
    - 後期：逐漸減速（學習率遞減）

    就像開車：
    起步慢 → 加速 → 巡航速度 → 減速
    """
    arg1 = step ** -0.5
    arg2 = step * (warmup_steps ** -1.5)

    lr = (d_model ** -0.5) * min(arg1, arg2)

    return lr

# 視覺化
import matplotlib.pyplot as plt

steps = range(1, 10000)
lrs = [transformer_lr_schedule(s, d_model=512) for s in steps]

plt.figure(figsize=(10, 6))
plt.plot(steps, lrs)
plt.xlabel('Steps')
plt.ylabel('Learning Rate')
plt.title('Transformer Learning Rate Schedule')
plt.grid(True)
plt.show()
```

### 3. Label Smoothing

**問題**：模型過度自信

```
普通訓練：
正確答案「我」→ 機率 1.0
其他答案     → 機率 0.0

問題：過於絕對，不夠靈活
```

**解決**：標籤平滑

```python
def label_smoothing(true_label, vocab_size, smoothing=0.1):
    """
    標籤平滑

    比喻：
    不要太絕對，保持一點「懷疑」

    正確答案：0.9（原本 1.0）
    其他答案：0.1 / (vocab_size - 1)
    """
    confidence = 1.0 - smoothing
    smooth_value = smoothing / (vocab_size - 1)

    # 初始化（所有詞都有小機率）
    smoothed = np.full(vocab_size, smooth_value)

    # 正確答案有更高機率
    smoothed[true_label] = confidence

    return smoothed
```

---

## 🔗 總結

### Transformer 革命性創新

1. **自注意力機制**：自動找出詞之間的關聯
2. **並行計算**：不用按順序處理，超快
3. **長距離依賴**：第 1 個詞和第 1000 個詞直接連接

### 核心組件

- **編碼器**：理解輸入
- **解碼器**：生成輸出
- **注意力**：找出重要關聯
- **位置編碼**：加入順序資訊

### 主要應用

- **GPT**：文本生成（ChatGPT）
- **BERT**：文本理解（搜尋、分類）
- **T5**：通用轉換

### 下一步學習

- **Vision Transformer**：Transformer 用於圖像
- **Efficient Transformers**：降低記憶體需求
- **Sparse Attention**：稀疏注意力機制

---

*最後更新: 2025-11-26*
