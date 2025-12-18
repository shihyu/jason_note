"""
Transformer 編碼器（Encoder）模組

編碼器負責將輸入序列編碼成高層次的表示，供解碼器使用。
編碼器由多個相同的編碼器層（EncoderLayer）堆疊而成。

每個編碼器層包含兩個子層：
1. 多頭自注意力機制（Multi-Head Self-Attention）
2. 前饋網絡（Feed-Forward Network）

每個子層都使用了：
- 殘差連接（Residual Connection）
- 層歸一化（Layer Normalization）

結構（每一層）：
    x -> [Self-Attention -> Add & Norm] -> [FFN -> Add & Norm] -> output

其中 Add & Norm 表示：
    LayerNorm(x + Sublayer(x))
"""
import torch
import torch.nn as nn
from transformer.multi_head_attention import MultiHeadAttention
from transformer.feed_forward import FeedForward


class EncoderLayer(nn.Module):
    """
    編碼器層（Encoder Layer）

    編碼器的基本單元，包含自注意力和前饋網絡兩個子層，
    各自配備殘差連接和層歸一化。

    參數：
        d_model (int): 模型的特徵維度
        n_heads (int): 注意力頭的數量
        d_ff (int): 前饋網絡隱藏層的維度
        dropout (float): Dropout 機率，預設為 0.1

    輸入：
        x (Tensor): 輸入張量，形狀為 (batch_size, seq_len, d_model)
        mask (Tensor, optional): 遮罩張量，用於遮蔽填充位置

    輸出：
        Tensor: 輸出張量，形狀為 (batch_size, seq_len, d_model)
    """

    def __init__(self, d_model, n_heads, d_ff, dropout=0.1):
        super().__init__()

        # 多頭自注意力子層
        # 用於計算輸入序列內部各位置之間的注意力
        self.self_attn = MultiHeadAttention(d_model, n_heads, dropout)

        # 自注意力子層的 Dropout 和 LayerNorm
        self.dropout1 = nn.Dropout(dropout)
        self.norm1 = nn.LayerNorm(d_model)

        # 前饋網絡子層
        # 對每個位置的表示進行非線性變換
        self.ffn = FeedForward(d_model, d_ff, dropout)

        # 前饋網絡子層的 Dropout 和 LayerNorm
        self.dropout2 = nn.Dropout(dropout)
        self.norm2 = nn.LayerNorm(d_model)

    def forward(self, x, mask=None):
        """
        編碼器層的前向傳播

        處理流程：
        1. 自注意力子層：x -> Self-Attention -> Dropout -> Add & Norm
        2. 前饋網絡子層：x -> FFN -> Dropout -> Add & Norm

        參數：
            x (Tensor): 輸入張量，形狀為 (batch_size, seq_len, d_model)
            mask (Tensor, optional): 遮罩張量

        返回：
            Tensor: 輸出張量，形狀為 (batch_size, seq_len, d_model)
        """
        # 第一個子層：多頭自注意力
        # 自注意力：Q = K = V = x
        # 輸出形狀：(batch_size, seq_len, d_model)
        attn_output = self.self_attn(x, x, x, mask)

        # 殘差連接 + LayerNorm
        # x + dropout(attn_output) 是殘差連接
        # norm1 進行層歸一化
        x = self.norm1(x + self.dropout1(attn_output))

        # 第二個子層：前饋網絡
        # 輸出形狀：(batch_size, seq_len, d_model)
        ffn_output = self.ffn(x)

        # 殘差連接 + LayerNorm
        x = self.norm2(x + self.dropout2(ffn_output))

        return x


class Encoder(nn.Module):
    """
    Transformer 編碼器（Encoder）

    由多個編碼器層（EncoderLayer）堆疊而成。
    編碼器將輸入序列編碼成高層次的表示。

    參數：
        d_model (int): 模型的特徵維度
        n_heads (int): 注意力頭的數量
        d_ff (int): 前饋網絡隱藏層的維度
        num_layers (int): 編碼器層的數量
        dropout (float): Dropout 機率，預設為 0.1

    輸入：
        x (Tensor): 輸入張量，形狀為 (batch_size, seq_len, d_model)
        mask (Tensor, optional): 遮罩張量

    輸出：
        Tensor: 編碼器輸出張量，形狀為 (batch_size, seq_len, d_model)
    """

    def __init__(self, d_model, n_heads, d_ff, num_layers, dropout=0.1):
        super().__init__()

        # 堆疊多個編碼器層
        # 使用 nn.ModuleList 以便 PyTorch 正確註冊這些層
        self.layers = nn.ModuleList(
            [EncoderLayer(d_model, n_heads, d_ff, dropout) for _ in range(num_layers)]
        )

        # 最終的層歸一化
        # 在所有編碼器層之後進行一次歸一化
        self.norm = nn.LayerNorm(d_model)

    def forward(self, x, mask=None):
        """
        編碼器的前向傳播

        將輸入依次通過每一層編碼器層，最後進行歸一化。

        參數：
            x (Tensor): 輸入張量，形狀為 (batch_size, seq_len, d_model)
            mask (Tensor, optional): 遮罩張量

        返回：
            Tensor: 編碼器輸出張量，形狀為 (batch_size, seq_len, d_model)
        """
        # 依次通過每一層編碼器層
        for layer in self.layers:
            x = layer(x, mask)

        # 最終的層歸一化
        x = self.norm(x)

        return x
