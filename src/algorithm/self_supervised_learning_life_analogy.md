# 自監督學習完整指南 - 用生活比喻理解

## 🎯 核心比喻：自學 vs 上課

### 三種學習方式對比

```
監督學習（Supervised Learning）：
老師教你「標準答案」

例子：
老師：「這是貓」（給標籤）
學生：「我記住了」

問題：需要大量「標註數據」（昂貴）
```

```
無監督學習（Unsupervised Learning）：
自己找規律，沒有答案

例子：
學生看 1000 張圖片
發現：「有些圖片很像（都是動物）」

問題：學到的東西不一定有用
```

```
自監督學習（Self-Supervised Learning）：
自己出題、自己答題

例子：
學生看一句話：「我愛___」
自己創造任務：「填空題，答案是『你』」
→ 通過「自己創造的任務」學習

優點：
✅ 不需要人工標註（省錢）
✅ 學到的特徵更通用（有用）
✅ 可以使用海量數據
```

---

## 📚 生活化案例 1：拼圖遊戲

### 情境：學習圖像特徵

```
監督學習：
老師告訴你「這是貓」「這是狗」
→ 需要 10 萬張標註圖片

自監督學習：
自己玩「拼圖遊戲」
→ 不需要標註！

步驟：
1. 拿一張圖片（沒有標籤）
2. 切成 9 塊拼圖
3. 打亂順序
4. 任務：把拼圖「還原」

學到什麼？
- 物體的邊緣
- 顏色的連續性
- 紋理特徵
→ 雖然沒有標籤，但學到了「圖像理解」！
```

### 遷移學習

```
訓練：用 100 萬張「無標註」圖片玩拼圖
→ 學會理解圖像

微調：用 1000 張「有標註」圖片做分類
→ 快速學會貓狗分類

比喻：
先「自學」基礎知識（大量數據）
再「上課」學專業技能（少量標註數據）
→ 事半功倍！
```

---

## 🏗️ 自監督學習的核心技巧

### 1. Pretext Task（前置任務）

**概念**：設計「自動生成標籤」的任務

```
任務 1：圖像旋轉預測
1. 隨機旋轉圖片（0°, 90°, 180°, 270°）
2. 任務：預測「旋轉了幾度？」
3. 標籤：自動生成（旋轉角度）

學到什麼？
- 物體的方向
- 空間關係

任務 2：拼圖排序
1. 切成 9 塊，打亂
2. 任務：「第 5 塊在哪？」
3. 標籤：原始位置（自動知道）

學到什麼？
- 物體的結構
- 部分與整體的關係

任務 3：顏色化
1. 把彩色圖片變灰階
2. 任務：「還原顏色」
3. 標籤：原始顏色（自動知道）

學到什麼？
- 物體的語義（天空是藍色、草地是綠色）
```

### 2. 對比學習（Contrastive Learning）

**核心思想**：相似的要接近，不相似的要遠離

```
比喻：整理照片

你有 1000 張照片：
- 「我在海邊」的照片 → 應該很相似
- 「我在海邊」vs「貓咪」→ 應該不相似

對比學習：
1. 同一張圖的「不同視角」→ 拉近（正樣本對）
2. 不同圖片 → 推遠（負樣本對）

數學：
相似度(圖1-增強版, 圖1-另一增強版) → 高
相似度(圖1, 圖2) → 低
```

**數據增強**：

```python
def create_positive_pair(image):
    """
    創建正樣本對

    比喻：
    同一張照片的「兩個版本」
    （本質相同，看起來不同）

    方法：
    - 裁切不同區域
    - 改變顏色
    - 翻轉
    - 加噪音
    """
    # 增強版本 1
    aug1 = random_crop(image)
    aug1 = color_jitter(aug1)
    aug1 = horizontal_flip(aug1)

    # 增強版本 2（不同的隨機操作）
    aug2 = random_crop(image)
    aug2 = color_jitter(aug2)
    aug2 = rotation(aug2)

    return aug1, aug2

# 使用
img = load_image("cat.jpg")
positive_pair = create_positive_pair(img)
# positive_pair[0] 和 positive_pair[1] 應該「相似」
```

