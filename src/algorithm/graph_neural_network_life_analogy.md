# 圖神經網路（GNN）完整指南 - 用生活比喻理解

## 🎯 核心比喻：社交網路 vs 傳統數據

### 傳統神經網路的限制

```
CNN：處理圖片（網格結構）
┌─┬─┬─┐
│ │ │ │  每個像素有固定的鄰居
├─┼─┼─┤
│ │ │ │
└─┴─┴─┘

RNN：處理序列（鏈式結構）
A → B → C → D
前後順序固定

問題：
現實世界很多數據是「圖結構」
- 社交網路（朋友關係）
- 分子結構（原子鍵結）
- 交通網路（道路連接）
- 知識圖譜（實體關係）
→ 沒有固定結構！
```

### GNN：處理圖結構數據

```
圖（Graph）= 節點 + 邊

社交網路例子：
    Alice ─── Bob
      │        │
      │        │
    Carol ─── David

節點（Nodes）：人（Alice、Bob、Carol、David）
邊（Edges）：朋友關係（連線）

GNN 的任務：
1. 節點分類：判斷每個人的興趣
2. 邊預測：預測誰會成為朋友
3. 圖分類：判斷整個社群的特性
```

---

## 📚 生活化案例 1：朋友圈影響力

### 情境：判斷興趣愛好

```
社交網路：
    Alice（愛運動）─── Bob（？）
      │                    │
      │                    │
    Carol（愛運動）─── David（愛讀書）

問題：Bob 的興趣是什麼？

傳統 ML：
只看 Bob 自己的資料
→ 資訊不足

GNN：
看 Bob 的朋友圈：
- Alice 愛運動
- Carol 愛運動
- David 愛讀書

推論：Bob 的朋友大多愛運動
→ Bob 可能也愛運動（70% 機率）
```

### 核心思想：訊息傳遞

```
第 1 步：每個人知道自己的資訊
Alice：「我愛運動」
Bob：「我不確定」
Carol：「我愛運動」
David：「我愛讀書」

第 2 步：向朋友「廣播」自己的資訊
Alice → Bob：「我愛運動」
Carol → Bob：「我愛運動」
David → Bob：「我愛讀書」

第 3 步：Bob 綜合朋友的資訊
收到：[運動, 運動, 讀書]
加權平均 → Bob 傾向「運動」

第 4 步：重複多次（多層 GNN）
逐步擴散資訊，考慮更遠的朋友
```

---

## 🏗️ GNN 核心機制

### 1. 訊息傳遞（Message Passing）

**比喻**：八卦傳播

```
村莊八卦傳播：

第 1 輪（1-hop 鄰居）：
小明聽到「隔壁鄰居」的八卦

第 2 輪（2-hop 鄰居）：
小明聽到「鄰居的鄰居」的八卦

第 3 輪（3-hop 鄰居）：
小明聽到「更遠的人」的八卦

→ 越傳越遠，資訊越豐富
```

**數學表達**：

```
h_v^(k+1) = UPDATE(h_v^(k), AGGREGATE({h_u^(k) : u ∈ N(v)}))
            ↑                ↑
          更新函數          聚合鄰居資訊

比喻：
h_v：節點 v 的「知識」
N(v)：節點 v 的「朋友圈」
AGGREGATE：聽取朋友們的意見
UPDATE：更新自己的看法
```

### 2. 聚合函數（Aggregation）

**問題**：如何總結朋友的意見？

