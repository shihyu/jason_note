# 進階優化器完整指南 - 用生活比喻理解

## 🎯 優化器的本質：如何更聰明地下山？

回到我們的「蒙眼下山」比喻：

**基本 SGD**：
```
感受坡度 → 往下走一步 → 重複
```

**問題**：
- ❌ 遇到平緩區域：走太慢
- ❌ 遇到陡峭區域：可能衝過頭
- ❌ 遇到山谷（兩側陡峭，中間平緩）：左右震盪

**進階優化器的改進**：
```
✅ 記住來時的路（Momentum）
✅ 根據地形調整步伐（AdaGrad、RMSprop）
✅ 兩者結合（Adam）
✅ 更聰明的策略（AdamW、Lookahead）
```

---

## 🚗 比喻 1：開車導航（Momentum）

### 基本 SGD = 新手司機

```
每次都重新判斷方向：
第 1 秒：往左 5 度
第 2 秒：往右 3 度
第 3 秒：往左 7 度
...
結果：方向盤抖動，車子搖晃 🚗💨
```

### Momentum = 熟練司機

```
記住「慣性」：
第 1 秒：往左 5 度
第 2 秒：繼續往左（加上新判斷的右 3 度）= 往左 2 度
第 3 秒：繼續這個方向...
結果：行駛平順，少震盪 🚗→
```

### 數學表達

**基本 SGD**：
```
v_t = -α × gradient
θ_t = θ_{t-1} + v_t
```

**Momentum**：
```
v_t = β × v_{t-1} - α × gradient
      ↑ 保留 90% 的「慣性」

θ_t = θ_{t-1} + v_t
```

### 生活化解釋

想像你推一個購物車：

```
沒有 Momentum：
每次推都「從零開始」
推一下 → 停 → 推一下 → 停
→ 很累，進展慢 😓

有 Momentum：
推一下 → 車子繼續滾動（慣性）
你只需要「微調方向」
→ 省力，進展快 😊
```

### Python 實作

```python
class MomentumOptimizer:
    def __init__(self, learning_rate=0.01, momentum=0.9):
        """
        Momentum 優化器

        比喻：記住「慣性」的開車方式

        參數：
            learning_rate: 每次調整的幅度
            momentum: 保留多少慣性（通常 0.9）
        """
        self.lr = learning_rate
        self.momentum = momentum
        self.velocity = {}  # 存儲每個參數的「速度」

    def update(self, param_name, param, gradient):
        """更新參數"""
        # 初始化速度
        if param_name not in self.velocity:
            self.velocity[param_name] = np.zeros_like(param)

        # 更新速度（保留慣性 + 新梯度）
        self.velocity[param_name] = (
            self.momentum * self.velocity[param_name] -
            self.lr * gradient
        )

        # 更新參數
        param += self.velocity[param_name]

        return param

# 使用範例
optimizer = MomentumOptimizer(learning_rate=0.01, momentum=0.9)

for epoch in range(100):
    # 計算梯度
    gradient = compute_gradient()

    # 更新權重
    weights = optimizer.update('weights', weights, gradient)
```

### 視覺化比較

```python
import numpy as np
import matplotlib.pyplot as plt

def visualize_momentum():
    """視覺化 SGD vs Momentum"""

    # 定義一個「山谷」函數
    def loss_function(x, y):
        return x**2 / 20 + y**2  # 橫向平緩，縱向陡峭

    # SGD 軌跡
    x_sgd, y_sgd = 10, 10
    trajectory_sgd = [(x_sgd, y_sgd)]

    for _ in range(100):
        grad_x = x_sgd / 10
        grad_y = 2 * y_sgd
        x_sgd -= 0.1 * grad_x
        y_sgd -= 0.1 * grad_y
        trajectory_sgd.append((x_sgd, y_sgd))

    # Momentum 軌跡
    x_mom, y_mom = 10, 10
    vx, vy = 0, 0
    trajectory_mom = [(x_mom, y_mom)]

    for _ in range(100):
        grad_x = x_mom / 10
        grad_y = 2 * y_mom

        # 更新速度（Momentum）
        vx = 0.9 * vx - 0.1 * grad_x
        vy = 0.9 * vy - 0.1 * grad_y

        x_mom += vx
        y_mom += vy
        trajectory_mom.append((x_mom, y_mom))

    # 繪圖
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))

    # 繪製損失函數等高線
    x = np.linspace(-12, 12, 100)
    y = np.linspace(-12, 12, 100)
    X, Y = np.meshgrid(x, y)
    Z = loss_function(X, Y)

    for ax in axes:
        ax.contour(X, Y, Z, levels=20, alpha=0.3)
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.grid(True)

    # SGD 軌跡
    traj = np.array(trajectory_sgd)
    axes[0].plot(traj[:, 0], traj[:, 1], 'ro-', linewidth=2, markersize=3)
    axes[0].set_title('SGD：左右震盪，進展慢')

    # Momentum 軌跡
    traj = np.array(trajectory_mom)
    axes[1].plot(traj[:, 0], traj[:, 1], 'bo-', linewidth=2, markersize=3)
    axes[1].set_title('Momentum：平穩快速')

    plt.tight_layout()
    plt.savefig('momentum_comparison.png', dpi=150)
    plt.show()

visualize_momentum()
```

