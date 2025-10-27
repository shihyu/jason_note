# MobileCLIP 完整學習指南

> **文件更新日期**：2025-10-27  
> **適用對象**：想使用 MobileCLIP 開發商品搜尋應用的開發者

---

## 目錄

1. [MobileCLIP 簡介](#1-mobileclip-簡介)
2. [為什麼 Python 訓練能在 iOS 執行](#2-為什麼-python-訓練能在-ios-執行)
3. [實際應用：商品拍照搜尋](#3-實際應用商品拍照搜尋)
4. [模型下載與安裝](#4-模型下載與安裝)
5. [MobileCLIP 參數詳解](#5-mobileclip-參數詳解)
6. [常用應用場景](#6-常用應用場景)
7. [完整程式碼範例](#7-完整程式碼範例)
8. [效能優化建議](#8-效能優化建議)

---

## 1. MobileCLIP 簡介

### 1.1 什麼是 MobileCLIP？

MobileCLIP 是 Apple 開發的**輕量級圖像-文字配對模型**，專門為行動裝置優化。它可以：

- **連接圖像與文字**：將圖片和文字描述映射到同一個 512 維的向量空間
- **零樣本分類**：無需訓練就能識別未見過的物體
- **高效運行**：在手機上延遲只有 1.5-15ms

### 1.2 核心特性

| 特性 | 說明 |
|------|------|
| **速度** | 比 OpenAI CLIP 快 2.3-4.8 倍 |
| **體積** | 參數量 50-150M（比標準 CLIP 小 2-3 倍）|
| **精準度** | ImageNet 零樣本準確率達 77.2% |
| **平台** | 支援 iOS、Android、Python |

### 1.3 實際應用場景

```
用途範例：
✓ 商品拍照搜尋（本文重點）
✓ 相簿智慧搜尋
✓ AR 購物助手
✓ 即時物體識別
✓ 圖片去重
```

---

## 2. 為什麼 Python 訓練能在 iOS 執行

### 2.1 技術架構

```
【開發階段】               【部署階段】
Python (PyTorch)    →     iOS (Core ML)
    ↓                         ↓
訓練模型               →     推論執行
(需要GPU集群)             (手機CPU/GPU)
    ↓                         ↓
.pt 檔案              →     .mlmodelc 檔案
(PyTorch格式)             (Core ML格式)
```

### 2.2 轉換流程

#### 步驟 1：Python 訓練（離線）
```python
# 使用 PyTorch 訓練
import mobileclip
model = mobileclip.create_model_and_transforms('mobileclip_s0')
# 訓練過程...
torch.save(model.state_dict(), 'mobileclip_s0.pt')
```

#### 步驟 2：模型轉換
```python
# 使用 coremltools 轉換
import coremltools as ct

# 轉換為 Core ML 格式
coreml_model = ct.convert(
    pytorch_model,
    inputs=[ct.ImageType(shape=(1, 3, 224, 224))]
)
coreml_model.save('MobileCLIP.mlmodelc')
```

#### 步驟 3：iOS 部署（線上）
```swift
// Swift 程式碼
import CoreML

let model = try MobileCLIP()
let prediction = try model.prediction(image: imageBuffer)
```

### 2.3 為什麼要分離 TextEncoder 和 ImageEncoder？

**記憶體優化策略**：

```
情境：商品資料庫有 10,000 個商品

【傳統做法】（浪費）
每次搜尋都重新計算：
- 10,000 張圖片 × ImageEncoder = 耗時
- 用戶輸入文字 × TextEncoder = 耗時

【MobileCLIP 做法】（高效）
預先計算：
- 10,000 張圖片 → 計算一次 → 存入資料庫
搜尋時：
- 用戶文字 → 即時計算（只需 1.6ms）
- 與預存的圖片向量比對（< 1秒）
```

**實際效能**：
- 搜尋 10,000 張照片：< 1 秒
- 即時搜尋體驗！

---

## 3. 實際應用：商品拍照搜尋

### 3.1 需求分析

**場景描述**：
1. 店員拍攝商品照片，標記價格和說明
2. 顧客用手機拍攝商品
3. 系統自動找到對應商品資訊

### 3.2 搜尋結果處理

#### 方案 A：單一最佳結果（推薦）
```python
def search_single_best(query_image, products, threshold=0.8):
    """
    回傳最相似的一個商品
    
    Args:
        query_image: 用戶拍攝的照片
        products: 商品資料庫
        threshold: 最低相似度門檻 (0-1)
    
    Returns:
        最相似商品或 None
    """
    similarities = calculate_similarity(query_image, products)
    best_match = max(similarities, key=lambda x: x.score)
    
    if best_match.score >= threshold:
        return {
            'product_id': best_match.id,
            'name': best_match.name,
            'price': best_match.price,
            'confidence': f"{best_match.score * 100:.1f}%",
            'description': best_match.description
        }
    else:
        return None  # 找不到相似商品
```

#### 方案 B：Top-K 結果
```python
def search_top_k(query_image, products, k=3, threshold=0.75):
    """
    回傳前 K 個最相似商品
    
    Args:
        k: 回傳幾個結果
        threshold: 最低相似度門檻
    """
    similarities = calculate_similarity(query_image, products)
    
    # 排序並篩選
    results = sorted(similarities, key=lambda x: x.score, reverse=True)
    results = [r for r in results if r.score >= threshold]
    results = results[:k]
    
    return results
```

### 3.3 相似商品去重

**問題**：同一商品多張照片會重複出現

**解決方案**：
```python
def deduplicate_results(results):
    """
    根據 product_id 去重
    """
    seen_ids = set()
    unique_results = []
    
    for result in results:
        if result.product_id not in seen_ids:
            unique_results.append(result)
            seen_ids.add(result.product_id)
    
    return unique_results
```

### 3.4 UI/UX 設計建議

```
┌─────────────────────────────┐
│  [返回]    搜尋結果          │
├─────────────────────────────┤
│                              │
│     [商品圖片]               │
│                              │
├─────────────────────────────┤
│  Nike 氣墊運動鞋             │
│  NT$ 3,200                   │
│                              │
│  匹配度：★★★★★ 95%         │
│                              │
│  說明：黑色經典款...         │
├─────────────────────────────┤
│  [查看詳情]  [查看更多相似]  │
└─────────────────────────────┘
```

### 3.5 完整搜尋系統

```python
class ProductSearchSystem:
    def __init__(self, model_path):
        # 載入模型
        self.model, _, self.preprocess = mobileclip.create_model_and_transforms(
            'mobileclip_s2',
            pretrained=model_path
        )
        self.tokenizer = mobileclip.get_tokenizer('mobileclip_s2')
        
        # 預先計算所有商品的圖片向量
        self.product_embeddings = {}
        
    def index_products(self, products):
        """
        預先計算商品向量（只需執行一次）
        """
        for product in products:
            image = self.preprocess(product.image).unsqueeze(0)
            with torch.no_grad():
                embedding = self.model.encode_image(image)
                embedding /= embedding.norm(dim=-1, keepdim=True)
            
            self.product_embeddings[product.id] = {
                'embedding': embedding,
                'product': product
            }
    
    def search(self, query_image=None, query_text=None, 
               max_results=1, min_similarity=0.75):
        """
        混合搜尋：支援圖片或文字
        """
        # 計算查詢向量
        if query_image:
            image = self.preprocess(query_image).unsqueeze(0)
            query_embedding = self.model.encode_image(image)
        elif query_text:
            text = self.tokenizer([query_text])
            query_embedding = self.model.encode_text(text)
        else:
            raise ValueError("需要提供圖片或文字")
        
        query_embedding /= query_embedding.norm(dim=-1, keepdim=True)
        
        # 計算相似度
        results = []
        for product_id, data in self.product_embeddings.items():
            similarity = (query_embedding @ data['embedding'].T).item()
            
            if similarity >= min_similarity:
                results.append({
                    'product': data['product'],
                    'similarity': similarity
                })
        
        # 排序
        results.sort(key=lambda x: x['similarity'], reverse=True)
        
        # 去重
        results = self._deduplicate(results)
        
        return results[:max_results]
    
    def _deduplicate(self, results):
        """去除重複商品"""
        seen = set()
        unique = []
        for r in results:
            pid = r['product'].id
            if pid not in seen:
                unique.append(r)
                seen.add(pid)
        return unique
```

---

## 4. 模型下載與安裝

### 4.1 環境安裝

```bash
# 創建虛擬環境
conda create -n clipenv python=3.10
conda activate clipenv

# 安裝 MobileCLIP
git clone https://github.com/apple/ml-mobileclip.git
cd ml-mobileclip
pip install -e .
```

### 4.2 下載模型

#### 方法 1：使用官方腳本（推薦）
```bash
# 自動下載所有模型到 checkpoints/ 目錄
source get_pretrained_models.sh
```

#### 方法 2：從 HuggingFace 下載
```bash
# 安裝 HuggingFace CLI
pip install huggingface_hub

# 下載單個模型
hf download apple/MobileCLIP-S2

# 下載所有模型
for model in S0 S1 S2 B B-LT; do
    hf download apple/MobileCLIP-$model
done
```

#### 方法 3：直接下載連結
- [MobileCLIP-S0](https://docs-assets.developer.apple.com/ml-research/datasets/mobileclip/mobileclip_s0.pt) (11.4M)
- [MobileCLIP-S1](https://docs-assets.developer.apple.com/ml-research/datasets/mobileclip/mobileclip_s1.pt) (21.5M)
- [MobileCLIP-S2](https://docs-assets.developer.apple.com/ml-research/datasets/mobileclip/mobileclip_s2.pt) (35.7M)
- [MobileCLIP-B](https://docs-assets.developer.apple.com/ml-research/datasets/mobileclip/mobileclip_b.pt) (86.3M)
- [MobileCLIP-B-LT](https://docs-assets.developer.apple.com/ml-research/datasets/mobileclip/mobileclip_blt.pt) (86.3M)

### 4.3 模型選擇指南

| 模型 | 參數量 | 延遲 | ImageNet準確率 | 適用場景 |
|------|--------|------|----------------|----------|
| **S0** | 54M | 1.5+1.6ms | 67.8% | 快速原型、測試 |
| **S1** | 64M | 2.5+1.9ms | 70.7% | 輕量應用 |
| **S2** | 78M | 3.6+2.1ms | 73.4% | **推薦**平衡效能 |
| **B** | 129M | 10.4+3.3ms | 76.8% | 高精準需求 |
| **B-LT** | 129M | 10.4+3.3ms | 77.2% | **最高精準度** |

**建議**：
- 開發測試：用 **S2**（快速迭代）
- 正式產品：用 **B-LT**（最佳效果）

---

## 5. MobileCLIP 參數詳解

### 5.1 模型初始化參數

```python
import mobileclip

# 基本載入
model, _, preprocess = mobileclip.create_model_and_transforms(
    model_name='mobileclip_s2',           # 模型選擇
    pretrained='/path/to/mobileclip_s2.pt' # 模型路徑
)

# MobileCLIP2 需要額外參數
import open_clip

model_kwargs = {}
if model_name in ['MobileCLIP2-S0', 'MobileCLIP2-S2', 'MobileCLIP2-B']:
    model_kwargs = {
        "image_mean": (0, 0, 0),  # 圖片均值
        "image_std": (1, 1, 1)     # 圖片標準差
    }

model, _, preprocess = open_clip.create_model_and_transforms(
    model_name,
    pretrained=model_path,
    **model_kwargs
)
```

### 5.2 圖片預處理參數

預處理流程自動包含：
```python
# 內建的 preprocess 函數執行：
# 1. Resize: 調整到 224x224
# 2. Center Crop: 中心裁剪
# 3. ToTensor: 轉為張量
# 4. Normalize: 標準化

# 使用方式
from PIL import Image
image = Image.open('product.jpg').convert('RGB')
image_tensor = preprocess(image).unsqueeze(0)  # 增加 batch 維度
```

**手動自定義預處理**：
```python
from torchvision import transforms

custom_preprocess = transforms.Compose([
    transforms.Resize(256),              # 調整大小
    transforms.CenterCrop(224),          # 中心裁剪
    transforms.ToTensor(),               # 轉張量
    transforms.Normalize(                # 標準化
        mean=[0.48145466, 0.4578275, 0.40821073],
        std=[0.26862954, 0.26130258, 0.27577711]
    )
])
```

### 5.3 推論參數

```python
import torch

# 基本推論
with torch.no_grad():                    # 關閉梯度計算（加速）
    with torch.cuda.amp.autocast():      # 混合精度（可選）
        # 圖片編碼
        image_features = model.encode_image(image_tensor)
        
        # 文字編碼
        text_features = model.encode_text(text_tokens)
        
        # 特徵正規化（重要！）
        image_features /= image_features.norm(dim=-1, keepdim=True)
        text_features /= text_features.norm(dim=-1, keepdim=True)
        
        # 計算相似度
        similarity = (100.0 * image_features @ text_features.T).softmax(dim=-1)
```

**參數說明**：
- `torch.no_grad()`：不計算梯度，節省記憶體和時間
- `torch.cuda.amp.autocast()`：自動混合精度，加速運算（需要 GPU）
- `100.0 *`：溫度參數，控制 softmax 的銳利度
- `.softmax(dim=-1)`：將相似度轉為機率分佈

### 5.4 溫度參數（Temperature）調整

```python
# 溫度參數影響相似度的銳利度
temperature = 100.0  # 預設值

# 高溫度 (> 100)：分佈更平滑，差異較小
# 低溫度 (< 100)：分佈更尖銳，差異更明顯

similarity = (temperature * image_features @ text_features.T).softmax(dim=-1)
```

**實驗建議**：
```python
# 不同場景的溫度建議
temperatures = {
    '商品搜尋': 100.0,      # 預設，平衡
    '精確匹配': 50.0,       # 更嚴格
    '模糊搜尋': 150.0,      # 更寬鬆
}
```

### 5.5 相似度閾值設定

```python
class SearchConfig:
    """搜尋配置"""
    
    # 相似度閾值（0-1）
    HIGH_CONFIDENCE = 0.85    # 高信心
    MEDIUM_CONFIDENCE = 0.75  # 中信心
    LOW_CONFIDENCE = 0.60     # 低信心
    
    # Top-K 設定
    MAX_RESULTS = 5           # 最多返回結果
    
    # 去重設定
    ENABLE_DEDUP = True       # 啟用去重

# 使用範例
def search_with_config(query, config):
    results = calculate_similarity(query)
    
    # 根據信心度篩選
    if config.use_high_threshold:
        results = [r for r in results if r.score >= config.HIGH_CONFIDENCE]
    
    return results[:config.MAX_RESULTS]
```

### 5.6 批次處理參數

```python
def batch_encode_images(images, batch_size=32):
    """
    批次處理圖片，提高效率
    
    Args:
        images: 圖片列表
        batch_size: 每批處理數量
    """
    all_features = []
    
    for i in range(0, len(images), batch_size):
        batch = images[i:i+batch_size]
        
        # 批次預處理
        batch_tensors = torch.stack([preprocess(img) for img in batch])
        
        with torch.no_grad():
            features = model.encode_image(batch_tensors)
            features /= features.norm(dim=-1, keepdim=True)
            all_features.append(features)
    
    return torch.cat(all_features, dim=0)
```

---

## 6. 常用應用場景

### 6.1 零樣本圖片分類

```python
from PIL import Image
import mobileclip
import torch

# 載入模型
model, _, preprocess = mobileclip.create_model_and_transforms(
    'mobileclip_s2',
    pretrained='checkpoints/mobileclip_s2.pt'
)
tokenizer = mobileclip.get_tokenizer('mobileclip_s2')

# 準備圖片
image = Image.open('product.jpg').convert('RGB')
image_input = preprocess(image).unsqueeze(0)

# 準備候選標籤
labels = ["手機", "筆記型電腦", "平板", "耳機", "相機"]
text_inputs = tokenizer(labels)

# 推論
with torch.no_grad():
    image_features = model.encode_image(image_input)
    text_features = model.encode_text(text_inputs)
    
    # 正規化
    image_features /= image_features.norm(dim=-1, keepdim=True)
    text_features /= text_features.norm(dim=-1, keepdim=True)
    
    # 計算相似度
    similarity = (100.0 * image_features @ text_features.T).softmax(dim=-1)

# 顯示結果
for label, score in zip(labels, similarity[0]):
    print(f"{label}: {score.item()*100:.2f}%")

# 輸出範例：
# 手機: 85.32%
# 筆記型電腦: 8.45%
# 平板: 4.23%
# 耳機: 1.50%
# 相機: 0.50%
```

### 6.2 圖片相似度搜尋

```python
def find_similar_images(query_image, image_database, top_k=5):
    """
    在圖片資料庫中找出最相似的圖片
    
    Args:
        query_image: 查詢圖片
        image_database: 圖片資料庫（已預計算向量）
        top_k: 返回前 K 個結果
    """
    # 編碼查詢圖片
    query_tensor = preprocess(query_image).unsqueeze(0)
    with torch.no_grad():
        query_features = model.encode_image(query_tensor)
        query_features /= query_features.norm(dim=-1, keepdim=True)
    
    # 計算與資料庫中所有圖片的相似度
    similarities = []
    for img_id, img_features in image_database.items():
        similarity = (query_features @ img_features.T).item()
        similarities.append((img_id, similarity))
    
    # 排序並返回 top-k
    similarities.sort(key=lambda x: x[1], reverse=True)
    return similarities[:top_k]

# 使用範例
similar_images = find_similar_images(
    query_image=Image.open('query.jpg'),
    image_database=precomputed_vectors,
    top_k=5
)

for img_id, score in similar_images:
    print(f"圖片 {img_id}: 相似度 {score*100:.1f}%")
```

### 6.3 文字搜尋圖片

```python
def text_to_image_search(query_text, image_database, threshold=0.7):
    """
    用文字描述搜尋圖片
    
    Args:
        query_text: 文字描述
        image_database: 圖片資料庫
        threshold: 相似度閾值
    """
    # 編碼查詢文字
    text_tokens = tokenizer([query_text])
    with torch.no_grad():
        text_features = model.encode_text(text_tokens)
        text_features /= text_features.norm(dim=-1, keepdim=True)
    
    # 搜尋匹配圖片
    results = []
    for img_id, img_features in image_database.items():
        similarity = (text_features @ img_features.T).item()
        if similarity >= threshold:
            results.append({
                'id': img_id,
                'similarity': similarity
            })
    
    results.sort(key=lambda x: x['similarity'], reverse=True)
    return results

# 使用範例
results = text_to_image_search(
    query_text="一雙紅色的運動鞋",
    image_database=product_vectors,
    threshold=0.7
)

for result in results[:5]:
    print(f"商品 {result['id']}: {result['similarity']*100:.1f}%")
```

### 6.4 圖片去重

```python
def detect_duplicates(images, similarity_threshold=0.95):
    """
    檢測重複或相似圖片
    
    Args:
        images: 圖片列表
        similarity_threshold: 相似度閾值（越高越嚴格）
    """
    # 計算所有圖片的向量
    features = []
    for img in images:
        img_tensor = preprocess(img).unsqueeze(0)
        with torch.no_grad():
            feat = model.encode_image(img_tensor)
            feat /= feat.norm(dim=-1, keepdim=True)
            features.append(feat)
    
    # 找出重複組
    duplicates = []
    seen = set()
    
    for i in range(len(features)):
        if i in seen:
            continue
        
        group = [i]
        for j in range(i+1, len(features)):
            if j in seen:
                continue
            
            similarity = (features[i] @ features[j].T).item()
            if similarity >= similarity_threshold:
                group.append(j)
                seen.add(j)
        
        if len(group) > 1:
            duplicates.append(group)
    
    return duplicates

# 使用範例
image_list = [Image.open(f'img_{i}.jpg') for i in range(100)]
duplicate_groups = detect_duplicates(image_list, similarity_threshold=0.95)

print(f"找到 {len(duplicate_groups)} 組重複圖片")
for i, group in enumerate(duplicate_groups):
    print(f"組 {i+1}: 圖片 {group}")
```

### 6.5 多模態檢索（Hybrid Search）

```python
def hybrid_search(query_image=None, query_text=None, 
                  image_database=None, weight_image=0.5):
    """
    結合圖片和文字的混合搜尋
    
    Args:
        query_image: 查詢圖片（可選）
        query_text: 查詢文字（可選）
        image_database: 圖片資料庫
        weight_image: 圖片權重（0-1，文字權重為 1-weight_image）
    """
    # 計算圖片特徵
    if query_image:
        img_tensor = preprocess(query_image).unsqueeze(0)
        with torch.no_grad():
            img_features = model.encode_image(img_tensor)
            img_features /= img_features.norm(dim=-1, keepdim=True)
    else:
        img_features = None
    
    # 計算文字特徵
    if query_text:
        text_tokens = tokenizer([query_text])
        with torch.no_grad():
            text_features = model.encode_text(text_tokens)
            text_features /= text_features.norm(dim=-1, keepdim=True)
    else:
        text_features = None
    
    # 混合搜尋
    results = []
    for img_id, db_features in image_database.items():
        score = 0
        
        if img_features is not None:
            img_sim = (img_features @ db_features.T).item()
            score += weight_image * img_sim
        
        if text_features is not None:
            text_sim = (text_features @ db_features.T).item()
            score += (1 - weight_image) * text_sim
        
        results.append({'id': img_id, 'score': score})
    
    results.sort(key=lambda x: x['score'], reverse=True)
    return results

# 使用範例：既有圖片又有文字描述
results = hybrid_search(
    query_image=Image.open('example.jpg'),
    query_text="紅色運動鞋",
    image_database=product_vectors,
    weight_image=0.6  # 60% 看圖片，40% 看文字
)
```

---

## 7. 完整程式碼範例

### 7.1 商品搜尋完整系統

```python
import torch
import mobileclip
from PIL import Image
from typing import List, Dict, Optional
import numpy as np
from dataclasses import dataclass

@dataclass
class Product:
    """商品資料結構"""
    id: str
    name: str
    price: float
    description: str
    image_path: str
    category: str

class ProductSearchEngine:
    """商品搜尋引擎"""
    
    def __init__(self, model_name='mobileclip_s2', model_path=None):
        """
        初始化搜尋引擎
        
        Args:
            model_name: 模型名稱
            model_path: 模型檔案路徑
        """
        print("🔧 正在載入模型...")
        self.model, _, self.preprocess = mobileclip.create_model_and_transforms(
            model_name,
            pretrained=model_path
        )
        self.tokenizer = mobileclip.get_tokenizer(model_name)
        self.model.eval()  # 設為評估模式
        
        # 產品向量資料庫
        self.product_vectors = {}
        self.products = {}
        
        print("✅ 模型載入完成！")
    
    def add_product(self, product: Product):
        """
        新增商品到資料庫
        
        Args:
            product: 商品物件
        """
        # 載入並預處理圖片
        image = Image.open(product.image_path).convert('RGB')
        image_tensor = self.preprocess(image).unsqueeze(0)
        
        # 計算圖片向量
        with torch.no_grad():
            features = self.model.encode_image(image_tensor)
            features /= features.norm(dim=-1, keepdim=True)
        
        # 存入資料庫
        self.product_vectors[product.id] = features
        self.products[product.id] = product
        
        print(f"✅ 已新增商品: {product.name}")
    
    def batch_add_products(self, products: List[Product], batch_size=32):
        """
        批次新增商品（更高效）
        
        Args:
            products: 商品列表
            batch_size: 批次大小
        """
        print(f"📦 正在批次處理 {len(products)} 個商品...")
        
        for i in range(0, len(products), batch_size):
            batch = products[i:i+batch_size]
            
            # 批次載入圖片
            images = []
            for product in batch:
                image = Image.open(product.image_path).convert('RGB')
                images.append(self.preprocess(image))
            
            # 批次計算向量
            batch_tensor = torch.stack(images)
            with torch.no_grad():
                features = self.model.encode_image(batch_tensor)
                features /= features.norm(dim=-1, keepdim=True)
            
            # 存入資料庫
            for j, product in enumerate(batch):
                self.product_vectors[product.id] = features[j:j+1]
                self.products[product.id] = product
            
            print(f"進度: {min(i+batch_size, len(products))}/{len(products)}")
        
        print("✅ 批次處理完成！")
    
    def search_by_image(self, 
                       query_image: Image.Image,
                       top_k: int = 5,
                       min_similarity: float = 0.7) -> List[Dict]:
        """
        用圖片搜尋商品
        
        Args:
            query_image: 查詢圖片
            top_k: 返回前 K 個結果
            min_similarity: 最低相似度閾值
        
        Returns:
            搜尋結果列表
        """
        # 編碼查詢圖片
        query_tensor = self.preprocess(query_image).unsqueeze(0)
        with torch.no_grad():
            query_features = self.model.encode_image(query_tensor)
            query_features /= query_features.norm(dim=-1, keepdim=True)
        
        # 計算相似度
        results = []
        for product_id, product_features in self.product_vectors.items():
            similarity = (query_features @ product_features.T).item()
            
            if similarity >= min_similarity:
                product = self.products[product_id]
                results.append({
                    'product_id': product.id,
                    'name': product.name,
                    'price': product.price,
                    'description': product.description,
                    'category': product.category,
                    'similarity': similarity,
                    'confidence': f"{similarity*100:.1f}%"
                })
        
        # 排序並返回前 K 個
        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results[:top_k]
    
    def search_by_text(self,
                      query_text: str,
                      top_k: int = 5,
                      min_similarity: float = 0.6) -> List[Dict]:
        """
        用文字搜尋商品
        
        Args:
            query_text: 查詢文字
            top_k: 返回前 K 個結果
            min_similarity: 最低相似度閾值
        """
        # 編碼查詢文字
        text_tokens = self.tokenizer([query_text])
        with torch.no_grad():
            query_features = self.model.encode_text(text_tokens)
            query_features /= query_features.norm(dim=-1, keepdim=True)
        
        # 計算相似度並返回結果
        results = []
        for product_id, product_features in self.product_vectors.items():
            similarity = (query_features @ product_features.T).item()
            
            if similarity >= min_similarity:
                product = self.products[product_id]
                results.append({
                    'product_id': product.id,
                    'name': product.name,
                    'price': product.price,
                    'description': product.description,
                    'category': product.category,
                    'similarity': similarity,
                    'confidence': f"{similarity*100:.1f}%"
                })
        
        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results[:top_k]
    
    def hybrid_search(self,
                     query_image: Optional[Image.Image] = None,
                     query_text: Optional[str] = None,
                     image_weight: float = 0.6,
                     top_k: int = 5) -> List[Dict]:
        """
        混合搜尋：結合圖片和文字
        
        Args:
            query_image: 查詢圖片（可選）
            query_text: 查詢文字（可選）
            image_weight: 圖片權重（0-1）
            top_k: 返回前 K 個結果
        """
        if query_image is None and query_text is None:
            raise ValueError("至少需要提供圖片或文字")
        
        # 計算圖片特徵
        img_features = None
        if query_image:
            query_tensor = self.preprocess(query_image).unsqueeze(0)
            with torch.no_grad():
                img_features = self.model.encode_image(query_tensor)
                img_features /= img_features.norm(dim=-1, keepdim=True)
        
        # 計算文字特徵
        text_features = None
        if query_text:
            text_tokens = self.tokenizer([query_text])
            with torch.no_grad():
                text_features = self.model.encode_text(text_tokens)
                text_features /= text_features.norm(dim=-1, keepdim=True)
        
        # 混合計算相似度
        results = []
        for product_id, product_features in self.product_vectors.items():
            score = 0
            
            if img_features is not None:
                img_sim = (img_features @ product_features.T).item()
                score += image_weight * img_sim
            
            if text_features is not None:
                text_sim = (text_features @ product_features.T).item()
                score += (1 - image_weight) * text_sim
            
            product = self.products[product_id]
            results.append({
                'product_id': product.id,
                'name': product.name,
                'price': product.price,
                'description': product.description,
                'category': product.category,
                'similarity': score,
                'confidence': f"{score*100:.1f}%"
            })
        
        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results[:top_k]
    
    def save_database(self, filepath: str):
        """儲存向量資料庫"""
        torch.save({
            'product_vectors': self.product_vectors,
            'products': self.products
        }, filepath)
        print(f"✅ 資料庫已儲存至: {filepath}")
    
    def load_database(self, filepath: str):
        """載入向量資料庫"""
        data = torch.load(filepath)
        self.product_vectors = data['product_vectors']
        self.products = data['products']
        print(f"✅ 已載入 {len(self.products)} 個商品")


# ============== 使用範例 ==============

def main():
    # 1. 初始化搜尋引擎
    engine = ProductSearchEngine(
        model_name='mobileclip_s2',
        model_path='checkpoints/mobileclip_s2.pt'
    )
    
    # 2. 準備商品資料
    products = [
        Product(
            id='P001',
            name='Nike 氣墊運動鞋',
            price=3200,
            description='黑色經典款，舒適透氣',
            image_path='products/nike_shoes.jpg',
            category='鞋類'
        ),
        Product(
            id='P002',
            name='Adidas 休閒鞋',
            price=2800,
            description='白色簡約設計',
            image_path='products/adidas_shoes.jpg',
            category='鞋類'
        ),
        # ... 更多商品
    ]
    
    # 3. 批次新增商品
    engine.batch_add_products(products)
    
    # 4. 儲存資料庫（選用）
    engine.save_database('product_database.pt')
    
    # 5. 搜尋範例
    
    # 方法 A：圖片搜尋
    query_image = Image.open('customer_photo.jpg')
    results = engine.search_by_image(query_image, top_k=3)
    
    print("\n📸 圖片搜尋結果：")
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['name']}")
        print(f"   價格: NT${result['price']}")
        print(f"   信心度: {result['confidence']}")
        print()
    
    # 方法 B：文字搜尋
    results = engine.search_by_text("紅色運動鞋", top_k=3)
    
    print("\n🔍 文字搜尋結果：")
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['name']} - {result['confidence']}")
    
    # 方法 C：混合搜尋
    results = engine.hybrid_search(
        query_image=Image.open('customer_photo.jpg'),
        query_text="舒適的運動鞋",
        image_weight=0.7,  # 70% 看圖片，30% 看文字
        top_k=3
    )
    
    print("\n🎯 混合搜尋結果：")
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['name']} - {result['confidence']}")

if __name__ == '__main__':
    main()
```

### 7.2 實時相機搜尋（iOS 風格）

```python
import cv2
import torch
import mobileclip
from PIL import Image
import time

class RealtimeProductSearch:
    """實時商品搜尋"""
    
    def __init__(self, model_path, database_path):
        # 載入模型
        self.model, _, self.preprocess = mobileclip.create_model_and_transforms(
            'mobileclip_s2',
            pretrained=model_path
        )
        self.model.eval()
        
        # 載入商品資料庫
        data = torch.load(database_path)
        self.product_vectors = data['product_vectors']
        self.products = data['products']
        
        print("✅ 實時搜尋系統已就緒")
    
    def search_frame(self, frame, threshold=0.75):
        """
        搜尋單一畫面
        
        Args:
            frame: OpenCV 畫面 (BGR)
            threshold: 相似度閾值
        """
        # 轉換為 RGB PIL Image
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(rgb_frame)
        
        # 預處理並編碼
        image_tensor = self.preprocess(pil_image).unsqueeze(0)
        with torch.no_grad():
            query_features = self.model.encode_image(image_tensor)
            query_features /= query_features.norm(dim=-1, keepdim=True)
        
        # 找最佳匹配
        best_match = None
        best_score = threshold
        
        for product_id, product_features in self.product_vectors.items():
            similarity = (query_features @ product_features.T).item()
            if similarity > best_score:
                best_score = similarity
                best_match = self.products[product_id]
        
        return best_match, best_score
    
    def run_camera(self, camera_id=0):
        """
        運行相機實時搜尋
        
        Args:
            camera_id: 相機編號
        """
        cap = cv2.VideoCapture(camera_id)
        
        print("📷 相機已啟動，按 'q' 退出")
        
        # FPS 計算
        fps_time = time.time()
        fps_counter = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # 每 10 幀搜尋一次（減少運算）
            if fps_counter % 10 == 0:
                product, score = self.search_frame(frame)
                
                # 在畫面上顯示結果
                if product:
                    text = f"{product.name} ({score*100:.1f}%)"
                    price_text = f"NT$ {product.price}"
                    
                    # 繪製半透明背景
                    overlay = frame.copy()
                    cv2.rectangle(overlay, (10, 10), (400, 100), (0, 0, 0), -1)
                    cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)
                    
                    # 繪製文字
                    cv2.putText(frame, text, (20, 40),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                    cv2.putText(frame, price_text, (20, 75),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # 計算並顯示 FPS
            fps_counter += 1
            if time.time() - fps_time > 1:
                fps = fps_counter / (time.time() - fps_time)
                fps_counter = 0
                fps_time = time.time()
            
            cv2.putText(frame, f"FPS: {fps:.1f}", (frame.shape[1]-150, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # 顯示畫面
            cv2.imshow('Product Search', frame)
            
            # 按 'q' 退出
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()

# 使用範例
if __name__ == '__main__':
    searcher = RealtimeProductSearch(
        model_path='checkpoints/mobileclip_s2.pt',
        database_path='product_database.pt'
    )
    searcher.run_camera(camera_id=0)
```

---

## 8. 效能優化建議

### 8.1 模型選擇優化

```python
# 根據裝置選擇模型
import platform

def select_optimal_model():
    """自動選擇最適合的模型"""
    
    system = platform.system()
    
    if torch.cuda.is_available():
        # 有 GPU：使用最大模型
        return 'mobileclip_blt', 'checkpoints/mobileclip_blt.pt'
    
    elif system == 'Darwin':  # macOS
        # Apple Silicon：使用中等模型
        return 'mobileclip_s2', 'checkpoints/mobileclip_s2.pt'
    
    else:
        # 一般 CPU：使用小模型
        return 'mobileclip_s0', 'checkpoints/mobileclip_s0.pt'

model_name, model_path = select_optimal_model()
print(f"✅ 選擇模型: {model_name}")
```

### 8.2 記憶體優化

```python
# 使用半精度浮點數（FP16）
model = model.half()  # 轉為 FP16，記憶體減半

# 推論時使用
with torch.cuda.amp.autocast():
    features = model.encode_image(image)

# 批次處理時清理記憶體
import gc

def batch_process_with_cleanup(images, batch_size=32):
    for i in range(0, len(images), batch_size):
        batch = images[i:i+batch_size]
        # ... 處理批次 ...
        
        # 清理記憶體
        torch.cuda.empty_cache()
        gc.collect()
```

### 8.3 速度優化

```python
# 1. 預先計算所有商品向量（只做一次）
def precompute_all_products(products):
    """預先計算，大幅提升搜尋速度"""
    print("正在預計算所有商品向量...")
    
    all_features = []
    for product in products:
        image = Image.open(product.image_path).convert('RGB')
        image_tensor = preprocess(image).unsqueeze(0)
        
        with torch.no_grad():
            features = model.encode_image(image_tensor)
            features /= features.norm(dim=-1, keepdim=True)
            all_features.append(features)
    
    # 合併為一個大矩陣（更快的矩陣運算）
    return torch.cat(all_features, dim=0)

# 2. 使用向量化運算
def fast_batch_search(query_features, all_product_features):
    """向量化搜尋，比迴圈快 10-100 倍"""
    # 一次計算所有相似度
    similarities = (query_features @ all_product_features.T)
    
    # 找出最佳匹配
    best_idx = similarities.argmax().item()
    best_score = similarities[0, best_idx].item()
    
    return best_idx, best_score

# 3. 使用 TorchScript（加速 50%）
traced_model = torch.jit.trace(
    model,
    (torch.randn(1, 3, 224, 224),)
)
traced_model.save('mobileclip_traced.pt')

# 載入加速模型
fast_model = torch.jit.load('mobileclip_traced.pt')
```

### 8.4 資料庫優化

```python
import numpy as np
from scipy.spatial.distance import cdist

class OptimizedDatabase:
    """優化的向量資料庫"""
    
    def __init__(self):
        self.vectors = None  # numpy array
        self.product_ids = []
        self.products = {}
    
    def build_index(self, product_vectors):
        """建立索引（使用 numpy 加速）"""
        vectors = []
        for pid, vec in product_vectors.items():
            vectors.append(vec.cpu().numpy())
            self.product_ids.append(pid)
        
        # 轉為 numpy array（更快）
        self.vectors = np.vstack(vectors)
        print(f"✅ 索引建立完成：{len(self.product_ids)} 個商品")
    
    def search(self, query_vector, top_k=5):
        """使用 numpy 加速搜尋"""
        query_np = query_vector.cpu().numpy()
        
        # 計算餘弦相似度（向量化）
        similarities = np.dot(query_np, self.vectors.T)[0]
        
        # 找出 top-k
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        results = []
        for idx in top_indices:
            results.append({
                'product_id': self.product_ids[idx],
                'similarity': float(similarities[idx])
            })
        
        return results

# 使用範例
db = OptimizedDatabase()
db.build_index(product_vectors)

# 搜尋速度提升 5-10 倍！
results = db.search(query_features, top_k=5)
```

### 8.5 快取策略

```python
from functools import lru_cache
import hashlib

class CachedSearchEngine:
    """帶快取的搜尋引擎"""
    
    def __init__(self, cache_size=1000):
        self.cache_size = cache_size
        self._setup_cache()
    
    def _setup_cache(self):
        """設定 LRU 快取"""
        
        @lru_cache(maxsize=self.cache_size)
        def _cached_encode_image(image_hash):
            """快取圖片編碼結果"""
            # 這裡返回預計算的結果
            return self._encode_image_impl(image_hash)
        
        self._cached_encode = _cached_encode_image
    
    def _image_to_hash(self, image):
        """將圖片轉為 hash（用於快取鍵）"""
        # 簡單的 hash 方法
        image_bytes = image.tobytes()
        return hashlib.md5(image_bytes).hexdigest()
    
    def search_with_cache(self, query_image):
        """使用快取的搜尋"""
        img_hash = self._image_to_hash(query_image)
        
        # 嘗試從快取獲取
        features = self._cached_encode(img_hash)
        
        # 搜尋
        return self._search_impl(features)

# 熱門商品的搜尋會變得超快！
```

### 8.6 效能基準測試

```python
import time

def benchmark_search_speed(engine, num_queries=100):
    """測試搜尋速度"""
    
    print("🔬 開始效能測試...")
    
    # 準備測試圖片
    test_images = [
        Image.open(f'test_{i}.jpg') 
        for i in range(num_queries)
    ]
    
    # 測試搜尋速度
    start_time = time.time()
    
    for img in test_images:
        results = engine.search_by_image(img, top_k=1)
    
    end_time = time.time()
    
    # 計算統計
    total_time = end_time - start_time
    avg_time = total_time / num_queries
    qps = num_queries / total_time
    
    print(f"\n📊 效能測試結果：")
    print(f"   總時間: {total_time:.2f} 秒")
    print(f"   平均延遲: {avg_time*1000:.2f} ms")
    print(f"   QPS (查詢/秒): {qps:.1f}")
    
    return {
        'total_time': total_time,
        'avg_latency': avg_time,
        'qps': qps
    }

# 運行測試
benchmark_search_speed(engine, num_queries=100)
```

---

## 附錄

### A. 常見問題 FAQ

**Q1: 為什麼我的搜尋結果不準確？**
- 檢查圖片品質（清晰度、光線）
- 確認閾值設定是否合理
- 考慮使用更大的模型（如 B-LT）
- 嘗試混合搜尋（圖片+文字）

**Q2: 如何處理多語言文字搜尋？**
- MobileCLIP 支援多語言（包含中文）
- 直接使用中文描述即可
- 效果可能略遜於英文

**Q3: 模型可以微調（fine-tune）嗎？**
- 可以，但需要大量資料和運算資源
- 建議先用預訓練模型測試
- 如需微調，參考 OpenCLIP 的訓練腳本

**Q4: 能在手機上運行嗎？**
- iOS：需轉換為 Core ML 格式
- Android：需轉換為 TensorFlow Lite
- 預期延遲：3-15ms（根據模型大小）

**Q5: 資料庫有幾萬個商品會太慢嗎？**
- 預計算向量後，10萬商品搜尋 < 1秒
- 可使用向量資料庫（如 Faiss）進一步加速
- 考慮使用 GPU 加速

### B. 參考資源

**官方資源**：
- GitHub: https://github.com/apple/ml-mobileclip
- 論文: https://arxiv.org/abs/2311.17049
- HuggingFace: https://huggingface.co/apple/MobileCLIP-S2

**相關工具**：
- OpenCLIP: https://github.com/mlfoundations/open_clip
- Core ML Tools: https://coremltools.readme.io
- PyTorch: https://pytorch.org

**學習資源**：
- CLIP 原理解說
- 向量搜尋最佳實踐
- iOS Core ML 開發指南

### C. 模型規格對照表

| 模型 | 圖片編碼器 | 文字編碼器 | 總參數 | 圖片延遲 | 文字延遲 | Top-1 準確率 |
|------|-----------|-----------|--------|---------|---------|-------------|
| S0 | 11.4M | 42.4M | 53.8M | 1.5ms | 1.6ms | 67.8% |
| S1 | 21.5M | 42.4M | 63.9M | 2.5ms | 1.9ms | 70.7% |
| S2 | 35.7M | 42.4M | 78.1M | 3.6ms | 2.1ms | 73.4% |
| B | 86.3M | 42.4M | 128.7M | 10.4ms | 3.3ms | 76.8% |
| B-LT | 86.3M | 42.4M | 128.7M | 10.4ms | 3.3ms | 77.2% |

*延遲測試平台：iPhone 12 Pro Max*

---

## 結語

MobileCLIP 是一個強大的工具，特別適合：
- ✅ 需要離線執行的應用
- ✅ 對延遲敏感的場景
- ✅ 行動裝置部署
- ✅ 零樣本學習需求

**開始使用建議**：
1. 先用 S2 模型快速原型
2. 測試真實場景效果
3. 根據需求選擇最終模型
4. 優化資料庫和搜尋流程

祝你開發順利！🚀

---

**文件版本**：v1.0  
**作者**：Claude  
**最後更新**：2025-10-27