```
Bob 的朋友們：
Alice：[0.9, 0.1, 0.0]（90% 運動）
Carol：[0.8, 0.2, 0.0]（80% 運動）
David：[0.1, 0.1, 0.8]（80% 讀書）

方法 1：平均（Mean）
平均 = (0.9+0.8+0.1)/3, (0.1+0.2+0.1)/3, (0.0+0.0+0.8)/3
     = [0.6, 0.13, 0.27]
→ 60% 運動

方法 2：最大值（Max）
最大 = [max(0.9,0.8,0.1), max(0.1,0.2,0.1), max(0.0,0.0,0.8)]
     = [0.9, 0.2, 0.8]
→ 取最強的意見

方法 3：求和（Sum）
總和 = [2.6, 0.4, 0.8]
→ 朋友越多，影響越大

方法 4：注意力（Attention）
「Alice 是好友，權重 0.7」
「Carol 是普通朋友，權重 0.2」
「David 是點頭之交，權重 0.1」
加權 = 0.7×[0.9,0.1,0] + 0.2×[0.8,0.2,0] + 0.1×[0.1,0.1,0.8]
```

### 3. 更新函數（Update）

**作用**：結合「自己的看法」和「朋友的看法」

```
Bob 原本的想法：[0.5, 0.3, 0.2]（不確定）
朋友的意見：[0.6, 0.13, 0.27]（偏運動）

更新方式 1：直接替換
Bob 新想法 = [0.6, 0.13, 0.27]

更新方式 2：加權結合
Bob 新想法 = 0.5×[0.5,0.3,0.2] + 0.5×[0.6,0.13,0.27]
           = [0.55, 0.215, 0.235]

更新方式 3：神經網路
concat([自己的, 朋友的]) → MLP → 新想法
```

---

## 💻 從零實作：簡單 GNN

### 範例：論文引用網路

```python
import numpy as np

class SimpleGNN:
    def __init__(self, input_dim, hidden_dim, output_dim):
        """
        簡單的圖神經網路

        比喻：
        研究論文引用網路
        - 節點：論文
        - 邊：引用關係（A 引用 B）
        - 任務：分類論文主題

        參數：
            input_dim: 節點特徵維度（如：論文的詞向量）
            hidden_dim: 隱藏層維度
            output_dim: 輸出維度（如：3 個類別）
        """
        # 第 1 層 GNN
        self.W1 = np.random.randn(input_dim, hidden_dim) * 0.01
        self.b1 = np.zeros(hidden_dim)

        # 第 2 層 GNN
        self.W2 = np.random.randn(hidden_dim, output_dim) * 0.01
        self.b2 = np.zeros(output_dim)

    def aggregate_neighbors(self, node_features, adjacency_matrix, node_idx):
        """
        聚合鄰居資訊

        比喻：
        收集「引用這篇論文」的所有論文的資訊

        參數：
            node_features: 所有節點的特徵 (N, D)
            adjacency_matrix: 鄰接矩陣 (N, N)
            node_idx: 當前節點索引

        返回：
            聚合後的鄰居特徵
        """
        # 找出鄰居（引用這篇論文的其他論文）
        neighbors = adjacency_matrix[node_idx]

        # 獲取鄰居特徵
        neighbor_features = node_features[neighbors == 1]

        # 聚合（這裡用平均）
        if len(neighbor_features) == 0:
            return np.zeros_like(node_features[0])

        aggregated = np.mean(neighbor_features, axis=0)

        return aggregated

    def gnn_layer(self, node_features, adjacency_matrix, W, b):
        """
        GNN 層

        比喻：
        1. 收集鄰居意見
        2. 結合自己的看法
        3. 更新知識
        """
        N = len(node_features)
        new_features = []

        for i in range(N):
            # 1. 聚合鄰居
            neighbor_agg = self.aggregate_neighbors(
                node_features, adjacency_matrix, i
            )

            # 2. 結合自己和鄰居的特徵
            combined = node_features[i] + neighbor_agg

            # 3. 通過神經網路更新
            updated = np.maximum(0, combined.dot(W) + b)  # ReLU

            new_features.append(updated)

        return np.array(new_features)

    def forward(self, node_features, adjacency_matrix):
        """
        前向傳播

        比喻：
        多輪「八卦傳播」，逐步理解每篇論文的主題

        參數：
            node_features: 初始節點特徵（論文詞向量）
            adjacency_matrix: 引用關係矩陣

        返回：
            每個節點的分類結果
        """
        # 第 1 層 GNN
        h1 = self.gnn_layer(node_features, adjacency_matrix, self.W1, self.b1)

        # 第 2 層 GNN
        h2 = self.gnn_layer(h1, adjacency_matrix, self.W2, self.b2)

        # Softmax（轉成機率）
        exp_h2 = np.exp(h2 - np.max(h2, axis=1, keepdims=True))
        probs = exp_h2 / np.sum(exp_h2, axis=1, keepdims=True)

        return probs


# 測試：論文引用網路
def test_paper_citation_gnn():
    """
    測試 GNN：論文主題分類

    比喻：
    5 篇論文，分成 3 個主題（AI、DB、HCI）
    """
    # 5 篇論文的特徵（簡化：用隨機向量表示）
    node_features = np.random.randn(5, 10)

    # 引用關係（鄰接矩陣）
    # adjacency_matrix[i][j] = 1 表示論文 j 引用論文 i
    adjacency_matrix = np.array([
        [0, 1, 1, 0, 0],  # 論文 0 被 1, 2 引用
        [0, 0, 1, 0, 0],  # 論文 1 被 2 引用
        [0, 0, 0, 1, 1],  # 論文 2 被 3, 4 引用
        [0, 0, 0, 0, 1],  # 論文 3 被 4 引用
        [0, 0, 0, 0, 0]   # 論文 4 沒有被引用
    ])

    # 創建 GNN
    gnn = SimpleGNN(input_dim=10, hidden_dim=16, output_dim=3)

    # 前向傳播
    predictions = gnn.forward(node_features, adjacency_matrix)

    print("論文主題預測：")
    topics = ['AI', 'DB', 'HCI']
    for i, pred in enumerate(predictions):
        topic_idx = np.argmax(pred)
        confidence = pred[topic_idx]
        print(f"論文 {i}: {topics[topic_idx]} ({confidence*100:.1f}% 信心)")

test_paper_citation_gnn()
```