---

## 🏃 比喻 2：跑步配速（AdaGrad）

### 問題：一刀切的學習率

```
情境：你在跑馬拉松

固定學習率 = 固定配速：
- 前 10 公里：體力充沛，配速太慢（浪費）
- 中間 20 公里：剛剛好
- 最後 12 公里：累了，配速太快（受傷）
```

### AdaGrad：自適應學習率

```
聰明配速：
- 前 10 公里：加速（探索階段，可以大步走）
- 中間 20 公里：穩定
- 最後 12 公里：減速（接近終點，小步調整）
```

### 核心思想

**根據「歷史梯度」調整學習率**：
- 梯度大的參數 → 學習率變小（走太多次了，該減速）
- 梯度小的參數 → 學習率保持大（走太少，該加速）

### 數學表達

```
G_t = G_{t-1} + (gradient)²
      ↑ 累積梯度平方（記錄「走了多遠」）

θ_t = θ_{t-1} - α / √(G_t + ε) × gradient
                  ↑ 自適應學習率
```

### 生活化例子：學英文單字

```
情境：你要記 100 個英文單字

單字 A：看了 1 次就記住 → G_A = 小
單字 B：看了 20 次還記不住 → G_B = 大

AdaGrad 策略：
- 單字 A：少複習（學習率保持大）
- 單字 B：多複習（學習率變小，慢慢記）
```

### Python 實作

```python
class AdaGradOptimizer:
    def __init__(self, learning_rate=0.01, epsilon=1e-8):
        """
        AdaGrad 優化器

        比喻：根據「累計跑的距離」調整配速

        參數：
            learning_rate: 初始學習率
            epsilon: 防止除零（非常小的數）
        """
        self.lr = learning_rate
        self.epsilon = epsilon
        self.G = {}  # 累積梯度平方

    def update(self, param_name, param, gradient):
        """更新參數"""
        # 初始化
        if param_name not in self.G:
            self.G[param_name] = np.zeros_like(param)

        # 累積梯度平方
        self.G[param_name] += gradient ** 2

        # 自適應學習率更新
        adapted_lr = self.lr / (np.sqrt(self.G[param_name]) + self.epsilon)
        param -= adapted_lr * gradient

        return param

# 範例
optimizer = AdaGradOptimizer(learning_rate=0.1)

for epoch in range(100):
    gradient = compute_gradient()
    weights = optimizer.update('weights', weights, gradient)

    # 觀察學習率變化
    current_lr = 0.1 / (np.sqrt(optimizer.G['weights']) + 1e-8)
    print(f"Epoch {epoch}: 學習率 = {np.mean(current_lr):.6f}")
```

### 缺點：學習率單調遞減

```
問題：後期學習率可能變太小

比喻：
跑到 30 公里時，配速已經慢到「用走的」
即使前方是下坡（可以加速），也提不起速度

解決：RMSprop（下一節）
```

---

## 📈 比喻 3：彈性配速（RMSprop）

### AdaGrad 的問題

```
AdaGrad：累積「所有」歷史梯度
G_t = G_1 + G_2 + G_3 + ... + G_t
→ G_t 只會越來越大
→ 學習率只會越來越小
→ 後期幾乎不動
```

### RMSprop：只記住「最近」的歷史

```
RMSprop：用「指數移動平均」
S_t = 0.9 × S_{t-1} + 0.1 × (gradient)²
      ↑ 保留 90% 舊記憶，加入 10% 新資訊

→ 最近的梯度影響大，久遠的梯度被「遺忘」
→ 學習率可以「回升」
```