---

## 💻 經典算法實作

### 1. SimCLR（Simple Contrastive Learning）

**核心思想**：最大化正樣本對的相似度

```python
import numpy as np

class SimCLR:
    def __init__(self, encoder, projection_dim=128):
        """
        SimCLR 對比學習

        比喻：
        訓練模型「認出」同一張圖的不同版本

        參數：
            encoder: 編碼器（如 ResNet）
            projection_dim: 投影頭維度
        """
        self.encoder = encoder
        self.projection_head = self.build_projection_head(projection_dim)

    def build_projection_head(self, dim):
        """
        投影頭：把特徵投影到「對比空間」

        比喻：
        把複雜的圖像特徵
        壓縮成「簡單的指紋」（128 維向量）
        """
        class ProjectionHead:
            def __init__(self, input_dim, output_dim):
                self.w1 = np.random.randn(input_dim, 256) * 0.01
                self.w2 = np.random.randn(256, output_dim) * 0.01

            def forward(self, x):
                h = np.maximum(0, x.dot(self.w1))  # ReLU
                z = h.dot(self.w2)
                # L2 歸一化（讓向量在單位球上）
                z = z / (np.linalg.norm(z) + 1e-8)
                return z

        return ProjectionHead(2048, dim)  # 假設 encoder 輸出 2048 維

    def compute_similarity(self, z_i, z_j):
        """
        計算相似度（餘弦相似度）

        比喻：
        兩個「指紋」有多像？

        公式：
            sim(z_i, z_j) = z_i · z_j / (||z_i|| × ||z_j||)

        值域：-1 到 1
        1 = 完全相同
        0 = 無關
        -1 = 完全相反
        """
        return np.dot(z_i, z_j)

    def nt_xent_loss(self, z_i, z_j, temperature=0.5):
        """
        NT-Xent 損失（對比損失）

        比喻：
        「正樣本對」應該相似（高分）
        「負樣本對」應該不相似（低分）

        參數：
            z_i, z_j: 正樣本對的表示
            temperature: 溫度參數（控制「柔和度」）
        """
        # 計算與所有樣本的相似度
        batch_size = len(z_i)

        # 正樣本相似度
        pos_sim = self.compute_similarity(z_i, z_j) / temperature

        # 負樣本相似度（與其他所有樣本）
        neg_sims = []
        for k in range(batch_size):
            if k != i:  # 排除自己
                neg_sim = self.compute_similarity(z_i, z_j[k]) / temperature
                neg_sims.append(neg_sim)

        # NT-Xent 損失
        # loss = -log(exp(pos_sim) / (exp(pos_sim) + Σexp(neg_sims)))
        numerator = np.exp(pos_sim)
        denominator = numerator + np.sum(np.exp(neg_sims))
        loss = -np.log(numerator / denominator)

        return loss

    def train_step(self, batch_images):
        """
        訓練一步

        比喻：
        1. 拿一批圖片
        2. 每張圖製作「兩個增強版本」
        3. 訓練模型「認出」它們是同一張
        """
        losses = []

        for image in batch_images:
            # 1. 數據增強（創建正樣本對）
            aug1, aug2 = create_positive_pair(image)

            # 2. 編碼
            h_i = self.encoder.forward(aug1)
            h_j = self.encoder.forward(aug2)

            # 3. 投影
            z_i = self.projection_head.forward(h_i)
            z_j = self.projection_head.forward(h_j)

            # 4. 計算損失
            loss = self.nt_xent_loss(z_i, z_j)
            losses.append(loss)

        return np.mean(losses)

    def extract_features(self, image):
        """
        提取特徵（訓練後使用）

        比喻：
        把圖片轉成「指紋」
        用於下游任務（分類、檢索等）
        """
        h = self.encoder.forward(image)
        return h  # 只用編碼器，不用投影頭


# 使用範例
def train_simclr():
    """訓練 SimCLR"""

    # 準備數據（無標註！）
    unlabeled_images = load_unlabeled_images()  # 100 萬張圖片

    # 創建 SimCLR
    encoder = ResNet50()  # 編碼器
    simclr = SimCLR(encoder)

    # 訓練
    for epoch in range(100):
        for batch in get_batches(unlabeled_images, batch_size=256):
            loss = simclr.train_step(batch)

            if epoch % 10 == 0:
                print(f"Epoch {epoch}, Loss: {loss:.4f}")

    # 微調（用少量標註數據）
    labeled_images, labels = load_labeled_images()  # 1000 張

    # 凍結編碼器，只訓練分類頭
    classifier = FullyConnected(input_dim=2048, output_dim=10)
    fine_tune(simclr.encoder, classifier, labeled_images, labels)

train_simclr()
```