**輸出範例**：
```
論文主題預測：
論文 0: AI (45.2% 信心)
論文 1: AI (52.1% 信心)
論文 2: DB (38.9% 信心)
論文 3: AI (61.3% 信心)
論文 4: HCI (42.7% 信心)
```

---

## 🔬 經典 GNN 架構

### 1. GCN（圖卷積網路）

**核心思想**：類似 CNN 的卷積，但在圖上

```
CNN 卷積：
┌─┬─┬─┐
│1│2│3│  對「鄰近像素」做加權平均
├─┼─┼─┤
│4│5│6│
└─┴─┴─┘

GCN 卷積：
    A ─── B
     \   /   對「鄰居節點」做加權平均
      \ /
       C
```

**更新公式**：

```python
def gcn_layer(H, A, W):
    """
    GCN 層

    比喻：
    每個人聽取朋友意見，更新自己的看法

    參數：
        H: 節點特徵矩陣 (N, D)
        A: 歸一化鄰接矩陣 (N, N)
        W: 權重矩陣 (D, D')

    公式：
        H' = σ(AHW)
        ↑    ↑ ↑ ↑
        激活 鄰接×特徵×權重
    """
    # 聚合鄰居特徵
    aggregated = A.dot(H)

    # 線性轉換
    transformed = aggregated.dot(W)

    # 激活函數
    activated = np.maximum(0, transformed)  # ReLU

    return activated

# 歸一化鄰接矩陣（考慮度數）
def normalize_adjacency(A):
    """
    度數歸一化

    比喻：
    朋友多的人，每個朋友影響力小一點
    朋友少的人，每個朋友影響力大一點
    """
    # 計算度數
    D = np.diag(np.sum(A, axis=1))
    D_inv_sqrt = np.linalg.inv(np.sqrt(D))

    # 歸一化：D^(-1/2) × A × D^(-1/2)
    A_norm = D_inv_sqrt.dot(A).dot(D_inv_sqrt)

    return A_norm
```

### 2. GraphSAGE（圖採樣聚合）

**問題**：GCN 需要完整圖，大圖計算慢

