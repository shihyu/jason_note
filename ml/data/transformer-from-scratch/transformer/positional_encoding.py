"""
位置編碼（Positional Encoding）模組

Transformer 模型使用位置編碼為序列中的每個位置添加位置資訊。
由於 Transformer 完全依賴注意力機制，缺乏對序列順序的內在建模能力，
需要在輸入的詞嵌入中加入位置編碼以讓模型識別不同的位置。

這裡採用正弦和餘弦函數生成固定的位置編碼，與原始論文中的方法一致：
- PE(pos, 2i) = sin(pos / 10000^(2i/d_model))
- PE(pos, 2i+1) = cos(pos / 10000^(2i/d_model))

其中：
- pos: 位置索引（0 到 max_len-1）
- i: 維度索引（0 到 d_model-1）
- d_model: 模型的特徵維度
"""
import torch
import torch.nn as nn
import math


class PositionalEncoding(nn.Module):
    """
    位置編碼層

    使用正弦和餘弦函數為序列中的每個位置生成位置編碼。
    位置編碼會被加到輸入的詞嵌入向量上，為模型提供位置資訊。

    參數：
        d_model (int): 模型的特徵維度（詞嵌入的維度）
        max_len (int): 支援的最大序列長度，預設為 5000

    輸入：
        x (Tensor): 形狀為 (batch_size, seq_len, d_model) 的輸入張量

    輸出：
        Tensor: 形狀為 (batch_size, seq_len, d_model) 的輸出張量
                輸出 = 輸入 + 位置編碼
    """

    def __init__(self, d_model, max_len=5000):
        super().__init__()

        # 建立位置索引張量：[0, 1, 2, ..., max_len-1]
        # 形狀：(max_len, 1)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)

        # 計算縮放因子 div_term
        # div_term = 1 / (10000^(2i/d_model)) = exp(-2i * log(10000) / d_model)
        # 只需要計算偶數索引（0, 2, 4, ...），因為奇數索引使用相同的 div_term
        # 形狀：(d_model/2,)
        div_term = torch.exp(
            torch.arange(0, d_model, 2).float() * -(math.log(10000.0) / d_model)
        )

        # 初始化位置編碼張量
        # 形狀：(1, max_len, d_model)
        # 第一個維度為 1，方便後續與 batch 廣播
        pe = torch.zeros(1, max_len, d_model)

        # 填充偶數維度：使用 sin 函數
        # pe[0, :, 0::2] 表示取第 0 個 batch、所有位置、偶數維度（0, 2, 4, ...）
        pe[0, :, 0::2] = torch.sin(position * div_term)

        # 填充奇數維度：使用 cos 函數
        # pe[0, :, 1::2] 表示取第 0 個 batch、所有位置、奇數維度（1, 3, 5, ...）
        pe[0, :, 1::2] = torch.cos(position * div_term)

        # 將位置編碼註冊為緩衝區（buffer）
        # 緩衝區不是可訓練參數，但會隨著模型一起保存和移動（CPU/GPU）
        self.register_buffer('pe', pe)

    def forward(self, x):
        """
        前向傳播：將位置編碼加到輸入張量上

        參數：
            x (Tensor): 輸入張量，形狀為 (batch_size, seq_len, d_model)

        返回：
            Tensor: 輸出張量，形狀為 (batch_size, seq_len, d_model)
        """
        # 將位置編碼加到輸入上
        # self.pe[:, :x.size(1), :] 選取前 seq_len 個位置的編碼
        # 由於 self.pe 的第一個維度是 1，會自動廣播到 batch_size
        x = x + self.pe[:, :x.size(1), :]
        return x