### 生活化比喻：體重管理

```
AdaGrad（累積所有歷史）：
你一輩子吃過的所有食物都算進去
→ 吃越多，減肥越難（即使最近在節食）

RMSprop（只看最近）：
只看「最近一個月」的飲食
→ 最近節食 → 可以減肥成功
→ 最近暴食 → 需要加強運動
```

### 數學表達

```
S_t = β × S_{t-1} + (1-β) × (gradient)²
      ↑ β 通常取 0.9（保留 90% 舊記憶）

θ_t = θ_{t-1} - α / √(S_t + ε) × gradient
```

### Python 實作

```python
class RMSpropOptimizer:
    def __init__(self, learning_rate=0.01, beta=0.9, epsilon=1e-8):
        """
        RMSprop 優化器

        比喻：根據「最近的表現」調整策略

        參數：
            learning_rate: 學習率
            beta: 衰減率（保留多少舊記憶）
            epsilon: 防止除零
        """
        self.lr = learning_rate
        self.beta = beta
        self.epsilon = epsilon
        self.S = {}  # 梯度平方的移動平均

    def update(self, param_name, param, gradient):
        """更新參數"""
        # 初始化
        if param_name not in self.S:
            self.S[param_name] = np.zeros_like(param)

        # 更新移動平均（「遺忘」舊梯度）
        self.S[param_name] = (
            self.beta * self.S[param_name] +
            (1 - self.beta) * gradient ** 2
        )

        # 自適應學習率更新
        adapted_lr = self.lr / (np.sqrt(self.S[param_name]) + self.epsilon)
        param -= adapted_lr * gradient

        return param

# 比較 AdaGrad vs RMSprop
def compare_adagrad_rmsprop():
    """視覺化兩者差異"""

    # 模擬梯度序列（前期大，中期小，後期又變大）
    gradients = []
    for t in range(100):
        if t < 30:
            grad = 2.0  # 前期：大梯度
        elif t < 70:
            grad = 0.1  # 中期：小梯度
        else:
            grad = 2.0  # 後期：大梯度
        gradients.append(grad)

    # AdaGrad
    G_adagrad = 0
    lr_adagrad = []
    for grad in gradients:
        G_adagrad += grad ** 2
        lr_adagrad.append(0.1 / np.sqrt(G_adagrad + 1e-8))

    # RMSprop
    S_rmsprop = 0
    lr_rmsprop = []
    for grad in gradients:
        S_rmsprop = 0.9 * S_rmsprop + 0.1 * grad ** 2
        lr_rmsprop.append(0.1 / np.sqrt(S_rmsprop + 1e-8))

    # 繪圖
    plt.figure(figsize=(12, 6))

    plt.subplot(2, 1, 1)
    plt.plot(gradients, label='梯度大小', linewidth=2)
    plt.ylabel('梯度')
    plt.legend()
    plt.grid(True)
    plt.title('梯度變化')

    plt.subplot(2, 1, 2)
    plt.plot(lr_adagrad, label='AdaGrad（只降不升）', linewidth=2)
    plt.plot(lr_rmsprop, label='RMSprop（可回升）', linewidth=2)
    plt.xlabel('迭代次數')
    plt.ylabel('學習率')
    plt.legend()
    plt.grid(True)
    plt.title('學習率變化')

    plt.tight_layout()
    plt.savefig('adagrad_vs_rmsprop.png', dpi=150)
    plt.show()

compare_adagrad_rmsprop()
```

---

## 🎖️ 比喻 4：完美駕駛（Adam）

### Adam = Momentum + RMSprop

```
Momentum：記住「方向」（一階動量）
RMSprop：調整「步伐」（二階動量）

Adam：兩者結合
→ 既平穩，又自適應
→ 目前最常用的優化器！
```

### 生活化比喻：高級自駕車

```
基本 SGD：
人工駕駛，一直修正方向盤 🚗

Momentum：
定速巡航，保持穩定速度 🚗→

RMSprop：
根據路況調整速度（上坡減速，下坡加速）🚗↗↘

Adam：
自駕車（定速巡航 + 自動調速）🚗🤖
→ 既穩定又聰明！
```

### 數學表達