**解決**：只採樣部分鄰居

```
完整 GCN：
考慮「所有」鄰居（可能有 1000 個）
→ 計算慢

GraphSAGE：
隨機採樣「K 個」鄰居（如 K=10）
→ 計算快

比喻：
你想知道全班對某議題的看法
完整調查：問全班 50 人（慢）
抽樣調查：隨機問 10 人（快，也有代表性）
```

```python
def graphsage_sample_neighbors(adjacency_matrix, node_idx, sample_size=10):
    """
    採樣鄰居

    比喻：
    從所有朋友中隨機選 K 個

    參數：
        adjacency_matrix: 鄰接矩陣
        node_idx: 當前節點
        sample_size: 採樣數量

    返回：
        採樣的鄰居索引
    """
    # 獲取所有鄰居
    neighbors = np.where(adjacency_matrix[node_idx] == 1)[0]

    # 如果鄰居少於 sample_size，全部使用
    if len(neighbors) <= sample_size:
        return neighbors

    # 隨機採樣
    sampled = np.random.choice(neighbors, size=sample_size, replace=False)

    return sampled

def graphsage_aggregate(node_features, sampled_neighbors):
    """
    聚合採樣的鄰居

    支援多種聚合方式：
    1. Mean：平均
    2. Max：最大池化
    3. LSTM：序列聚合
    """
    # 方法 1：平均聚合
    neighbor_features = node_features[sampled_neighbors]
    aggregated = np.mean(neighbor_features, axis=0)

    return aggregated
```

### 3. GAT（圖注意力網路）

**創新**：不同鄰居有不同重要性

```
普通 GNN：
所有鄰居「平等」對待

GAT：
重要的鄰居「權重高」
不重要的鄰居「權重低」

比喻：
你有 10 個朋友
- 好友 Alice：意見權重 0.5（很重要）
- 同事 Bob：意見權重 0.3
- 路人 Carol：意見權重 0.01（幾乎忽略）

→ 自動學習誰的意見重要
```

**注意力機制**：

```python
def gat_attention(h_i, h_j, W, a):
    """
    計算注意力分數

    比喻：
    計算「節點 i 對節點 j 的重視程度」

    參數：
        h_i: 節點 i 的特徵
        h_j: 節點 j 的特徵
        W: 權重矩陣
        a: 注意力向量

    公式：
        e_ij = LeakyReLU(a^T [W×h_i || W×h_j])
               ↑         ↑
            注意力分數   拼接特徵
    """
    # 線性轉換
    Wh_i = h_i.dot(W)
    Wh_j = h_j.dot(W)

    # 拼接
    concat = np.concatenate([Wh_i, Wh_j])

    # 注意力分數
    e_ij = np.dot(a, concat)

    # LeakyReLU
    e_ij = np.maximum(0.01 * e_ij, e_ij)

    return e_ij

def gat_aggregate(node_features, adjacency_matrix, node_idx, W, a):
    """
    GAT 聚合（帶注意力）

    步驟：
    1. 計算對每個鄰居的注意力分數
    2. Softmax 歸一化
    3. 加權聚合
    """
    # 獲取鄰居
    neighbors = np.where(adjacency_matrix[node_idx] == 1)[0]

    # 計算注意力分數
    attention_scores = []
    for neighbor in neighbors:
        score = gat_attention(
            node_features[node_idx],
            node_features[neighbor],
            W, a
        )
        attention_scores.append(score)

    # Softmax 歸一化
    attention_scores = np.array(attention_scores)
    attention_weights = np.exp(attention_scores) / np.sum(np.exp(attention_scores))

    # 加權聚合
    aggregated = np.zeros_like(node_features[node_idx])
    for i, neighbor in enumerate(neighbors):
        aggregated += attention_weights[i] * node_features[neighbor]

    return aggregated
```

---

## 🎯 實戰應用

### 1. 社交網路分析

**任務 1：社群檢測**

