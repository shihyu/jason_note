# 卷積神經網路（CNN）完整指南 - 用生活比喻理解

## 🎯 核心比喻：拼圖遊戲高手

想像你在玩一個 1000 片的拼圖：

**新手做法**（全連接神經網路）：
```
❌ 拿起一片，跟其他 999 片「全部」比對
❌ 累死了，效率超低
❌ 而且容易記錯（過擬合）
```

**高手做法**（卷積神經網路）：
```
✅ 先找「顏色相近」的區域（局部特徵）
✅ 再找「邊緣線條」（特徵提取）
✅ 最後組合成完整圖案（分層識別）
```

**這就是 CNN 的核心思想：局部特徵 + 分層識別！**

---

## 🔍 三大核心概念

### 1. 卷積（Convolution）= 特徵探測器

**比喻**：用印章在紙上蓋印

```
原始圖片               卷積核（印章）         特徵圖
┌───────┐              ┌───┐              ┌───────┐
│ 1 2 3 │              │1 0│              │檢測到 │
│ 4 5 6 │    ✕         │0 1│    =         │斜線！ │
│ 7 8 9 │              └───┘              └───────┘
└───────┘
```

**生活例子**：
- **找人臉**：印章形狀 = 眼睛、鼻子、嘴巴
- **找車子**：印章形狀 = 輪子、車窗
- **找貓咪**：印章形狀 = 尖耳朵、鬍鬚

### 2. 池化（Pooling）= 抓重點

**比喻**：看報紙只看標題

```
原始特徵圖            Max Pooling           簡化版
┌─────────┐           (取最大值)          ┌─────┐
│ 1  3  2  4 │                           │ 3  4 │
│ 5  6  7  8 │    →    取 2×2 區域    →   │ 9 12 │
│ 9 10 11 12 │         的最大值           └─────┘
└─────────┘
```

**好處**：
- ✅ 減少計算量（只看重點）
- ✅ 增加容錯性（位置偏移也能識別）
- ✅ 擴大視野（看到更大範圍）

### 3. 全連接層（Fully Connected）= 最終決策

**比喻**：法官綜合所有證據判案

```
特徵提取階段           全連接層             最終判斷
┌───────┐           ┌────────┐          ┌────┐
│特徵1: 鬍鬚│    →     │ 綜合分析 │    →     │ 貓 │
│特徵2: 尖耳│           │ 所有特徵 │          │ 95%│
│特徵3: 圓眼│           └────────┘          └────┘
└───────┘
```

---

## 🏗️ CNN 架構：蓋房子的流程

### 比喻：建築工地

```
原料檢查 → 打地基 → 砌牆 → 裝潢 → 驗收
(輸入)   (卷積1)  (卷積2) (卷積3) (全連接)
```

### 詳細流程

#### 第 1 步：原料檢查（輸入層）
```
工頭收到一張建築藍圖（圖片）
大小：28×28 像素（長×寬）
顏色：灰階（1 個通道）或彩色（3 個通道：RGB）
```

#### 第 2 步：打地基（第一層卷積）
```
使用 32 個不同的「印章」（卷積核）掃描藍圖
每個印章負責找一種特徵：
- 印章 1：找「水平線」
- 印章 2：找「垂直線」
- 印章 3：找「斜線」
- ...
- 印章 32：找「圓弧」

結果：產生 32 張「特徵地圖」
```