---

### 2. BERT（Masked Language Model）

**任務**：填空題

```
原始句子：
「我愛吃蘋果」

遮蔽版本：
「我愛吃[MASK]」

任務：
預測 [MASK] 是什麼
→ 答案：蘋果

標籤：
自動生成（原始詞）
```

**實作**：

```python
class BERT:
    def __init__(self, vocab_size, hidden_dim):
        """
        BERT 自監督學習

        比喻：
        玩「填空遊戲」學習語言

        參數：
            vocab_size: 詞彙量
            hidden_dim: 隱藏層維度
        """
        self.vocab_size = vocab_size
        self.transformer = Transformer(
            vocab_size=vocab_size,
            d_model=hidden_dim,
            num_layers=12
        )

    def mask_tokens(self, tokens, mask_prob=0.15):
        """
        隨機遮蔽單詞

        比喻：
        隨機塗黑 15% 的字

        策略：
        - 80%：替換成 [MASK]
        - 10%：替換成隨機詞
        - 10%：保持原樣

        為什麼這樣？
        避免模型「依賴」[MASK] 標記
        ```"""
        masked_tokens = tokens.copy()
        labels = tokens.copy()

        for i in range(len(tokens)):
            if np.random.rand() < mask_prob:
                rand = np.random.rand()

                if rand < 0.8:
                    # 80%：遮蔽
                    masked_tokens[i] = MASK_TOKEN
                elif rand < 0.9:
                    # 10%：隨機詞
                    masked_tokens[i] = np.random.randint(self.vocab_size)
                # 10%：保持原樣（不做處理）

            else:
                # 不遮蔽的詞，標籤設為 -1（不計算損失）
                labels[i] = -1

        return masked_tokens, labels

    def forward(self, tokens):
        """
        前向傳播

        比喻：
        看「塗黑」的句子
        猜測被塗黑的字是什麼
        """
        # 通過 Transformer
        hidden_states = self.transformer.forward(tokens)

        # 預測每個位置的詞
        predictions = self.predict_tokens(hidden_states)

        return predictions

    def train_step(self, sentences):
        """
        訓練一步

        比喻：
        1. 拿一批句子
        2. 隨機塗黑 15% 的字
        3. 訓練模型猜測被塗黑的字
        """
        total_loss = 0

        for sentence in sentences:
            # 1. 遮蔽
            masked_tokens, labels = self.mask_tokens(sentence)

            # 2. 預測
            predictions = self.forward(masked_tokens)

            # 3. 計算損失（只計算被遮蔽的詞）
            loss = 0
            for i, label in enumerate(labels):
                if label != -1:  # 被遮蔽的詞
                    loss += cross_entropy(predictions[i], label)

            total_loss += loss

        return total_loss / len(sentences)


# 使用範例
def pretrain_bert():
    """預訓練 BERT"""

    # 準備數據（無標註！）
    unlabeled_text = load_wikipedia()  # 維基百科全文

    # 創建 BERT
    bert = BERT(vocab_size=30000, hidden_dim=768)

    # 預訓練
    for epoch in range(100):
        for batch in get_batches(unlabeled_text, batch_size=256):
            loss = bert.train_step(batch)

            if epoch % 10 == 0:
                print(f"Epoch {epoch}, Loss: {loss:.4f}")

    # 微調（情感分析）
    labeled_reviews, sentiments = load_movie_reviews()  # 1000 條評論

    fine_tune_classifier(bert, labeled_reviews, sentiments)

pretrain_bert()
```

---

### 3. MoCo（Momentum Contrast）

**創新**：用「隊列」存儲負樣本

```
SimCLR 的問題：
需要「大批次」（batch size = 4096）
→ 需要很多 GPU（昂貴）

MoCo 的解決：
用「隊列」存儲「過去的」負樣本
→ 可以用小批次（batch size = 256）

比喻：
SimCLR = 每次考試，考官都是「新面孔」
MoCo = 考官是「過去幾次」考試的考官
→ 不需要同時請很多考官
```

```python
class MoCo:
    def __init__(self, encoder, queue_size=65536):
        """
        MoCo 對比學習

        比喻：
        維護一個「記憶隊列」存儲過去的樣本

        參數：
            encoder: 編碼器
            queue_size: 隊列大小（負樣本數量）
        """
        # Query 編碼器（正常更新）
        self.encoder_q = encoder

        # Key 編碼器（動量更新）
        self.encoder_k = encoder.copy()

        # 隊列（存儲過去的負樣本）
        self.queue = np.zeros((queue_size, 128))
        self.queue_ptr = 0

        # 動量係數
        self.momentum = 0.999

    def momentum_update(self):
        """
        動量更新 Key 編碼器

        比喻：
        Key 編碼器「慢慢」跟隨 Query 編碼器

        公式：
            θ_k = m × θ_k + (1-m) × θ_q
            ↑     ↑         ↑
          Key    保留99.9%  借鑑0.1%
        """
        for param_q, param_k in zip(
            self.encoder_q.parameters(),
            self.encoder_k.parameters()
        ):
            param_k = self.momentum * param_k + (1 - self.momentum) * param_q

    def enqueue_dequeue(self, keys):
        """
        更新隊列

        比喻：
        「先進先出」
        新樣本進來，舊樣本出去
        """
        batch_size = len(keys)

        # 加入隊列
        self.queue[self.queue_ptr:self.queue_ptr + batch_size] = keys

        # 更新指針
        self.queue_ptr = (self.queue_ptr + batch_size) % len(self.queue)

    def train_step(self, batch_images):
        """訓練一步"""

        losses = []

        for image in batch_images:
            # 1. 創建正樣本對
            query, key = create_positive_pair(image)

            # 2. 編碼
            q = self.encoder_q.forward(query)  # Query
            k = self.encoder_k.forward(key)    # Key（不反向傳播）

            # 3. 計算相似度
            # 正樣本：q 和 k
            pos_sim = np.dot(q, k)

            # 負樣本：q 和隊列中的所有樣本
            neg_sims = q.dot(self.queue.T)

            # 4. 對比損失
            logits = np.concatenate([[pos_sim], neg_sims])
            labels = 0  # 第 0 個是正樣本
            loss = cross_entropy(logits, labels)

            losses.append(loss)

            # 5. 更新隊列
            self.enqueue_dequeue([k])

        # 6. 動量更新 Key 編碼器
        self.momentum_update()

        return np.mean(losses)
```

---

## 🎯 自監督學習在 NLP

### 1. Word2Vec

**任務**：根據上下文預測詞

```
句子：「我愛吃___和香蕉」

任務：
填空，答案可能是「蘋果」

學到什麼？
「蘋果」和「香蕉」在語義上相近
（因為它們出現在相似的上下文）
```

### 2. GPT（自迴歸語言模型）

**任務**：預測下一個詞

```
輸入：「今天天氣」
任務：預測下一個詞
可能答案：「很好」「不錯」「糟糕」

標籤：
下一個詞（自動知道）
```

### 3. T5（Text-to-Text）

**任務**：各種文本轉換

```
填空：
輸入：「我愛吃<X>」
輸出：「蘋果」

翻譯：
輸入：「translate English to Chinese: I love you」
輸出：「我愛你」

摘要：
輸入：「summarize: [長文章]」
輸出：「[摘要]」

→ 統一成「文本到文本」任務
→ 可以用同一個模型
```

---

## 🚀 自監督學習在 CV

### 任務類型

```
1. Pretext Tasks（前置任務）
   - 旋轉預測
   - 拼圖還原
   - 顏色化

2. Contrastive Learning（對比學習）
   - SimCLR
   - MoCo
   - BYOL

3. Masked Image Modeling（遮蔽圖像建模）
   - MAE（Masked Autoencoder）
   - BEiT（類似 BERT）

4. Self-Distillation（自蒸餾）
   - DINO
   - EsViT
```

---

## 📊 自監督 vs 監督 vs 無監督

| 特性 | 監督學習 | 無監督學習 | 自監督學習 |
|------|---------|-----------|----------|
| **需要標註** | ✅ 是（大量） | ❌ 否 | ❌ 否 |
| **學習目標** | 明確（標籤） | 模糊（聚類） | 明確（自動任務） |
| **數據需求** | 少（1萬） | 大（10萬） | 大（100萬） |
| **效果** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **成本** | 高（標註） | 低 | 低 |
| **泛化能力** | 中 | 中 | 高 |

---

## 🎓 實務建議

### 1. 數據增強策略

```python
# 圖像增強
augmentations = [
    RandomCrop(size=224),
    ColorJitter(brightness=0.4, contrast=0.4),
    RandomHorizontalFlip(p=0.5),
    RandomRotation(degrees=15),
    GaussianBlur(kernel_size=3),
]

# 文本增強
def augment_text(sentence):
    """文本增強策略"""

    # 1. 回譯（Back Translation）
    # 中文 → 英文 → 中文
    en = translate_to_english(sentence)
    augmented = translate_to_chinese(en)

    # 2. 同義詞替換
    # 「好」→「棒」「優秀」
    augmented = replace_with_synonym(sentence)

    # 3. 隨機插入
    augmented = random_insert_word(sentence)

    return augmented
```

### 2. 溫度參數調優

```python
# 溫度參數（temperature）的影響

temperature = 0.1  # 低溫
→ 相似度分數「集中」
→ 對比更明顯
→ 訓練更難（容易過擬合）

temperature = 1.0  # 高溫
→ 相似度分數「分散」
→ 對比較柔和
→ 訓練更穩定

推薦：temperature = 0.5（中等）
```

### 3. 負樣本選擇

```python
# 策略 1：隨機負樣本
# 從 batch 中隨機選擇
negative_samples = random.sample(batch, k=256)

# 策略 2：困難負樣本（Hard Negatives）
# 選擇「最像」但「不是」的樣本
similarities = compute_similarities(query, all_samples)
hard_negatives = top_k_similar(similarities, k=64)

# 策略 3：混合策略
negatives = random_negatives + hard_negatives
```

---

## 🔗 總結

### 自監督學習核心思想

1. **自動生成標籤**：不需要人工標註
2. **Pretext Task**：設計前置任務
3. **遷移學習**：預訓練 + 微調

### 主要優勢

- ✅ 不需要標註數據（省成本）
- ✅ 可使用海量數據
- ✅ 學到通用特徵（泛化好）
- ✅ 少量標註即可微調

### 主要挑戰

- ⚠️ 需要大算力（預訓練慢）
- ⚠️ 前置任務設計需技巧
- ⚠️ 不是所有領域都適用

### 主要應用

- **CV**：圖像分類、目標檢測
- **NLP**：BERT、GPT 系列
- **多模態**：CLIP（文本-圖像）
- **推薦系統**：用戶行為建模

### 未來方向

- 多模態自監督學習
- 小樣本自監督學習
- 在線自監督學習
- 可解釋自監督學習

---

*最後更新: 2025-11-26*