```
問題：
在 Facebook 上，哪些人是「同一個圈子」？

比喻：
找出「閨蜜團」、「同事群」、「球友圈」

GNN 解法：
1. 節點：用戶
2. 邊：好友關係
3. 訓練：節點聚類
4. 結果：相似的人分到同一類
```

**任務 2：影響力預測**

```
問題：
誰是「意見領袖」？（影響力最大）

GNN 解法：
1. 分析圖結構（中心性）
2. 考慮朋友數量和質量
3. 預測資訊傳播範圍
```

### 2. 分子性質預測

**任務**：預測新藥物是否有效

```
分子 = 圖
- 節點：原子（C、H、O、N...）
- 邊：化學鍵（單鍵、雙鍵、三鍵）

目標：
輸入：分子結構
輸出：是否能治療某種疾病（0/1）

比喻：
就像「看分子的朋友圈」
- 原子周圍有哪些原子？
- 鍵結方式如何？
→ 預測分子性質
```

```python
class MoleculeGNN:
    """分子性質預測 GNN"""

    def __init__(self):
        # 原子類型（C, H, O, N, ...）
        self.atom_types = ['C', 'H', 'O', 'N', 'S', 'P']

        # GNN 層
        self.gnn_layers = [
            GCNLayer(input_dim=16, output_dim=32),
            GCNLayer(input_dim=32, output_dim=64)
        ]

        # 圖級別池化（整個分子的表示）
        self.readout = GlobalMeanPooling()

        # 分類層
        self.classifier = FullyConnected(input_dim=64, output_dim=1)

    def forward(self, molecule_graph):
        """
        預測分子性質

        比喻：
        1. 理解每個原子的環境（GNN）
        2. 整合成整個分子的表示（Pooling）
        3. 判斷分子是否有效（分類器）
        """
        # 1. 節點嵌入（原子特徵）
        node_features = self.embed_atoms(molecule_graph.atoms)

        # 2. GNN 層（傳播資訊）
        for layer in self.gnn_layers:
            node_features = layer(node_features, molecule_graph.adjacency)

        # 3. 圖池化（整個分子的表示）
        molecule_embedding = self.readout(node_features)

        # 4. 分類
        prediction = self.classifier(molecule_embedding)

        return prediction
```

### 3. 推薦系統

**任務**：商品推薦

```
用戶-商品 二部圖：
用戶 ──── 商品
 │  \   /  │
 │   \ /   │
用戶 ──── 商品

節點：
- 用戶節點
- 商品節點

邊：
- 用戶購買商品
- 用戶瀏覽商品

GNN 預測：
「用戶 A 會不會喜歡商品 B？」

比喻：
- 看用戶的朋友買了什麼
- 看商品被誰買過
- 綜合判斷
```

### 4. 交通流量預測

**任務**：預測道路擁堵

```
道路網路 = 圖
- 節點：路口
- 邊：道路
- 節點特徵：當前車流量、時間

目標：
預測「未來 30 分鐘」每個路口的車流量

GNN 優勢：
考慮「鄰近路口」的影響
（某路口塞車 → 影響周圍路口）
```

---

## 🚀 進階技術

### 1. 異質圖（Heterogeneous Graph）

**概念**：不同類型的節點和邊

```
學術網路：
- 節點類型：作者、論文、會議
- 邊類型：
  - 作者 → 寫 → 論文
  - 論文 → 發表於 → 會議
  - 作者 → 合作 → 作者

普通 GNN：
所有節點「一視同仁」

異質圖 GNN：
不同類型節點「區別對待」
- 作者節點用 W_author
- 論文節點用 W_paper
```

### 2. 時間圖（Temporal Graph）

**概念**：圖結構隨時間變化

```
動態社交網路：
今天：A 和 B 是朋友
明天：A 和 B 絕交
後天：A 和 C 成為朋友

普通 GNN：
只看「靜態快照」

時間圖 GNN：
考慮「演化過程」
- RNN + GNN 結合
- 預測「未來的連接」
```

### 3. 自監督學習

**問題**：圖數據標籤少