**代碼實作**：
```python
import numpy as np

def convolution_2d(image, kernel):
    """
    2D 卷積運算

    比喻：用印章在圖片上蓋印

    參數：
        image: 原始圖片 (H, W)
        kernel: 卷積核/印章 (K, K)

    返回：
        feature_map: 特徵圖
    """
    H, W = image.shape
    K = kernel.shape[0]

    # 輸出大小
    output_H = H - K + 1
    output_W = W - K + 1
    feature_map = np.zeros((output_H, output_W))

    # 滑動印章
    for i in range(output_H):
        for j in range(output_W):
            # 提取當前區域
            region = image[i:i+K, j:j+K]

            # 卷積運算（對應元素相乘再相加）
            feature_map[i, j] = np.sum(region * kernel)

    return feature_map

# 範例：檢測垂直邊緣
image = np.array([
    [0, 0, 0, 255, 255, 255, 0, 0],
    [0, 0, 0, 255, 255, 255, 0, 0],
    [0, 0, 0, 255, 255, 255, 0, 0],
    [0, 0, 0, 255, 255, 255, 0, 0],
])

# 垂直邊緣檢測器（印章）
vertical_kernel = np.array([
    [-1, 0, 1],
    [-1, 0, 1],
    [-1, 0, 1]
])

# 執行卷積
feature_map = convolution_2d(image, vertical_kernel)
print("檢測到的垂直邊緣：")
print(feature_map)
```

**輸出**：
```
檢測到的垂直邊緣：
[[   0.  765. -765.    0.]
 [   0.  765. -765.    0.]
 [   0.  765. -765.    0.]]
```

#### 第 3 步：簡化藍圖（池化層）
```
工頭說：「這些特徵太細了，給我抓重點！」

Max Pooling（取最大值）：
┌─────┐
│ 1 3 │  → 取最大值 = 3
│ 2 1 │
└─────┘

結果：特徵圖縮小一半（28×28 → 14×14）
```

**代碼實作**：
```python
def max_pooling_2d(feature_map, pool_size=2):
    """
    最大池化

    比喻：在每個小區域找最強信號

    參數：
        feature_map: 特徵圖 (H, W)
        pool_size: 池化窗口大小

    返回：
        pooled: 池化後的特徵圖
    """
    H, W = feature_map.shape
    output_H = H // pool_size
    output_W = W // pool_size
    pooled = np.zeros((output_H, output_W))

    for i in range(output_H):
        for j in range(output_W):
            # 提取池化區域
            region = feature_map[
                i*pool_size:(i+1)*pool_size,
                j*pool_size:(j+1)*pool_size
            ]
            # 取最大值
            pooled[i, j] = np.max(region)

    return pooled

# 測試
test_map = np.array([
    [1, 3, 2, 4],
    [5, 6, 7, 8],
    [9, 10, 11, 12],
    [13, 14, 15, 16]
])

pooled = max_pooling_2d(test_map, pool_size=2)
print("池化結果：")
print(pooled)
```

**輸出**：
```
池化結果：
[[ 6.  8.]
 [14. 16.]]
```

#### 第 4 步：重複處理（多層卷積）
```
第 2 層卷積：
- 在第 1 層的 32 張特徵圖上，再用 64 個印章
- 找「組合特徵」（例如：眼睛 = 兩個圓 + 一條線）

第 3 層卷積：
- 在第 2 層的 64 張特徵圖上，再用 128 個印章
- 找「高階特徵」（例如：臉 = 兩個眼睛 + 鼻子 + 嘴巴）
```

#### 第 5 步：驗收（全連接層）
```
建築師（全連接層）綜合所有特徵：
- 看到尖耳朵 + 鬍鬚 + 圓眼睛
- 判斷：這是「貓」！（90% 信心）
```

---

## 🎨 完整實作：手寫數字識別 CNN

### 架構設計

```
輸入: 28×28 灰階圖片（手寫數字）
    ↓
卷積層1: 32 個 3×3 卷積核 → 激活(ReLU) → 池化(2×2)
    ↓ (14×14×32)
卷積層2: 64 個 3×3 卷積核 → 激活(ReLU) → 池化(2×2)
    ↓ (7×7×64)
展平: 7×7×64 = 3136 個特徵
    ↓
全連接層1: 128 個神經元
    ↓
全連接層2: 10 個神經元（0-9 的機率）
    ↓
輸出: 預測數字
```

### 完整代碼