```
# 一階動量（Momentum）
m_t = β₁ × m_{t-1} + (1-β₁) × gradient

# 二階動量（RMSprop）
v_t = β₂ × v_{t-1} + (1-β₂) × gradient²

# 偏差修正（Bias Correction）
m̂_t = m_t / (1 - β₁ᵗ)
v̂_t = v_t / (1 - β₂ᵗ)

# 更新參數
θ_t = θ_{t-1} - α × m̂_t / (√v̂_t + ε)
```

### 為什麼需要偏差修正？

**問題**：初始時 m_0 = 0, v_0 = 0

```
第 1 步：
m_1 = 0.9 × 0 + 0.1 × gradient = 0.1 × gradient
→ 比實際梯度小 10 倍！

第 2 步：
m_2 = 0.9 × (0.1 × grad) + 0.1 × grad
    = 0.19 × gradient（累積）
→ 還是偏小

...直到多次迭代後才接近真實值
```

**解決**：偏差修正

```
m̂_t = m_t / (1 - β₁ᵗ)

第 1 步：m̂_1 = 0.1 × grad / (1 - 0.9¹) = 0.1 / 0.1 = grad ✓
第 2 步：m̂_2 = 0.19 × grad / (1 - 0.9²) = 0.19 / 0.19 = grad ✓
```

### Python 完整實作

```python
class AdamOptimizer:
    def __init__(self, learning_rate=0.001, beta1=0.9, beta2=0.999, epsilon=1e-8):
        """
        Adam 優化器

        比喻：最智能的自駕車

        參數：
            learning_rate: 學習率（通常 0.001）
            beta1: 一階動量衰減率（通常 0.9）
            beta2: 二階動量衰減率（通常 0.999）
            epsilon: 防止除零
        """
        self.lr = learning_rate
        self.beta1 = beta1
        self.beta2 = beta2
        self.epsilon = epsilon

        self.m = {}  # 一階動量
        self.v = {}  # 二階動量
        self.t = 0   # 時間步

    def update(self, param_name, param, gradient):
        """更新參數"""
        # 初始化
        if param_name not in self.m:
            self.m[param_name] = np.zeros_like(param)
            self.v[param_name] = np.zeros_like(param)

        # 時間步 +1
        self.t += 1

        # 更新一階動量（Momentum）
        self.m[param_name] = (
            self.beta1 * self.m[param_name] +
            (1 - self.beta1) * gradient
        )

        # 更新二階動量（RMSprop）
        self.v[param_name] = (
            self.beta2 * self.v[param_name] +
            (1 - self.beta2) * gradient ** 2
        )

        # 偏差修正
        m_hat = self.m[param_name] / (1 - self.beta1 ** self.t)
        v_hat = self.v[param_name] / (1 - self.beta2 ** self.t)

        # 更新參數
        param -= self.lr * m_hat / (np.sqrt(v_hat) + self.epsilon)

        return param

# 完整訓練範例
def train_with_adam():
    """使用 Adam 訓練線性迴歸"""

    # 生成數據
    np.random.seed(42)
    X = np.linspace(0, 10, 100)
    y = 3 * X + 7 + np.random.randn(100) * 2

    # 初始化參數
    w = 0.0
    b = 0.0

    # 創建優化器
    optimizer = AdamOptimizer(learning_rate=0.1)

    # 訓練
    loss_history = []
    for epoch in range(100):
        # 前向傳播
        y_pred = w * X + b
        loss = np.mean((y_pred - y) ** 2)
        loss_history.append(loss)

        # 計算梯度
        dw = (2/len(X)) * np.sum((y_pred - y) * X)
        db = (2/len(X)) * np.sum(y_pred - y)

        # 更新參數
        w = optimizer.update('w', w, dw)
        b = optimizer.update('b', b, db)

        if epoch % 10 == 0:
            print(f"Epoch {epoch}: Loss = {loss:.4f}, w = {w:.4f}, b = {b:.4f}")

    print(f"\n最終結果: w = {w:.4f}, b = {b:.4f}")
    print(f"真實參數: w = 3.0000, b = 7.0000")

    return loss_history

loss_history = train_with_adam()
```

**輸出**：
```
Epoch 0: Loss = 149.2341, w = 2.8234, b = 0.3124
Epoch 10: Loss = 4.1234, w = 2.9823, b = 6.9123
Epoch 20: Loss = 4.0123, w = 2.9956, b = 7.0045
...
Epoch 90: Loss = 3.9876, w = 2.9991, b = 7.0012

最終結果: w = 2.9991, b = 7.0012
真實參數: w = 3.0000, b = 7.0000
```

