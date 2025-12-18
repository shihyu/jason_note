# Transformer From Scratch

> 基於論文《Attention Is All You Need》的 PyTorch 純手工實作

一個完整、模組化、易於理解的 Transformer 模型實作，包含完整的測試覆蓋和繁體中文註解。

## 特色

- **純 PyTorch 實作**：不依賴第三方高階框架，便於學習和修改
- **完整測試覆蓋**：69 個單元測試，涵蓋所有核心組件
- **模組化設計**：每個組件都可以獨立使用和測試
- **繁體中文註解**：所有程式碼都有詳細的繁體中文註解
- **TDD 開發**：遵循測試驅動開發（Test-Driven Development）
- **batch-first 格式**：符合 PyTorch 常用的資料佈局

## 專案結構

```
transformer-from-scratch/
├── transformer/                     # 核心程式碼
│   ├── __init__.py
│   ├── positional_encoding.py      # 位置編碼
│   ├── multi_head_attention.py     # 多頭注意力機制
│   ├── feed_forward.py             # 前饋網絡
│   ├── encoder.py                  # 編碼器
│   ├── decoder.py                  # 解碼器
│   ├── mask.py                     # 遮罩生成函數
│   └── model.py                    # 完整 Transformer 模型
├── tests/                          # 測試檔案
│   ├── __init__.py
│   ├── test_positional_encoding.py
│   ├── test_multi_head_attention.py
│   ├── test_feed_forward.py
│   ├── test_encoder.py
│   ├── test_decoder.py
│   ├── test_mask.py
│   └── test_model.py
├── Makefile                        # 建置工具
├── requirements.txt                # Python 依賴
└── README.md                       # 專案說明
```

## 快速開始

### 1. 安裝依賴

```bash
make setup
```

或手動安裝：

```bash
pip install -r requirements.txt
```

### 2. 執行測試

```bash
# 執行所有測試
make test

# 執行測試（詳細輸出）
make test-verbose
```

### 3. 使用範例

```python
import torch
from transformer.model import Transformer
from transformer.mask import create_padding_mask

# 建立模型（使用論文中的配置）
model = Transformer(
    src_vocab_size=10000,  # 源語言詞彙表大小
    tgt_vocab_size=10000,  # 目標語言詞彙表大小
    d_model=512,           # 模型維度
    n_heads=8,             # 注意力頭數量
    d_ff=2048,             # 前饋網絡隱藏層維度
    num_layers=6,          # 編碼器/解碼器層數
    dropout=0.1            # Dropout 機率
)

# 建立輸入資料
batch_size = 32
src_seq_len = 10
tgt_seq_len = 12

src = torch.randint(0, 10000, (batch_size, src_seq_len))
tgt = torch.randint(0, 10000, (batch_size, tgt_seq_len))

# 建立遮罩（遮蔽填充位置和未來詞）
src_mask, tgt_mask = create_padding_mask(src, tgt, pad_idx=0)

# 前向傳播
output = model(src, tgt, src_mask, tgt_mask)
# 輸出形狀：(32, 12, 10000)

print(f"輸出形狀: {output.shape}")
# 輸出形狀: torch.Size([32, 12, 10000])
```

## 核心組件

### 1. Positional Encoding（位置編碼）

為序列中的每個位置添加位置資訊，使用正弦和餘弦函數。

```python
from transformer.positional_encoding import PositionalEncoding

pe = PositionalEncoding(d_model=512, max_len=5000)
x = torch.randn(32, 10, 512)  # (batch_size, seq_len, d_model)
output = pe(x)
```

### 2. Multi-Head Attention（多頭注意力）

允許模型在不同的表示子空間中關注序列的不同位置。

```python
from transformer.multi_head_attention import MultiHeadAttention

mha = MultiHeadAttention(d_model=512, n_heads=8)
Q = K = V = torch.randn(32, 10, 512)
output = mha(Q, K, V)
```

### 3. Feed Forward Network（前饋網絡）

對每個位置的表示進行非線性變換。

```python
from transformer.feed_forward import FeedForward

ffn = FeedForward(d_model=512, d_ff=2048)
x = torch.randn(32, 10, 512)
output = ffn(x)
```

### 4. Encoder（編碼器）

將輸入序列編碼成高層次的表示。

```python
from transformer.encoder import Encoder

encoder = Encoder(d_model=512, n_heads=8, d_ff=2048, num_layers=6)
x = torch.randn(32, 10, 512)
output = encoder(x)
```

### 5. Decoder（解碼器）

根據編碼器輸出和目標序列生成最終輸出。

```python
from transformer.decoder import Decoder

decoder = Decoder(d_model=512, n_heads=8, d_ff=2048, num_layers=6)
tgt = torch.randn(32, 12, 512)
memory = torch.randn(32, 10, 512)  # 編碼器輸出
output = decoder(tgt, memory)
```

### 6. Mask Functions（遮罩函數）

生成填充遮罩和未來遮罩。

```python
from transformer.mask import create_padding_mask

src = torch.tensor([[1, 2, 3, 0, 0]])  # 0 是填充符號
tgt = torch.tensor([[1, 2, 3, 0]])

src_mask, tgt_mask = create_padding_mask(src, tgt, pad_idx=0)
```

## 測試

專案包含 69 個單元測試，測試覆蓋所有核心組件：

```bash
# 執行所有測試
pytest tests/ -v

# 執行特定測試檔案
pytest tests/test_model.py -v

# 執行測試並顯示覆蓋率
pytest tests/ --cov=transformer
```

測試統計：
- ✅ 6 個 PositionalEncoding 測試
- ✅ 10 個 MultiHeadAttention 測試
- ✅ 10 個 FeedForward 測試
- ✅ 12 個 Encoder 測試
- ✅ 12 個 Decoder 測試
- ✅ 9 個 Mask 測試
- ✅ 10 個 Transformer 模型測試

**總計：69/69 測試通過 ✅**

## Makefile 指令

```bash
make          # 顯示可用指令
make setup    # 安裝專案依賴
make test     # 執行所有測試
make clean    # 清理暫存檔案
```

## 技術細節

### 模型配置（論文標準）

- **d_model**: 512（模型維度）
- **n_heads**: 8（注意力頭數量）
- **d_ff**: 2048（前饋網絡隱藏層維度）
- **num_layers**: 6（編碼器/解碼器層數）
- **dropout**: 0.1（Dropout 機率）

### 架構特點

1. **殘差連接**：每個子層都使用殘差連接
2. **層歸一化**：每個子層後都進行 LayerNorm
3. **位置編碼**：使用正弦/餘弦函數的固定位置編碼
4. **縮放點積注意力**：注意力分數除以 √d_k
5. **遮罩機制**：支援填充遮罩和未來遮罩

## 環境需求

- Python >= 3.9
- PyTorch >= 2.0
- pytest >= 7.0
- numpy >= 1.24

## 參考資料

- 論文：[Attention Is All You Need](https://arxiv.org/abs/1706.03762)
- PyTorch 官方文檔：[torch.nn.Transformer](https://pytorch.org/docs/stable/generated/torch.nn.Transformer.html)

## 授權

MIT License

## 貢獻

歡迎提出 Issue 或 Pull Request！

## 作者

使用 TDD 方法從零開始實作，所有程式碼都經過完整測試驗證。