```python
import numpy as np

class SimpleCNN:
    def __init__(self):
        """
        簡單的 CNN 用於手寫數字識別

        比喻：訓練一個郵局分揀員
        """
        # 卷積層 1：32 個 3×3 濾波器
        self.conv1_filters = np.random.randn(32, 3, 3) * 0.1
        self.conv1_bias = np.zeros(32)

        # 卷積層 2：64 個 3×3 濾波器
        self.conv2_filters = np.random.randn(64, 32, 3, 3) * 0.1
        self.conv2_bias = np.zeros(64)

        # 全連接層 1
        self.fc1_weights = np.random.randn(3136, 128) * 0.01
        self.fc1_bias = np.zeros(128)

        # 全連接層 2（輸出層）
        self.fc2_weights = np.random.randn(128, 10) * 0.01
        self.fc2_bias = np.zeros(10)

    def relu(self, x):
        """ReLU 激活函數：保留正值，負值歸零"""
        return np.maximum(0, x)

    def relu_derivative(self, x):
        """ReLU 導數"""
        return (x > 0).astype(float)

    def conv2d(self, image, filters, bias):
        """
        2D 卷積運算（簡化版）

        比喻：用不同印章掃描圖片
        """
        n_filters = filters.shape[0]
        filter_size = filters.shape[-1]

        H, W = image.shape[-2:]
        output_H = H - filter_size + 1
        output_W = W - filter_size + 1

        output = np.zeros((n_filters, output_H, output_W))

        # 對每個濾波器
        for f in range(n_filters):
            # 滑動窗口
            for i in range(output_H):
                for j in range(output_W):
                    if len(image.shape) == 2:  # 單通道
                        region = image[i:i+filter_size, j:j+filter_size]
                        output[f, i, j] = np.sum(region * filters[f]) + bias[f]
                    else:  # 多通道
                        region = image[:, i:i+filter_size, j:j+filter_size]
                        output[f, i, j] = np.sum(region * filters[f]) + bias[f]

        return output

    def max_pooling(self, feature_maps, pool_size=2):
        """
        最大池化

        比喻：每個區域只保留最強信號
        """
        n_maps, H, W = feature_maps.shape
        output_H = H // pool_size
        output_W = W // pool_size

        output = np.zeros((n_maps, output_H, output_W))

        for m in range(n_maps):
            for i in range(output_H):
                for j in range(output_W):
                    region = feature_maps[
                        m,
                        i*pool_size:(i+1)*pool_size,
                        j*pool_size:(j+1)*pool_size
                    ]
                    output[m, i, j] = np.max(region)

        return output

    def softmax(self, x):
        """Softmax：轉換成機率分佈"""
        exp_x = np.exp(x - np.max(x))  # 防止溢出
        return exp_x / np.sum(exp_x)

    def forward(self, image):
        """
        前向傳播：識別流程

        比喻：
        1. 看圖片找特徵（卷積）
        2. 抓重點（池化）
        3. 重複多次（多層）
        4. 最終判斷（全連接）
        """
        # 輸入：28×28 圖片
        self.input = image

        # 卷積層 1
        self.conv1_out = self.conv2d(image, self.conv1_filters, self.conv1_bias)
        self.conv1_activated = self.relu(self.conv1_out)

        # 池化層 1：28×28 → 14×14
        self.pool1_out = self.max_pooling(self.conv1_activated, pool_size=2)

        # 卷積層 2
        self.conv2_out = self.conv2d(self.pool1_out, self.conv2_filters, self.conv2_bias)
        self.conv2_activated = self.relu(self.conv2_out)

        # 池化層 2：14×14 → 7×7
        self.pool2_out = self.max_pooling(self.conv2_activated, pool_size=2)

        # 展平：7×7×64 = 3136
        self.flattened = self.pool2_out.flatten()

        # 全連接層 1
        self.fc1_out = self.flattened.dot(self.fc1_weights) + self.fc1_bias
        self.fc1_activated = self.relu(self.fc1_out)

        # 全連接層 2（輸出層）
        self.fc2_out = self.fc1_activated.dot(self.fc2_weights) + self.fc2_bias
        self.output = self.softmax(self.fc2_out)

        return self.output

    def predict(self, image):
        """
        預測數字

        比喻：給郵局員工一張信件，讓他判斷是幾號信箱
        """
        probabilities = self.forward(image)
        return np.argmax(probabilities)

# 測試
if __name__ == "__main__":
    # 創建一個簡單的 "7" 字形圖案
    test_image = np.zeros((28, 28))
    test_image[5, 5:23] = 1  # 頂部橫線
    test_image[5:25, 20] = 1  # 右側豎線

    # 創建 CNN
    cnn = SimpleCNN()

    # 預測
    prediction = cnn.predict(test_image)
    print(f"CNN 預測這是數字: {prediction}")

    # 查看各數字的機率
    probs = cnn.forward(test_image)
    print("\n各數字的信心度：")
    for i, prob in enumerate(probs):
        print(f"數字 {i}: {prob*100:.2f}%")
```

