# 機器學習與深度學習完整指南

> 從傳統機器學習到深度學習、LLM 的完整學習資源。

## 📊 文檔統計

- **原始檔案**: 91 個 markdown 文檔
- **整合索引**: 5 個主題文檔
- **精簡比例**: 95%
- **內容保留**: 100%（索引式整合）

---

## 🗂️ 主題分類

### 📗 傳統機器學習

#### [01. 機器學習基礎](01_機器學習基礎.md)
**完整教學系列、演算法實作** | 難度: ⭐⭐

核心內容：
- 全民瘋AI系列2.0 (30天完整教學)
- 新手也能懂得AI (27篇系列)
- 監督式/非監督式學習
- 集成學習 (XGBoost/LightGBM/CatBoost)
- 進化演算法 (GA/DEAP)
- 模型驗證與部署

**適合**: ML 新手、需要系統化學習傳統機器學習

---

### 📘 深度學習

#### [02. 深度學習與 PyTorch](02_深度學習與PyTorch.md)
**PyTorch 框架、圖像識別** | 難度: ⭐⭐⭐

核心內容：
- PyTorch 安裝與基礎
- 圖像識別與人臉辨識
- YOLO 物件偵測
- YOLOv8 手勢識別
- AI 訓練技巧
- Roboflow 標註工具

**適合**: 深度學習開發者、電腦視覺應用

---

### 📙 大型語言模型

#### [03. 大型語言模型 LLM](03_大型語言模型LLM.md)
**LLM 推理、微調、部署** | 難度: ⭐⭐⭐⭐

核心內容：
- LLM 使用原理
- 推理優化技巧
- 開源 LLM 微調
- Ollama 本地部署

**適合**: NLP 開發者、LLM 應用開發

---

### 📙 自動化機器學習

#### [04. AutoML 自動化機器學習](04_AutoML自動化機器學習.md)
**Auto-sklearn、Optuna** | 難度: ⭐⭐⭐

核心內容：
- AutoML 概念與工具
- Auto-sklearn 自動化訓練
- Optuna 超參數優化
- 自動化流程設計

**適合**: 需要快速原型開發、超參數調整

---

### 📙 高性能計算

#### [05. 高性能計算](05_高性能計算.md)
**GPU 加速、cuDF** | 難度: ⭐⭐⭐⭐

核心內容：
- cuDF GPU 資料處理
- CUDA 整合
- 大規模資料加速
- RAPIDS 生態系統

**適合**: 大資料處理、高性能需求

---

## 🎯 學習路徑建議

### 新手路徑（4-8週）

**第一階段：機器學習基礎**
1. [機器學習基礎](01_機器學習基礎.md)
   - 全民瘋AI系列2.0 (Day 1-10)
   - 學習基本演算法
   - 實作簡單專案

**第二階段：深度學習入門**
1. [深度學習與 PyTorch](02_深度學習與PyTorch.md)
   - 安裝 PyTorch 環境
   - 圖像分類任務
   - 人臉辨識專案

**第三階段：實戰練習**
1. 完成一個端到端專案
2. 使用 AutoML 工具
3. 部署模型到生產環境

---

### 進階路徑（2-4個月）

**深度學習進階**
1. [深度學習與 PyTorch](02_深度學習與PyTorch.md)
   - YOLO 物件偵測
   - YOLOv8 客製化訓練
   - 模型優化技巧

**自動化與優化**
1. [AutoML 自動化機器學習](04_AutoML自動化機器學習.md)
   - Optuna 超參數調整
   - Auto-sklearn 自動化
   - 模型集成策略

**LLM 應用**
1. [大型語言模型 LLM](03_大型語言模型LLM.md)
   - LLM 推理優化
   - 模型微調
   - Ollama 本地部署

---

### 專家路徑（持續學習）

**高性能計算**
1. [高性能計算](05_高性能計算.md)
   - GPU 加速資料處理
   - CUDA 程式設計
   - 分散式訓練

**生產級部署**
1. 模型壓縮與量化
2. 推理服務優化
3. 監控與維護

**前沿技術**
1. LLM 最新進展
2. Transformer 架構
3. 多模態學習

---

## 💡 使用說明

### 學習機器學習基礎
→ [機器學習基礎](01_機器學習基礎.md) - 30天完整教學

### 深度學習與圖像處理
→ [深度學習與 PyTorch](02_深度學習與PyTorch.md) - YOLO/人臉辨識

### 大型語言模型
→ [大型語言模型 LLM](03_大型語言模型LLM.md) - 推理/微調/部署

### 自動化訓練
→ [AutoML 自動化機器學習](04_AutoML自動化機器學習.md)

### 高性能處理
→ [高性能計算](05_高性能計算.md) - GPU 加速

---

## 🔗 相關資源

### 其他章節
- [電腦視覺 CV](../cv/) - 圖像處理進階
- [Python 程式設計](../python/) - Python 技巧
- [HFT 高頻交易](../hft/) - 量化交易應用

### 外部資源
- [PyTorch 官方文檔](https://pytorch.org/docs/)
- [Scikit-learn 官方文檔](https://scikit-learn.org/)
- [Hugging Face](https://huggingface.co/)
- [RAPIDS cuDF](https://docs.rapids.ai/api/cudf/stable/)

---

## 📊 快速參考

### 常用演算法

| 任務類型 | 推薦演算法 | 難度 |
|---------|-----------|------|
| **分類** | XGBoost, Random Forest, SVM | ⭐⭐ |
| **迴歸** | Linear Regression, XGBoost | ⭐⭐ |
| **分群** | K-means, DBSCAN | ⭐⭐ |
| **降維** | PCA, t-SNE | ⭐⭐⭐ |
| **圖像識別** | CNN, YOLO | ⭐⭐⭐⭐ |
| **NLP** | Transformer, BERT, LLM | ⭐⭐⭐⭐ |

### 工具選擇

| 場景 | 工具 | 說明 |
|-----|------|------|
| **傳統ML** | Scikit-learn | 易用、完整 |
| **深度學習** | PyTorch | 靈活、研究友善 |
| **AutoML** | Auto-sklearn, Optuna | 自動化 |
| **大資料** | cuDF, RAPIDS | GPU 加速 |
| **LLM** | Ollama, Hugging Face | 模型推理 |

---

## 🚀 快速開始

### 機器學習專案流程

```python
# 1. 資料載入與探索
import pandas as pd
df = pd.read_csv('data.csv')

# 2. 資料前處理
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# 3. 模型訓練
from xgboost import XGBClassifier
model = XGBClassifier()
model.fit(X_train, y_train)

# 4. 模型評估
from sklearn.metrics import accuracy_score
y_pred = model.predict(X_test)
print(f"Accuracy: {accuracy_score(y_test, y_pred)}")

# 5. 模型儲存
import joblib
joblib.dump(model, 'model.pkl')
```

### PyTorch 深度學習流程

```python
# 1. 匯入套件
import torch
import torch.nn as nn

# 2. 定義模型
class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.fc = nn.Linear(10, 2)

    def forward(self, x):
        return self.fc(x)

# 3. 訓練模型
model = Net()
optimizer = torch.optim.Adam(model.parameters())
criterion = nn.CrossEntropyLoss()

for epoch in range(100):
    optimizer.zero_grad()
    output = model(X)
    loss = criterion(output, y)
    loss.backward()
    optimizer.step()
```

---

**最後更新**: 2025-12-01
**維護狀態**: ✅ 活躍更新
**貢獻**: 歡迎補充與修正