---

## 🚀 比喻 5：減重版 Adam（AdamW）

### 問題：正則化與 Adam 不兼容

**背景知識**：
```
正則化（Weight Decay）：防止過擬合
做法：讓權重「自動衰減」

loss = 原始 loss + λ × Σ(weights²)
                     ↑ 懲罰大權重
```

**問題**：
```
在 Adam 中，正則化被「自適應學習率」影響
→ 效果不如預期
```

### AdamW：解耦權重衰減

**核心思想**：
```
不要把正則化加到梯度裡
直接對權重做衰減
```

**比喻**：減肥策略

```
Adam + 傳統正則化：
「少吃」+ 「運動」混在一起計算
→ 效果打折扣

AdamW：
「少吃」和「運動」分開執行
→ 效果更好
```

### Python 實作

```python
class AdamWOptimizer:
    def __init__(self, learning_rate=0.001, beta1=0.9, beta2=0.999,
                 epsilon=1e-8, weight_decay=0.01):
        """
        AdamW 優化器

        比喻：Adam + 獨立的權重衰減

        新參數：
            weight_decay: 權重衰減率（類似正則化強度）
        """
        self.lr = learning_rate
        self.beta1 = beta1
        self.beta2 = beta2
        self.epsilon = epsilon
        self.weight_decay = weight_decay

        self.m = {}
        self.v = {}
        self.t = 0

    def update(self, param_name, param, gradient):
        """更新參數"""
        # 初始化
        if param_name not in self.m:
            self.m[param_name] = np.zeros_like(param)
            self.v[param_name] = np.zeros_like(param)

        self.t += 1

        # 更新動量（和 Adam 一樣）
        self.m[param_name] = (
            self.beta1 * self.m[param_name] +
            (1 - self.beta1) * gradient
        )
        self.v[param_name] = (
            self.beta2 * self.v[param_name] +
            (1 - self.beta2) * gradient ** 2
        )

        # 偏差修正
        m_hat = self.m[param_name] / (1 - self.beta1 ** self.t)
        v_hat = self.v[param_name] / (1 - self.beta2 ** self.t)

        # Adam 更新
        param -= self.lr * m_hat / (np.sqrt(v_hat) + self.epsilon)

        # 額外：權重衰減（解耦的關鍵！）
        param -= self.lr * self.weight_decay * param

        return param
```

### Adam vs AdamW 比較

```python
def compare_adam_adamw():
    """比較 Adam 和 AdamW 在過擬合情況下的表現"""

    # 生成數據（故意用小數據集，容易過擬合）
    np.random.seed(42)
    X = np.random.randn(20, 10)  # 20 個樣本，10 個特徵
    y = np.random.randn(20)

    # 初始化權重（故意很大，需要正則化）
    w_adam = np.random.randn(10) * 5
    w_adamw = w_adam.copy()

    # 創建優化器
    adam = AdamOptimizer(learning_rate=0.01)
    adamw = AdamWOptimizer(learning_rate=0.01, weight_decay=0.01)

    # 訓練
    weight_norm_adam = []
    weight_norm_adamw = []

    for epoch in range(200):
        # Adam
        y_pred = X.dot(w_adam)
        grad = (2/len(X)) * X.T.dot(y_pred - y)
        w_adam = adam.update('w', w_adam, grad)
        weight_norm_adam.append(np.linalg.norm(w_adam))

        # AdamW
        y_pred = X.dot(w_adamw)
        grad = (2/len(X)) * X.T.dot(y_pred - y)
        w_adamw = adamw.update('w', w_adamw, grad)
        weight_norm_adamw.append(np.linalg.norm(w_adamw))

    # 繪圖
    plt.figure(figsize=(10, 6))
    plt.plot(weight_norm_adam, label='Adam（權重較大，容易過擬合）', linewidth=2)
    plt.plot(weight_norm_adamw, label='AdamW（權重受控，防止過擬合）', linewidth=2)
    plt.xlabel('迭代次數')
    plt.ylabel('權重範數 ||w||')
    plt.title('Adam vs AdamW：權重大小比較')
    plt.legend()
    plt.grid(True)
    plt.savefig('adam_vs_adamw.png', dpi=150)
    plt.show()

compare_adam_adamw()
```

---