---

## 🔬 深入理解：為什麼 CNN 這麼強？

### 優勢 1：參數共享（省記憶體）

**比喻**：印章可重複使用

```
全連接網路：
每個位置都要記住「這裡有沒有貓」
參數量：28×28×1000 = 784,000 個參數 😱

CNN：
只需要一個「貓臉偵測器」印章，到處蓋
參數量：3×3×32 = 288 個參數 😊

省了：784,000 / 288 ≈ 2700 倍！
```

### 優勢 2：平移不變性（容錯能力強）

**比喻**：無論貓在照片左邊還是右邊，都能認出

```
情況 1：貓在左上角
情況 2：貓在右下角

全連接網路：「這是兩張完全不同的圖！」❌
CNN：「都有貓臉特徵，是同一隻貓！」✅
```

### 優勢 3：層次化特徵（由簡到繁）

**比喻**：學習中文字

```
第 1 層：認識筆劃（橫、豎、撇、捺）
第 2 層：組合部首（木、火、水、土）
第 3 層：認識完整字（森、焱、淼、圭）

同理：
第 1 層：邊緣、線條
第 2 層：眼睛、鼻子、嘴巴
第 3 層：完整的臉
```

---

## 🎮 實戰案例：貓狗分類器

### 問題描述

給定一張圖片，判斷是貓還是狗。

### 數據準備

```python
# 假設我們有 1000 張貓的圖片，1000 張狗的圖片
# 每張圖片大小：64×64×3（RGB 彩色圖）

import numpy as np
from PIL import Image

def load_images(folder, label, num_images=1000):
    """
    載入圖片

    比喻：收集訓練樣本
    """
    images = []
    labels = []

    for i in range(num_images):
        # 載入圖片
        img_path = f"{folder}/image_{i}.jpg"
        img = Image.open(img_path)
        img = img.resize((64, 64))  # 統一大小

        # 轉換成陣列並正規化
        img_array = np.array(img) / 255.0  # 0-1 範圍

        images.append(img_array)
        labels.append(label)  # 0=貓, 1=狗

    return np.array(images), np.array(labels)

# 載入數據
cat_images, cat_labels = load_images("data/cats", label=0)
dog_images, dog_labels = load_images("data/dogs", label=1)

# 合併並打亂
all_images = np.concatenate([cat_images, dog_images])
all_labels = np.concatenate([cat_labels, dog_labels])

# 打亂數據
shuffle_idx = np.random.permutation(len(all_images))
all_images = all_images[shuffle_idx]
all_labels = all_labels[shuffle_idx]
```

### CNN 架構（使用 PyTorch 風格）

