# MobileCLIP 完整使用指南

> Apple MobileCLIP 模型介紹 + 完整程式碼範例

---

## 📑 目錄

- [模型介紹與選擇](#模型介紹與選擇)
- [安裝與環境設置](#安裝與環境設置)
- [基礎使用範例](#基礎使用範例)
- [進階應用範例](#進階應用範例)
- [效能優化技巧](#效能優化技巧)
- [常見問題處理](#常見問題處理)

---

## 模型介紹與選擇

### 📊 五個模型完整對比

| 模型 | 參數量 | 推論速度 | ImageNet 準確度 | 38 個數據集平均 | 檔案大小 | 適用場景 |
|------|--------|----------|----------------|----------------|---------|----------|
| **S0** | 54M | 3.1ms | 67.8% | 58.1% | ~45 MB | 極致輕量，低階手機 |
| **S1** | 63M | 3.3ms | 72.6% | 61.3% | ~55 MB | 平衡速度與準確度 ⭐ |
| **S2** | 82M | 4.2ms | 75.7% | 63.7% | ~70 MB | 較高準確度需求 ⭐ |
| **B** | 86M | 5.4ms | 76.8% | 65.2% | ~75 MB | 高準確度，中階手機 |
| **B (LT)** | 86M | 5.4ms | 77.2% | 65.8% | ~75 MB | 最高準確度 |

> ⭐ 推薦：以圖找圖應用優先選擇 **S1** 或 **S2**

---

### 🔍 模型詳細說明

#### **mobileclip_s0.pt** - 極致輕量版
```
✓ 特點：體積最小、速度最快
✓ 參數：11.4M (圖像) + 42.4M (文字) = 53.8M
✓ 速度：1.5ms (圖像) + 1.6ms (文字) = 3.1ms
✓ 準確度：ImageNet 67.8%

適合：
- 入門級手機、IoT 裝置
- 即時處理需求（相機 App）
- 需要極低延遲的應用

比較：
與 OpenAI ViT-B/16 準確度相當，但快 4.8 倍、小 2.8 倍
```

#### **mobileclip_s1.pt** - 輕量平衡版 ⭐
```
✓ 特點：輕量與準確度的最佳平衡點
✓ 參數：約 63M
✓ 速度：約 3.3ms
✓ 準確度：ImageNet 72.6%

適合：
- 一般手機應用
- 大多數以圖找圖場景
- 平衡效能與品質

推薦理由：
- 快速驗證 POC 的最佳選擇
- Android 移植最容易
- 準確度已足夠大多數場景
```

#### **mobileclip_s2.pt** - 中等規模版 ⭐
```
✓ 特點：更高準確度，仍保持輕量
✓ 參數：約 82M
✓ 速度：約 4.2ms
✓ 準確度：ImageNet 75.7%

適合：
- 中高階手機
- 需要較高辨識準確度的應用
- 電商、圖片搜尋等場景

比較：
比 SigLIP ViT-B/16 快 2.3 倍、小 2.1 倍，但準確度更高
```

#### **mobileclip_b.pt** - 標準大模型
```
✓ 特點：高準確度版本
✓ 參數：約 86M
✓ 速度：約 5.4ms
✓ 準確度：ImageNet 76.8%

適合：
- 旗艦手機、平板
- 專業應用（設計、創意工具）
- 對準確度要求高的場景
```

#### **mobileclip_blt.pt** - 長訓練版本
```
✓ 特點：B 版本的增強訓練版，準確度最高
✓ 參數：86M（與 B 相同）
✓ 速度：5.4ms（與 B 相同）
✓ 準確度：ImageNet 77.2%（最高）
✓ 訓練：使用更長的訓練時間（600k iterations）

適合：
- 需要最佳準確度的應用
- 服務端部署（記憶體不受限）
- 品質優先的場景

比較：
準確度超越 OpenAI ViT-L/14@336
```

---

### 🎯 模型選擇決策樹

```
┌─────────────────────────────┐
│  需要最快速度？              │
│  └─ Yes → S0                │
└─────────────────────────────┘
         │ No
         ↓
┌─────────────────────────────┐
│  需要最高準確度？            │
│  └─ Yes → B (LT)            │
└─────────────────────────────┘
         │ No
         ↓
┌─────────────────────────────┐
│  介於兩者之間？              │
│  ├─ 偏向速度 → S1 ⭐        │
│  ├─ 平衡 → S2 ⭐            │
│  └─ 偏向準確度 → B          │
└─────────────────────────────┘
```

### 📱 實際應用場景推薦

| 應用場景 | 推薦模型 | 理由 |
|---------|---------|------|
| 相機即時辨識 | **S0** | 速度優先，低延遲 |
| 手機相簿搜尋 | **S1** 或 **S2** | 平衡體驗 |
| 電商以圖找圖 | **S2** 或 **B** | 準確度重要 |
| 專業圖片管理 | **B (LT)** | 品質優先 |
| IoT/邊緣設備 | **S0** | 資源受限 |
| 服務端 API | **B (LT)** | 無資源限制 |

---

## 安裝與環境設置

### 📦 安裝依賴

```bash
# 安裝必要套件
pip install torch torchvision pillow numpy tqdm matplotlib

# 安裝 MobileCLIP
pip install git+https://github.com/apple/ml-mobileclip.git
```

### 📥 下載預訓練模型

```bash
# 建立模型資料夾
mkdir -p checkpoints
cd checkpoints

# 下載模型（選一個或多個）
# S0 - 最輕量（建議先下載這個測試）
wget https://docs-assets.developer.apple.com/ml-research/datasets/mobileclip/mobileclip_s0.pt

# S1 - 平衡版（推薦）
wget https://docs-assets.developer.apple.com/ml-research/datasets/mobileclip/mobileclip_s1.pt

# S2 - 中等規模（推薦）
wget https://docs-assets.developer.apple.com/ml-research/datasets/mobileclip/mobileclip_s2.pt

# B - 大模型
wget https://docs-assets.developer.apple.com/ml-research/datasets/mobileclip/mobileclip_b.pt

# B (LT) - 最佳準確度
wget https://docs-assets.developer.apple.com/ml-research/datasets/mobileclip/mobileclip_blt.pt
```

或使用官方腳本：
```bash
# 下載所有模型
source get_pretrained_models.sh
```

---

## 基礎使用範例

### 🎯 範例 1：單張圖片特徵提取（最基本）

```python
import torch
import mobileclip
from PIL import Image

# ========== 1. 載入模型 ==========
model, _, preprocess = mobileclip.create_model_and_transforms(
    'mobileclip_s1',  # 模型名稱：s0, s1, s2, b
    pretrained='checkpoints/mobileclip_s1.pt'  # 權重檔案路徑
)

# 設定為評估模式
model.eval()

# 選擇裝置（GPU 或 CPU）
device = 'cuda' if torch.cuda.is_available() else 'cpu'
model.to(device)

print(f"✓ 模型已載入，使用裝置: {device}")


# ========== 2. 從圖片檔案轉換成 tensor ==========

# 讀取圖片（支援 jpg, png 等格式）
image_path = "my_cat.jpg"
image = Image.open(image_path).convert('RGB')  # 確保是 RGB 格式

print(f"✓ 原始圖片大小: {image.size}")

# 使用 preprocess 進行預處理（resize, normalize 等）
image_tensor = preprocess(image)  # 輸出 shape: (3, H, W)

print(f"✓ 預處理後 tensor shape: {image_tensor.shape}")

# 增加 batch 維度 (1, 3, H, W)
image_tensor = image_tensor.unsqueeze(0)

print(f"✓ 加入 batch 維度後: {image_tensor.shape}")

# 移動到對應裝置
image_tensor = image_tensor.to(device)


# ========== 3. 提取特徵 ==========

with torch.no_grad():  # 不需要計算梯度
    image_features = model.encode_image(image_tensor)
    
    # L2 歸一化（重要！用於計算相似度）
    image_features = image_features / image_features.norm(dim=-1, keepdim=True)

print(f"✓ 特徵向量 shape: {image_features.shape}")  # (1, 512)
print(f"✓ 特徵向量範例（前 10 維）: {image_features[0, :10]}")

# 轉換成 numpy（如果需要儲存或進一步處理）
features_numpy = image_features.cpu().numpy()
print(f"✓ Numpy 格式 shape: {features_numpy.shape}")
```

**輸出範例：**
```
✓ 模型已載入，使用裝置: cpu
✓ 原始圖片大小: (1920, 1080)
✓ 預處理後 tensor shape: torch.Size([3, 256, 256])
✓ 加入 batch 維度後: torch.Size([1, 3, 256, 256])
✓ 特徵向量 shape: torch.Size([1, 512])
✓ 特徵向量範例（前 10 維）: tensor([ 0.0234, -0.1234,  0.0567, ...])
✓ Numpy 格式 shape: (1, 512)
```

---

### 📐 關鍵概念說明

#### **image_tensor 的完整轉換流程**

```python
# 步驟 1: 讀取圖片檔案
image = Image.open("cat.jpg").convert('RGB')
# → PIL.Image 物件，例如 (1920, 1080, 3)

# 步驟 2: 預處理（resize, normalize）
image_tensor = preprocess(image)
# → torch.Tensor, shape: (3, H, W)，例如 (3, 256, 256)
# → 值範圍已被標準化（通常是 [-1, 1] 或 [0, 1]）

# 步驟 3: 增加 batch 維度
image_tensor = image_tensor.unsqueeze(0)
# → shape: (1, 3, H, W)，例如 (1, 3, 256, 256)

# 步驟 4: 移到對應裝置
image_tensor = image_tensor.to(device)
# → 如果有 GPU 就移到 GPU，否則留在 CPU

# 步驟 5: 提取特徵
image_features = model.encode_image(image_tensor)
# → shape: (1, 512)，就是你要的特徵向量！
```

#### **preprocess 做了什麼？**

`preprocess` 是 MobileCLIP 提供的預處理函數，等同於：

```python
from torchvision import transforms

preprocess = transforms.Compose([
    transforms.Resize(256),              # 調整大小
    transforms.CenterCrop(256),          # 中心裁切
    transforms.ToTensor(),               # 轉成 Tensor
    transforms.Normalize(                # 標準化
        mean=[0.485, 0.456, 0.406],      # ImageNet mean
        std=[0.229, 0.224, 0.225]        # ImageNet std
    )
])
```

---

## 進階應用範例

### 🚀 範例 2：批次處理多張圖片（更快）

```python
import torch
import mobileclip
from PIL import Image
from pathlib import Path
from tqdm import tqdm

# 載入模型
model, _, preprocess = mobileclip.create_model_and_transforms(
    'mobileclip_s1',
    pretrained='checkpoints/mobileclip_s1.pt'
)
model.eval()
device = 'cuda' if torch.cuda.is_available() else 'cpu'
model.to(device)


# ========== 批次處理多張圖片 ==========

def extract_features_batch(image_paths, batch_size=32):
    """
    批次提取多張圖片的特徵
    
    Args:
        image_paths: 圖片路徑列表
        batch_size: 批次大小
    
    Returns:
        features: (N, 512) 的特徵矩陣
        valid_paths: 成功處理的圖片路徑列表
    """
    all_features = []
    valid_paths = []
    
    # 分批處理
    for i in tqdm(range(0, len(image_paths), batch_size), desc="提取特徵"):
        batch_paths = image_paths[i:i+batch_size]
        
        # 載入並預處理這一批圖片
        batch_images = []
        batch_valid_paths = []
        
        for path in batch_paths:
            try:
                img = Image.open(path).convert('RGB')
                img_tensor = preprocess(img)
                batch_images.append(img_tensor)
                batch_valid_paths.append(path)
            except Exception as e:
                print(f"⚠ 無法讀取 {path}: {e}")
                continue
        
        if not batch_images:
            continue
        
        # 堆疊成 batch (B, 3, H, W)
        batch_tensor = torch.stack(batch_images).to(device)
        
        # 提取特徵
        with torch.no_grad():
            features = model.encode_image(batch_tensor)
            # L2 歸一化
            features = features / features.norm(dim=-1, keepdim=True)
        
        all_features.append(features.cpu())
        valid_paths.extend(batch_valid_paths)
    
    # 合併所有批次
    if all_features:
        all_features = torch.cat(all_features, dim=0)
    else:
        all_features = torch.empty(0, 512)
    
    return all_features, valid_paths


# ========== 使用範例 ==========

# 掃描圖片資料夾
image_folder = "./my_photos"
image_paths = []

for ext in ['*.jpg', '*.jpeg', '*.png', '*.webp']:
    image_paths.extend(list(Path(image_folder).glob(ext)))

image_paths = [str(p) for p in image_paths]
print(f"找到 {len(image_paths)} 張圖片")

# 批次提取特徵
features, valid_paths = extract_features_batch(image_paths, batch_size=32)

print(f"✓ 特徵矩陣 shape: {features.shape}")  # (N, 512)
print(f"✓ 成功處理 {len(valid_paths)} 張圖片")

# 儲存特徵
import numpy as np
np.savez('image_features.npz', 
         features=features.numpy(),
         paths=valid_paths)
print("✓ 特徵已儲存到 image_features.npz")
```

---

### 🔍 範例 3：以圖找圖（完整流程）

#### 步驟 1: 建立圖片索引

```python
import torch
import mobileclip
from PIL import Image
import numpy as np
from pathlib import Path
from tqdm import tqdm

def build_image_index(image_folder, model_name='mobileclip_s1', output_file='index.npz'):
    """
    建立圖片索引
    
    Args:
        image_folder: 圖片資料夾路徑
        model_name: 使用的模型名稱
        output_file: 索引輸出檔案
    
    Returns:
        features_matrix: (N, 512) 特徵矩陣
        image_paths: 圖片路徑列表
    """
    
    # 載入模型
    print("📦 載入模型...")
    model, _, preprocess = mobileclip.create_model_and_transforms(
        model_name,
        pretrained=f'checkpoints/{model_name}.pt'
    )
    model.eval()
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model.to(device)
    print(f"✓ 模型已載入到 {device}")
    
    # 掃描所有圖片
    print("\n📂 掃描圖片...")
    image_paths = []
    for ext in ['*.jpg', '*.jpeg', '*.png', '*.webp', '*.bmp']:
        image_paths.extend(Path(image_folder).glob(ext))
    
    image_paths = [str(p) for p in image_paths]
    print(f"✓ 找到 {len(image_paths)} 張圖片")
    
    # 批次提取特徵
    print("\n🎨 提取特徵...")
    all_features = []
    valid_paths = []
    batch_size = 32
    
    for i in tqdm(range(0, len(image_paths), batch_size)):
        batch_paths = image_paths[i:i+batch_size]
        batch_images = []
        batch_valid = []
        
        for img_path in batch_paths:
            try:
                img = Image.open(img_path).convert('RGB')
                img_tensor = preprocess(img)
                batch_images.append(img_tensor)
                batch_valid.append(img_path)
            except Exception as e:
                print(f"⚠ 跳過 {img_path}: {e}")
        
        if not batch_images:
            continue
        
        # 批次推論
        batch_tensor = torch.stack(batch_images).to(device)
        
        with torch.no_grad():
            features = model.encode_image(batch_tensor)
            features = features / features.norm(dim=-1, keepdim=True)
        
        all_features.append(features.cpu().numpy())
        valid_paths.extend(batch_valid)
    
    # 合併特徵
    features_matrix = np.vstack(all_features)
    
    # 儲存索引
    print(f"\n💾 儲存索引...")
    np.savez(output_file, 
             features=features_matrix,
             paths=valid_paths,
             model_name=model_name)
    
    print(f"✓ 索引已建立: {output_file}")
    print(f"✓ 特徵矩陣 shape: {features_matrix.shape}")
    print(f"✓ 圖片數量: {len(valid_paths)}")
    
    return features_matrix, valid_paths


# ========== 使用範例 ==========
if __name__ == '__main__':
    features, paths = build_image_index(
        image_folder='./my_photos',
        model_name='mobileclip_s1',
        output_file='photo_index.npz'
    )
```

#### 步驟 2: 搜尋相似圖片

```python
import torch
import mobileclip
from PIL import Image
import numpy as np

def search_similar_images(query_image_path, 
                         index_file='index.npz', 
                         top_k=5,
                         model_name='mobileclip_s1'):
    """
    搜尋相似圖片
    
    Args:
        query_image_path: 查詢圖片路徑
        index_file: 索引檔案路徑
        top_k: 返回結果數量
        model_name: 使用的模型名稱
    
    Returns:
        results: [(image_path, similarity_score), ...]
    """
    
    # 載入索引
    print(f"📂 載入索引: {index_file}")
    data = np.load(index_file, allow_pickle=True)
    index_features = data['features']  # (N, 512)
    image_paths = data['paths'].tolist()
    
    print(f"✓ 載入 {len(image_paths)} 張圖片的索引")
    
    # 載入模型
    print(f"\n📦 載入模型...")
    model, _, preprocess = mobileclip.create_model_and_transforms(
        model_name,
        pretrained=f'checkpoints/{model_name}.pt'
    )
    model.eval()
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model.to(device)
    
    # 提取查詢圖片特徵
    print(f"\n🔍 提取查詢圖片特徵...")
    query_img = Image.open(query_image_path).convert('RGB')
    query_tensor = preprocess(query_img).unsqueeze(0).to(device)
    
    with torch.no_grad():
        query_feat = model.encode_image(query_tensor)
        query_feat = query_feat / query_feat.norm(dim=-1, keepdim=True)
    
    query_feat = query_feat.cpu().numpy()  # (1, 512)
    
    # 計算餘弦相似度（矩陣乘法）
    print(f"\n📊 計算相似度...")
    similarities = np.dot(index_features, query_feat.T).squeeze()  # (N,)
    
    # 取 Top-K
    top_indices = np.argsort(similarities)[::-1][:top_k]
    
    # 顯示結果
    print(f"\n{'='*60}")
    print(f"查詢圖片: {query_image_path}")
    print(f"{'='*60}")
    print(f"\nTop-{top_k} 最相似圖片:\n")
    
    results = []
    for i, idx in enumerate(top_indices):
        path = image_paths[idx]
        score = similarities[idx]
        print(f"{i+1}. {path}")
        print(f"   相似度: {score:.4f} ({score*100:.2f}%)\n")
        results.append((path, float(score)))
    
    return results


# ========== 使用範例 ==========
if __name__ == '__main__':
    results = search_similar_images(
        query_image_path='./query_cat.jpg',
        index_file='photo_index.npz',
        top_k=5,
        model_name='mobileclip_s1'
    )
```

---

### 📊 範例 4：視覺化搜尋結果

```python
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np

def visualize_search_results(query_path, results, top_k=5, save_path='search_results.png'):
    """
    視覺化搜尋結果
    
    Args:
        query_path: 查詢圖片路徑
        results: [(image_path, score), ...] 搜尋結果
        top_k: 顯示數量
        save_path: 儲存路徑
    """
    
    # 設定圖表
    fig, axes = plt.subplots(1, top_k+1, figsize=(3*(top_k+1), 3))
    
    # 顯示查詢圖片
    query_img = Image.open(query_path)
    axes[0].imshow(query_img)
    axes[0].set_title('Query Image', fontsize=12, fontweight='bold', color='red')
    axes[0].axis('off')
    axes[0].set_facecolor('#ffe6e6')
    
    # 顯示搜尋結果
    for i, (img_path, score) in enumerate(results[:top_k]):
        try:
            img = Image.open(img_path)
            axes[i+1].imshow(img)
            axes[i+1].set_title(
                f'#{i+1}\nScore: {score:.3f}', 
                fontsize=10,
                color='green' if score > 0.8 else 'blue'
            )
            axes[i+1].axis('off')
        except Exception as e:
            print(f"無法載入圖片 {img_path}: {e}")
            axes[i+1].text(0.5, 0.5, 'Error', ha='center', va='center')
            axes[i+1].axis('off')
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.show()
    
    print(f"✓ 搜尋結果已儲存到 {save_path}")


# ========== 使用範例 ==========
if __name__ == '__main__':
    # 先搜尋
    results = search_similar_images(
        query_image_path='./query_cat.jpg',
        index_file='photo_index.npz',
        top_k=5
    )
    
    # 視覺化
    visualize_search_results(
        query_path='./query_cat.jpg',
        results=results,
        top_k=5
    )
```

---

### 🎯 範例 5：完整的 CLI 工具

#### build_index.py - 建立索引

```python
#!/usr/bin/env python3
"""
建立圖片索引
用法: python build_index.py --images ./photos --output index.npz --model mobileclip_s1
"""

import argparse
import torch
import mobileclip
from PIL import Image
import numpy as np
from pathlib import Path
from tqdm import tqdm

def main():
    parser = argparse.ArgumentParser(description='建立圖片索引')
    parser.add_argument('--images', required=True, help='圖片資料夾路徑')
    parser.add_argument('--output', default='index.npz', help='輸出索引檔案')
    parser.add_argument('--model', default='mobileclip_s1', 
                       choices=['mobileclip_s0', 'mobileclip_s1', 'mobileclip_s2', 
                               'mobileclip_b', 'mobileclip_blt'],
                       help='使用的模型')
    parser.add_argument('--batch-size', type=int, default=32, help='批次大小')
    args = parser.parse_args()
    
    print("="*60)
    print("MobileCLIP 圖片索引建立工具")
    print("="*60)
    
    # 載入模型
    print(f"\n📦 載入模型: {args.model}")
    model, _, preprocess = mobileclip.create_model_and_transforms(
        args.model.replace('mobileclip_', ''),
        pretrained=f'checkpoints/{args.model}.pt'
    )
    model.eval()
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model.to(device)
    print(f"✓ 使用裝置: {device}")
    
    # 掃描圖片
    print(f"\n📂 掃描圖片資料夾: {args.images}")
    image_paths = []
    for ext in ['*.jpg', '*.jpeg', '*.png', '*.webp', '*.bmp']:
        image_paths.extend(Path(args.images).glob(ext))
    image_paths = [str(p) for p in image_paths]
    print(f"✓ 找到 {len(image_paths)} 張圖片")
    
    if len(image_paths) == 0:
        print("❌ 沒有找到圖片，請檢查路徑")
        return
    
    # 提取特徵
    print(f"\n🎨 提取特徵（batch_size={args.batch_size}）...")
    all_features = []
    valid_paths = []
    
    for i in tqdm(range(0, len(image_paths), args.batch_size)):
        batch_paths = image_paths[i:i+args.batch_size]
        batch_images = []
        batch_valid = []
        
        for img_path in batch_paths:
            try:
                img = Image.open(img_path).convert('RGB')
                img_tensor = preprocess(img)
                batch_images.append(img_tensor)
                batch_valid.append(img_path)
            except:
                continue
        
        if batch_images:
            batch_tensor = torch.stack(batch_images).to(device)
            with torch.no_grad():
                features = model.encode_image(batch_tensor)
                features = features / features.norm(dim=-1, keepdim=True)
            all_features.append(features.cpu().numpy())
            valid_paths.extend(batch_valid)
    
    # 合併並儲存
    features_matrix = np.vstack(all_features)
    
    print(f"\n💾 儲存索引...")
    np.savez(args.output,
             features=features_matrix,
             paths=valid_paths,
             model_name=args.model)
    
    print(f"\n{'='*60}")
    print("✅ 索引建立完成！")
    print(f"{'='*60}")
    print(f"輸出檔案: {args.output}")
    print(f"特徵矩陣: {features_matrix.shape}")
    print(f"成功處理: {len(valid_paths)} 張圖片")
    print(f"失敗: {len(image_paths) - len(valid_paths)} 張圖片")

if __name__ == '__main__':
    main()
```

#### search.py - 搜尋相似圖片

```python
#!/usr/bin/env python3
"""
搜尋相似圖片
用法: python search.py --query cat.jpg --index index.npz --top 5
"""

import argparse
import torch
import mobileclip
from PIL import Image
import numpy as np

def main():
    parser = argparse.ArgumentParser(description='搜尋相似圖片')
    parser.add_argument('--query', required=True, help='查詢圖片路徑')
    parser.add_argument('--index', required=True, help='索引檔案路徑')
    parser.add_argument('--top', type=int, default=5, help='返回結果數量')
    parser.add_argument('--visualize', action='store_true', help='視覺化結果')
    args = parser.parse_args()
    
    print("="*60)
    print("MobileCLIP 以圖找圖工具")
    print("="*60)
    
    # 載入索引
    print(f"\n📂 載入索引: {args.index}")
    data = np.load(args.index, allow_pickle=True)
    index_features = data['features']
    image_paths = data['paths'].tolist()
    model_name = str(data['model_name'])
    
    print(f"✓ 載入 {len(image_paths)} 張圖片")
    print(f"✓ 使用模型: {model_name}")
    
    # 載入模型
    print(f"\n📦 載入模型...")
    model, _, preprocess = mobileclip.create_model_and_transforms(
        model_name.replace('mobileclip_', ''),
        pretrained=f'checkpoints/{model_name}.pt'
    )
    model.eval()
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model.to(device)
    
    # 提取查詢特徵
    print(f"\n🔍 分析查詢圖片: {args.query}")
    query_img = Image.open(args.query).convert('RGB')
    query_tensor = preprocess(query_img).unsqueeze(0).to(device)
    
    with torch.no_grad():
        query_feat = model.encode_image(query_tensor)
        query_feat = query_feat / query_feat.norm(dim=-1, keepdim=True)
    
    query_feat = query_feat.cpu().numpy()
    
    # 計算相似度
    print(f"\n📊 計算相似度...")
    similarities = np.dot(index_features, query_feat.T).squeeze()
    top_indices = np.argsort(similarities)[::-1][:args.top]
    
    # 顯示結果
    print(f"\n{'='*60}")
    print(f"Top-{args.top} 最相似圖片:")
    print(f"{'='*60}\n")
    
    results = []
    for i, idx in enumerate(top_indices):
        path = image_paths[idx]
        score = similarities[idx]
        print(f"{i+1}. {path}")
        print(f"   相似度: {score:.4f} ({score*100:.2f}%)\n")
        results.append((path, float(score)))
    
    # 視覺化（可選）
    if args.visualize:
        import matplotlib.pyplot as plt
        
        fig, axes = plt.subplots(1, args.top+1, figsize=(3*(args.top+1), 3))
        
        # 查詢圖片
        axes[0].imshow(query_img)
        axes[0].set_title('Query', fontweight='bold')
        axes[0].axis('off')
        
        # 結果
        for i, (path, score) in enumerate(results):
            img = Image.open(path)
            axes[i+1].imshow(img)
            axes[i+1].set_title(f'#{i+1}: {score:.3f}')
            axes[i+1].axis('off')
        
        plt.tight_layout()
        plt.savefig('search_results.png', dpi=150, bbox_inches='tight')
        print(f"✓ 視覺化結果已儲存: search_results.png")
        plt.show()

if __name__ == '__main__':
    main()
```

#### 使用範例

```bash
# 建立索引
python build_index.py --images ./my_photos --output photos.npz --model mobileclip_s1

# 搜尋相似圖片
python search.py --query ./cat.jpg --index photos.npz --top 5

# 搜尋並視覺化
python search.py --query ./cat.jpg --index photos.npz --top 5 --visualize
```

---

## 效能優化技巧

### ⚡ 1. 使用 GPU 加速

```python
# 檢查並使用 GPU
device = 'cuda' if torch.cuda.is_available() else 'cpu'
model.to(device)

# 確認是否使用 GPU
print(f"使用裝置: {device}")
print(f"GPU 名稱: {torch.cuda.get_device_name(0)}" if torch.cuda.is_available() else "")
```

### ⚡ 2. 批次處理（速度提升 5-10 倍）

```python
# ❌ 不好：一張張處理
for img_path in image_paths:
    tensor = preprocess(Image.open(img_path)).unsqueeze(0)
    features = model.encode_image(tensor)

# ✅ 好：批次處理
batch_size = 32
for i in range(0, len(image_paths), batch_size):
    batch = [preprocess(Image.open(p)) for p in image_paths[i:i+batch_size]]
    batch_tensor = torch.stack(batch)
    batch_features = model.encode_image(batch_tensor)  # 快很多！
```

### ⚡ 3. 使用混合精度（FP16）

```python
# 使用自動混合精度（AMP）
with torch.cuda.amp.autocast():
    image_features = model.encode_image(image_tensor)

# 速度提升約 2 倍，記憶體減少約 50%
```

### ⚡ 4. 不計算梯度

```python
# 推論時必須使用
with torch.no_grad():
    image_features = model.encode_image(image_tensor)

# 節省記憶體和計算時間
```

### ⚡ 5. 預先計算並快取特徵

```python
# 一次性建立索引
features = extract_all_features(image_folder)
np.save('features_cache.npy', features)

# 之後直接載入
features = np.load('features_cache.npy')

# 避免重複提取特徵
```

### ⚡ 6. 使用 DataLoader（大規模資料）

```python
from torch.utils.data import Dataset, DataLoader

class ImageDataset(Dataset):
    def __init__(self, image_paths, transform):
        self.image_paths = image_paths
        self.transform = transform
    
    def __len__(self):
        return len(self.image_paths)
    
    def __getitem__(self, idx):
        img = Image.open(self.image_paths[idx]).convert('RGB')
        return self.transform(img), self.image_paths[idx]

# 使用 DataLoader
dataset = ImageDataset(image_paths, preprocess)
dataloader = DataLoader(dataset, batch_size=32, num_workers=4, pin_memory=True)

for images, paths in dataloader:
    images = images.to(device)
    with torch.no_grad():
        features = model.encode_image(images)
```

---

## 常見問題處理

### 🐛 錯誤 1: 忘記加 batch 維度

```python
# ❌ 錯誤
image_tensor = preprocess(image)  # shape: (3, H, W)
features = model.encode_image(image_tensor)  # 報錯！

# ✅ 正確
image_tensor = preprocess(image).unsqueeze(0)  # shape: (1, 3, H, W)
features = model.encode_image(image_tensor)
```

### 🐛 錯誤 2: 忘記轉 RGB

```python
# ❌ 錯誤（PNG 可能是 RGBA，灰階圖是 L）
image = Image.open('image.png')
features = model.encode_image(preprocess(image).unsqueeze(0))  # 可能報錯

# ✅ 正確
image = Image.open('image.png').convert('RGB')  # 強制轉成 RGB
features = model.encode_image(preprocess(image).unsqueeze(0))
```

### 🐛 錯誤 3: 忘記 L2 歸一化

```python
# ❌ 錯誤（相似度計算不準確）
features = model.encode_image(image_tensor)
similarity = features @ features.T

# ✅ 正確
features = model.encode_image(image_tensor)
features = features / features.norm(dim=-1, keepdim=True)  # L2 歸一化
similarity = features @ features.T  # 正確的餘弦相似度
```

### 🐛 錯誤 4: 裝置不匹配

```python
# ❌ 錯誤
model.to('cuda')
image_tensor = preprocess(image).unsqueeze(0)  # 在 CPU
features = model.encode_image(image_tensor)  # 報錯：tensor 不在同一裝置

# ✅ 正確
model.to(device)
image_tensor = preprocess(image).unsqueeze(0).to(device)  # 移到同一裝置
features = model.encode_image(image_tensor)
```

### 🐛 錯誤 5: 記憶體不足（OOM）

```python
# 解決方法 1: 減少 batch size
batch_size = 16  # 原本 32，改成 16

# 解決方法 2: 清理 GPU 記憶體
torch.cuda.empty_cache()

# 解決方法 3: 使用梯度累積
with torch.no_grad():  # 不計算梯度
    features = model.encode_image(image_tensor)

# 解決方法 4: 使用 CPU
device = 'cpu'  # 改用 CPU（較慢但不會 OOM）
```

### 🐛 問題 6: 圖片讀取失敗

```python
# 健壯的圖片讀取
def load_image_safely(image_path):
    try:
        img = Image.open(image_path).convert('RGB')
        return img
    except Exception as e:
        print(f"⚠ 無法讀取 {image_path}: {e}")
        return None

# 使用
img = load_image_safely('image.jpg')
if img is not None:
    features = extract_features(img)
```

### 🔧 除錯技巧

```python
# 1. 檢查 tensor shape
print(f"Image tensor shape: {image_tensor.shape}")  # 應該是 (1, 3, H, W)
print(f"Features shape: {features.shape}")  # 應該是 (1, 512)

# 2. 檢查特徵向量是否歸一化
print(f"Feature norm: {torch.norm(features)}")  # 應該接近 1.0

# 3. 檢查裝置
print(f"Model device: {next(model.parameters()).device}")
print(f"Tensor device: {image_tensor.device}")

# 4. 視覺化相似度矩陣
import matplotlib.pyplot as plt
similarity_matrix = features @ features.T
plt.imshow(similarity_matrix.cpu().numpy())
plt.colorbar()
plt.title('Similarity Matrix')
plt.show()
```

---

## 📝 完整測試腳本

將以下程式碼儲存為 `test_mobileclip.py`：

```python
#!/usr/bin/env python3
"""
MobileCLIP 完整測試腳本
"""

import torch
import mobileclip
from PIL import Image
import numpy as np

def test_single_image():
    """測試單張圖片特徵提取"""
    print("\n" + "="*60)
    print("測試 1: 單張圖片特徵提取")
    print("="*60)
    
    # 載入模型
    model, _, preprocess = mobileclip.create_model_and_transforms(
        'mobileclip_s1',
        pretrained='checkpoints/mobileclip_s1.pt'
    )
    model.eval()
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model.to(device)
    
    print(f"✓ 模型已載入到 {device}")
    
    # 測試圖片
    image_path = "test.jpg"  # 替換成你的圖片
    image = Image.open(image_path).convert('RGB')
    
    print(f"✓ 圖片大小: {image.size}")
    
    # 提取特徵
    image_tensor = preprocess(image).unsqueeze(0).to(device)
    
    with torch.no_grad():
        features = model.encode_image(image_tensor)
        features = features / features.norm(dim=-1, keepdim=True)
    
    print(f"✓ 特徵 shape: {features.shape}")
    print(f"✓ 特徵 norm: {torch.norm(features).item():.4f}")
    print(f"✓ 特徵前 5 維: {features[0, :5]}")


def test_similarity():
    """測試相似度計算"""
    print("\n" + "="*60)
    print("測試 2: 相似度計算")
    print("="*60)
    
    # 載入模型
    model, _, preprocess = mobileclip.create_model_and_transforms(
        'mobileclip_s1',
        pretrained='checkpoints/mobileclip_s1.pt'
    )
    model.eval()
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model.to(device)
    
    # 兩張測試圖片
    image1 = Image.open("test1.jpg").convert('RGB')
    image2 = Image.open("test2.jpg").convert('RGB')
    
    # 提取特徵
    tensor1 = preprocess(image1).unsqueeze(0).to(device)
    tensor2 = preprocess(image2).unsqueeze(0).to(device)
    
    with torch.no_grad():
        feat1 = model.encode_image(tensor1)
        feat2 = model.encode_image(tensor2)
        
        feat1 = feat1 / feat1.norm(dim=-1, keepdim=True)
        feat2 = feat2 / feat2.norm(dim=-1, keepdim=True)
    
    # 計算相似度
    similarity = (feat1 @ feat2.T).item()
    
    print(f"✓ 圖片 1 特徵: {feat1.shape}")
    print(f"✓ 圖片 2 特徵: {feat2.shape}")
    print(f"✓ 餘弦相似度: {similarity:.4f} ({similarity*100:.2f}%)")


def test_batch_processing():
    """測試批次處理"""
    print("\n" + "="*60)
    print("測試 3: 批次處理")
    print("="*60)
    
    # 載入模型
    model, _, preprocess = mobileclip.create_model_and_transforms(
        'mobileclip_s1',
        pretrained='checkpoints/mobileclip_s1.pt'
    )
    model.eval()
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model.to(device)
    
    # 批次圖片
    image_paths = ["test1.jpg", "test2.jpg", "test3.jpg"]
    images = [Image.open(p).convert('RGB') for p in image_paths]
    
    # 批次處理
    batch_tensor = torch.stack([preprocess(img) for img in images]).to(device)
    
    print(f"✓ Batch shape: {batch_tensor.shape}")
    
    with torch.no_grad():
        batch_features = model.encode_image(batch_tensor)
        batch_features = batch_features / batch_features.norm(dim=-1, keepdim=True)
    
    print(f"✓ Batch features shape: {batch_features.shape}")
    print(f"✓ 每張圖片特徵 norm: {torch.norm(batch_features, dim=-1)}")


def main():
    print("\n" + "🚀"*30)
    print("MobileCLIP 完整測試")
    print("🚀"*30)
    
    try:
        test_single_image()
    except Exception as e:
        print(f"❌ 測試 1 失敗: {e}")
    
    try:
        test_similarity()
    except Exception as e:
        print(f"❌ 測試 2 失敗: {e}")
    
    try:
        test_batch_processing()
    except Exception as e:
        print(f"❌ 測試 3 失敗: {e}")
    
    print("\n" + "✅"*30)
    print("測試完成！")
    print("✅"*30 + "\n")


if __name__ == '__main__':
    main()
```

執行測試：
```bash
python test_mobileclip.py
```

---

## 🎓 學習路徑建議

### 階段 1: 基礎（1-2 天）
1. ✅ 安裝環境和下載模型
2. ✅ 跑通範例 1（單張圖片）
3. ✅ 理解 `preprocess` 和 `unsqueeze` 的作用
4. ✅ 測試不同模型（S0, S1, S2）

### 階段 2: 實戰（3-5 天）
1. ✅ 實作範例 2（批次處理）
2. ✅ 實作範例 3（以圖找圖）
3. ✅ 建立自己的圖片索引
4. ✅ 測試搜尋功能

### 階段 3: 優化（2-3 天）
1. ✅ 實作 CLI 工具
2. ✅ 效能優化（GPU、批次）
3. ✅ 視覺化搜尋結果
4. ✅ 錯誤處理和健壯性

### 階段 4: Android 準備（3-5 天）
1. ✅ 模型轉換（TorchScript）
2. ✅ 量化測試（INT8）
3. ✅ CPU 效能測試
4. ✅ 撰寫移植文件

---

## 📚 參考資源

- **官方 GitHub**: https://github.com/apple/ml-mobileclip
- **論文**: [MobileCLIP: Fast Image-Text Models](https://arxiv.org/pdf/2311.17049.pdf)
- **HuggingFace 模型**: [MobileCLIP Collection](https://huggingface.co/collections/apple/mobileclip-models-datacompdr-data-665789776e1aa2b59f35f7c8)
- **PyTorch 官方文檔**: https://pytorch.org/docs/stable/index.html

---

## 💡 快速參考

### 核心程式碼片段

```python
# 載入模型
model, _, preprocess = mobileclip.create_model_and_transforms(
    'mobileclip_s1', pretrained='checkpoints/mobileclip_s1.pt'
)
model.eval()
model.to('cuda' if torch.cuda.is_available() else 'cpu')

# 單張圖片
image = Image.open('cat.jpg').convert('RGB')
tensor = preprocess(image).unsqueeze(0).to(device)
with torch.no_grad():
    features = model.encode_image(tensor)
    features = features / features.norm(dim=-1, keepdim=True)

# 相似度計算
similarity = (features1 @ features2.T).item()
```

---

**祝您使用順利！有問題隨時查閱本指南 🚀**