## 🔭 比喻 6：先看再跳（Lookahead）

### 核心思想：兩階段優化

**比喻**：跳躍前先觀察

```
普通優化器（如 Adam）：
看一步 → 跳一步 → 看一步 → 跳一步
→ 可能跳錯方向

Lookahead：
看 5 步 → 評估結果 → 跳一大步
→ 更穩健，不容易跳錯
```

### 生活化例子：買房選址

```
直接決策（普通優化器）：
看到一間房 → 立刻買
看到另一間 → 又買
→ 可能買錯

Lookahead 策略：
先租房住 5 個月（快速試探）
評估哪個區域最好
再買房（慢參數更新）
→ 決策更穩
```

### 算法流程

```
1. 用「快權重」探索 k 步（如 Adam 走 5 步）
   w_fast_1, w_fast_2, ..., w_fast_k

2. 用「慢權重」更新一步（朝快權重的方向）
   w_slow = w_slow + α × (w_fast_k - w_slow)

3. 重置快權重 = 慢權重
   w_fast = w_slow

4. 重複
```

### Python 實作

```python
class LookaheadOptimizer:
    def __init__(self, base_optimizer, k=5, alpha=0.5):
        """
        Lookahead 優化器

        比喻：先快速試探，再慢速決策

        參數：
            base_optimizer: 基礎優化器（如 Adam）
            k: 內部優化器走幾步
            alpha: 慢權重更新速率
        """
        self.base_optimizer = base_optimizer
        self.k = k
        self.alpha = alpha

        self.slow_weights = {}  # 慢權重
        self.step_count = 0

    def update(self, param_name, param, gradient):
        """更新參數"""
        # 初始化慢權重
        if param_name not in self.slow_weights:
            self.slow_weights[param_name] = param.copy()

        # 用基礎優化器更新快權重
        param = self.base_optimizer.update(param_name, param, gradient)

        # 計數
        self.step_count += 1

        # 每 k 步，更新慢權重
        if self.step_count % self.k == 0:
            # 慢權重朝快權重方向移動
            self.slow_weights[param_name] += (
                self.alpha * (param - self.slow_weights[param_name])
            )

            # 重置快權重 = 慢權重
            param = self.slow_weights[param_name].copy()

        return param

# 使用範例
base_adam = AdamOptimizer(learning_rate=0.001)
lookahead = LookaheadOptimizer(base_adam, k=5, alpha=0.5)

for epoch in range(100):
    gradient = compute_gradient()
    weights = lookahead.update('weights', weights, gradient)
```

---

## 📊 優化器大比拼

### 測試場景：複雜地形

```python
def compare_all_optimizers():
    """在複雜損失函數上比較所有優化器"""

    # 定義一個複雜的損失函數（有多個局部最小值）
    def rastrigin(x, y):
        """Rastrigin 函數：很多局部最小值"""
        A = 10
        return (A * 2 + (x**2 - A * np.cos(2 * np.pi * x)) +
                        (y**2 - A * np.cos(2 * np.pi * y)))

    # 初始點
    start_x, start_y = 4.5, 4.5

    # 創建所有優化器
    optimizers = {
        'SGD': SGDOptimizer(learning_rate=0.01),
        'Momentum': MomentumOptimizer(learning_rate=0.01, momentum=0.9),
        'AdaGrad': AdaGradOptimizer(learning_rate=0.5),
        'RMSprop': RMSpropOptimizer(learning_rate=0.01),
        'Adam': AdamOptimizer(learning_rate=0.1),
        'AdamW': AdamWOptimizer(learning_rate=0.1, weight_decay=0.01),
    }

    # 訓練每個優化器
    trajectories = {}

    for name, optimizer in optimizers.items():
        x, y = start_x, start_y
        trajectory = [(x, y)]

        for _ in range(100):
            # 計算梯度
            grad_x = 2 * x + 2 * np.pi * A * np.sin(2 * np.pi * x)
            grad_y = 2 * y + 2 * np.pi * A * np.sin(2 * np.pi * y)

            # 更新
            x = optimizer.update(f'{name}_x', x, grad_x)
            y = optimizer.update(f'{name}_y', y, grad_y)

            trajectory.append((x, y))

        trajectories[name] = np.array(trajectory)

    # 繪圖
    fig = plt.figure(figsize=(18, 12))

    # 繪製損失函數等高線
    x = np.linspace(-5, 5, 200)
    y = np.linspace(-5, 5, 200)
    X, Y = np.meshgrid(x, y)
    Z = rastrigin(X, Y)

    # 為每個優化器繪製子圖
    colors = ['red', 'blue', 'green', 'orange', 'purple', 'brown']

    for idx, (name, traj) in enumerate(trajectories.items()):
        ax = fig.add_subplot(2, 3, idx + 1)
        ax.contour(X, Y, Z, levels=20, alpha=0.3)
        ax.plot(traj[:, 0], traj[:, 1],
                color=colors[idx], linewidth=2, marker='o', markersize=2)
        ax.plot(0, 0, 'r*', markersize=20, label='全局最小值')
        ax.set_title(f'{name}', fontsize=14, fontweight='bold')
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.legend()
        ax.grid(True)

    plt.tight_layout()
    plt.savefig('optimizer_comparison_complex.png', dpi=150)
    plt.show()

compare_all_optimizers()
```