```python
class CatDogClassifier:
    """
    貓狗分類器

    比喻：訓練寵物識別專家
    """
    def __init__(self):
        # 卷積層 1：找基本特徵（邊緣、顏色）
        self.conv1 = Conv2D(input_channels=3, output_channels=32, kernel_size=3)

        # 卷積層 2：找組合特徵（眼睛、鼻子）
        self.conv2 = Conv2D(input_channels=32, output_channels=64, kernel_size=3)

        # 卷積層 3：找高階特徵（臉型、身體）
        self.conv3 = Conv2D(input_channels=64, output_channels=128, kernel_size=3)

        # 全連接層：最終判斷
        self.fc1 = FullyConnected(input_size=128*6*6, output_size=256)
        self.fc2 = FullyConnected(input_size=256, output_size=2)  # 2 類：貓、狗

    def forward(self, image):
        """
        前向傳播：識別流程

        image: 64×64×3 的貓或狗圖片
        """
        # 第 1 層：找基本特徵
        x = self.conv1(image)      # 64×64×3 → 62×62×32
        x = relu(x)
        x = max_pool(x, size=2)    # 62×62×32 → 31×31×32

        # 第 2 層：找組合特徵
        x = self.conv2(x)          # 31×31×32 → 29×29×64
        x = relu(x)
        x = max_pool(x, size=2)    # 29×29×64 → 14×14×64

        # 第 3 層：找高階特徵
        x = self.conv3(x)          # 14×14×64 → 12×12×128
        x = relu(x)
        x = max_pool(x, size=2)    # 12×12×128 → 6×6×128

        # 展平
        x = flatten(x)             # 6×6×128 = 4608

        # 全連接層
        x = self.fc1(x)            # 4608 → 256
        x = relu(x)
        x = dropout(x, rate=0.5)   # 防止過擬合

        x = self.fc2(x)            # 256 → 2
        output = softmax(x)        # 轉換成機率 [P(貓), P(狗)]

        return output

    def predict(self, image):
        """預測是貓還是狗"""
        probs = self.forward(image)
        if probs[0] > probs[1]:
            return "貓", probs[0]
        else:
            return "狗", probs[1]

# 使用範例
classifier = CatDogClassifier()

# 測試一張新圖片
test_image = load_image("test.jpg")
animal, confidence = classifier.predict(test_image)
print(f"這是：{animal}（信心度：{confidence*100:.1f}%）")
```

**輸出範例**：
```
這是：貓（信心度：87.3%）
```

---

## 🧪 進階技巧

### 技巧 1：數據增強（Data Augmentation）

**比喻**：用不同角度拍照練習

```python
def augment_image(image):
    """
    數據增強：製造更多訓練樣本

    比喻：
    - 原本只有 100 張貓照片
    - 透過翻轉、旋轉、縮放，變成 500 張
    """
    augmented = []

    # 原始圖片
    augmented.append(image)

    # 水平翻轉（鏡像）
    augmented.append(np.fliplr(image))

    # 旋轉 15 度
    augmented.append(rotate(image, angle=15))

    # 隨機裁切
    augmented.append(random_crop(image, size=0.9))

    # 調整亮度
    augmented.append(adjust_brightness(image, factor=1.2))

    return augmented
```

### 技巧 2：遷移學習（Transfer Learning）

**比喻**：站在巨人的肩膀上

```
情境：你要訓練一個「識別台灣特有種鳥類」的模型

笨方法：
從零開始訓練 → 需要 10 萬張鳥類照片 😱

聰明方法：
1. 下載「已經會認 1000 種動物的模型」（如 ResNet）
2. 只重新訓練「最後一層」（改成台灣 20 種鳥類）
3. 只需要 1000 張照片！😊
```

**代碼**：
```python
def transfer_learning():
    """遷移學習範例"""
    # 載入預訓練模型（已經學會識別 1000 種物品）
    pretrained_model = load_pretrained_resnet50()

    # 凍結前面的層（不訓練）
    for layer in pretrained_model.layers[:-1]:
        layer.trainable = False

    # 只替換最後一層
    pretrained_model.layers[-1] = FullyConnected(
        input_size=2048,
        output_size=20  # 改成 20 種台灣鳥類
    )

    # 只訓練最後一層
    train(pretrained_model, taiwan_bird_data)
```

### 技巧 3：批次正規化（Batch Normalization）

**比喻**：標準化考試成績

```
問題：
- 班級 A 平均 60 分（題目難）
- 班級 B 平均 90 分（題目簡單）
→ 無法公平比較！

解決：
標準化成「Z 分數」
→ 每班平均 0，標準差 1
→ 可以公平比較了！

CNN 中：
每層輸出範圍不同 → 難以訓練
批次正規化 → 每層標準化 → 訓練更穩定
```