**解決**：自己創造訓練任務

```
任務 1：連接預測
遮蔽部分邊 → 預測是否有邊
（就像「完形填空」）

任務 2：屬性重構
遮蔽節點特徵 → 重構特徵
（就像「猜謎遊戲」）

任務 3：對比學習
同一個圖的不同視角應該相似
（就像「找相似」）
```

---

## 📊 GNN vs 其他方法

| 方法 | 適用數據 | 優點 | 缺點 |
|------|---------|------|------|
| **CNN** | 網格（圖片） | 平移不變性 | 無法處理圖 |
| **RNN** | 序列（文本） | 時序建模 | 無法處理圖 |
| **傳統圖演算法** | 圖（PageRank） | 可解釋 | 無法學習特徵 |
| **GNN** | 圖 | 端到端學習 | 計算複雜度高 |

---

## 🎓 實務建議

### 1. 圖構建技巧

```python
def build_graph_from_data(data, threshold=0.5):
    """
    從數據構建圖

    比喻：定義「誰和誰是朋友」的規則

    策略 1：基於距離
    如果兩個節點「相似度 > 閾值」→ 連邊

    策略 2：K 近鄰
    每個節點連接「最近的 K 個節點」

    策略 3：領域知識
    根據實際意義構建（如：同一公司 → 連邊）
    """
    N = len(data)
    adjacency_matrix = np.zeros((N, N))

    for i in range(N):
        for j in range(i+1, N):
            # 計算相似度（如：餘弦相似度）
            similarity = cosine_similarity(data[i], data[j])

            # 如果相似度高，連邊
            if similarity > threshold:
                adjacency_matrix[i, j] = 1
                adjacency_matrix[j, i] = 1

    return adjacency_matrix
```

### 2. 過平滑問題

**問題**：GNN 層數太多 → 所有節點特徵變相同

```
比喻：
八卦傳太多輪
→ 最後全村的八卦都一樣
→ 失去個性

2 層 GNN：
節點 A：[0.8, 0.2]
節點 B：[0.2, 0.8]
→ 特徵不同 ✓

10 層 GNN：
節點 A：[0.5, 0.5]
節點 B：[0.5, 0.5]
→ 特徵完全相同 ✗
```

**解決方案**：
```python
# 1. 限制層數（2-3 層通常足夠）
gnn = GNN(num_layers=2)

# 2. 殘差連接（保留原始特徵）
h_new = h_old + gnn_layer(h_old)

# 3. Jumping Knowledge（跳躍連接）
h_final = concat([h_0, h_1, h_2])  # 拼接所有層
```

### 3. 大圖訓練技巧

```python
# 技巧 1：Mini-batch 訓練
# 每次只訓練「部分節點」
batch_nodes = random.sample(all_nodes, batch_size=256)

# 技巧 2：鄰居採樣
# 只考慮「K 個鄰居」而非全部
sampled_neighbors = sample_neighbors(node, K=10)

# 技巧 3：Layer-wise 訓練
# 逐層訓練，而非端到端
train_layer_1()
train_layer_2()
...
```

---

## 🔗 總結

### GNN 核心思想

1. **訊息傳遞**：節點交換資訊
2. **鄰居聚合**：總結朋友意見
3. **特徵更新**：更新自己的表示

### 主要優勢

- ✅ 處理非歐幾里得數據（圖結構）
- ✅ 考慮關係資訊（不只看節點自己）
- ✅ 端到端學習
- ✅ 歸納能力（可泛化到新節點）

### 主要挑戰

- ⚠️ 計算複雜度高（大圖）
- ⚠️ 過平滑問題（深層網路）
- ⚠️ 異質圖處理困難

### 主要應用

- 社交網路分析
- 藥物發現
- 推薦系統
- 交通預測
- 知識圖譜

### 未來方向

- 可解釋性（為什麼做這個預測？）
- 大規模圖學習（億級節點）
- 動態圖學習（實時更新）
- 跨領域應用

---

*最後更新: 2025-11-26*