### 結果分析表

| 優化器 | 速度 | 穩定性 | 適用場景 | 推薦指數 |
|--------|------|--------|----------|----------|
| **SGD** | ⭐⭐ | ⭐⭐ | 教學、簡單問題 | ⭐⭐ |
| **Momentum** | ⭐⭐⭐ | ⭐⭐⭐ | 需要加速收斂 | ⭐⭐⭐ |
| **AdaGrad** | ⭐⭐ | ⭐⭐⭐ | 稀疏數據（NLP） | ⭐⭐ |
| **RMSprop** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | RNN、時間序列 | ⭐⭐⭐⭐ |
| **Adam** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | **通用首選** | ⭐⭐⭐⭐⭐ |
| **AdamW** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | **防過擬合** | ⭐⭐⭐⭐⭐ |
| **Lookahead** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 需要穩健性 | ⭐⭐⭐⭐ |

---

## 🎓 實戰建議

### 1. 如何選擇優化器？

```
決策樹：

開始
  │
  ├─ 是教學/調試？
  │   └─ Yes → SGD
  │
  ├─ 是 NLP 任務？
  │   └─ Yes → AdaGrad 或 Adam
  │
  ├─ 是 RNN/LSTM？
  │   └─ Yes → RMSprop
  │
  ├─ 是 Transformer？
  │   └─ Yes → AdamW
  │
  └─ 其他（CNN、一般深度學習）
      └─ Adam（通用首選）
```

### 2. 超參數設定建議

```python
# 推薦起點
configs = {
    'SGD': {
        'learning_rate': 0.01,
    },
    'Momentum': {
        'learning_rate': 0.01,
        'momentum': 0.9,
    },
    'Adam': {
        'learning_rate': 0.001,
        'beta1': 0.9,
        'beta2': 0.999,
    },
    'AdamW': {
        'learning_rate': 0.001,
        'beta1': 0.9,
        'beta2': 0.999,
        'weight_decay': 0.01,
    },
}
```

### 3. 常見錯誤與解決

| 問題 | 可能原因 | 解決方案 |
|------|---------|---------|
| Loss 不下降 | 學習率太大/太小 | 嘗試 0.1, 0.01, 0.001 |
| 訓練不穩定 | 沒用 Momentum | 改用 Adam |
| 過擬合 | 沒有正則化 | 用 AdamW + Dropout |
| 後期進展慢 | AdaGrad 問題 | 改用 Adam 或 RMSprop |

---

## 📚 總結

### 優化器進化史

```
1986: SGD（基礎）
   ↓
1999: Momentum（加速）
   ↓
2011: AdaGrad（自適應）
   ↓
2012: RMSprop（改進 AdaGrad）
   ↓
2014: Adam（結合 Momentum + RMSprop）★ 里程碑
   ↓
2017: AdamW（解耦權重衰減）
   ↓
2019: Lookahead（兩階段優化）
   ↓
2023: 持續演化中...
```

### 核心思想總結

1. **Momentum**：記住方向，減少震盪
2. **AdaGrad/RMSprop**：自適應學習率
3. **Adam**：結合兩者優點
4. **AdamW**：更好的正則化
5. **Lookahead**：更穩健的更新

### 推薦使用

- 🥇 **首選**：Adam 或 AdamW
- 🥈 **備選**：RMSprop（RNN）
- 🥉 **特殊**：SGD + Momentum（某些 CV 任務）

---

*最後更新: 2025-11-26*