**代碼**：
```python
def batch_normalization(x, epsilon=1e-5):
    """
    批次正規化

    比喻：把每批數據調整到相同尺度
    """
    # 計算平均值和標準差
    mean = np.mean(x, axis=0)
    std = np.std(x, axis=0)

    # 標準化
    x_normalized = (x - mean) / (std + epsilon)

    # 可學習的縮放和平移參數
    gamma = 1.0  # 縮放
    beta = 0.0   # 平移

    return gamma * x_normalized + beta
```

---

## 📊 常見 CNN 架構

### 1. LeNet-5（1998）- 始祖

```
比喻：自行車（簡單但有效）

結構：
輸入 → Conv → Pool → Conv → Pool → FC → FC → 輸出
```

### 2. AlexNet（2012）- 深度學習崛起

```
比喻：摩托車（更快更強）

創新：
- 使用 ReLU 激活函數
- 使用 Dropout 防止過擬合
- 使用 GPU 加速訓練
```

### 3. VGGNet（2014）- 更深的網路

```
比喻：汽車（穩定可靠）

特點：
- 使用很多 3×3 小卷積核
- 網路很深（16-19 層）
- 結構簡單規律
```

### 4. ResNet（2015）- 殘差連接

```
比喻：高速公路（有快速通道）

創新：殘差連接（Skip Connection）

普通網路：
x → 層1 → 層2 → 層3 → 輸出

ResNet：
x → 層1 → 層2 → 層3 → 輸出
 └─────────────────────┘
     (快速通道)

好處：可以訓練超深網路（100+ 層）
```

**代碼**：
```python
def residual_block(x):
    """
    殘差塊

    比喻：高速公路的快速通道
    """
    # 保存輸入（快速通道）
    shortcut = x

    # 主要路徑
    x = conv2d(x, filters=64, kernel_size=3)
    x = batch_norm(x)
    x = relu(x)

    x = conv2d(x, filters=64, kernel_size=3)
    x = batch_norm(x)

    # 合併（快速通道 + 主要路徑）
    x = x + shortcut
    x = relu(x)

    return x
```

### 5. MobileNet（2017）- 輕量化

```
比喻：電動滑板車（省電高效）

特點：
- 專為手機設計
- 參數少、速度快
- 適合邊緣設備
```

---

## 🎯 實務建議

### 1. 選擇合適的架構

| 任務 | 推薦架構 | 原因 |
|------|---------|------|
| 手寫數字識別 | LeNet | 簡單任務，小模型足夠 |
| 物體分類 | ResNet-50 | 平衡效果與速度 |
| 人臉識別 | FaceNet | 專門優化 |
| 手機應用 | MobileNet | 省資源 |
| 高精度需求 | EfficientNet | 效果最佳 |

### 2. 超參數調優

```python
# 推薦起點
config = {
    'learning_rate': 0.001,
    'batch_size': 32,
    'epochs': 50,
    'optimizer': 'Adam',
    'dropout_rate': 0.5
}
```

### 3. 常見錯誤與解決

| 問題 | 原因 | 解決方案 |
|------|------|----------|
| 訓練準確率低 | 模型太簡單 | 加深網路、增加參數 |
| 測試準確率低 | 過擬合 | Dropout、數據增強 |
| 訓練很慢 | 模型太大 | 減少參數、用更小的模型 |
| Loss 不下降 | 學習率不對 | 嘗試 0.01, 0.001, 0.0001 |

---

## 📚 總結

### CNN 三大核心

1. **卷積**：用「印章」找特徵
2. **池化**：抓重點、降維
3. **全連接**：綜合判斷

### 為什麼 CNN 強大？

- ✅ 參數少（參數共享）
- ✅ 容錯強（平移不變性）
- ✅ 層次化（由簡到繁）

### 下一步學習

- **目標檢測**：YOLO、Faster R-CNN（找出圖片中所有物體）
- **語義分割**：U-Net、FCN（像素級分類）
- **生成對抗網路**：GAN（生成新圖片）
- **注意力機制**：Vision Transformer（用 Transformer 做視覺）

---

*最後更新: 2025-11-26*
