"""
Transformer 解碼器（Decoder）模組

解碼器負責根據編碼器的輸出和目標序列生成最終的輸出。
解碼器由多個相同的解碼器層（DecoderLayer）堆疊而成。

每個解碼器層包含三個子層：
1. 多頭自注意力機制（Masked Multi-Head Self-Attention）
2. 多頭交叉注意力機制（Multi-Head Cross-Attention）
3. 前饋網絡（Feed-Forward Network）

每個子層都使用了：
- 殘差連接（Residual Connection）
- 層歸一化（Layer Normalization）

結構（每一層）：
    tgt -> [Masked Self-Attention -> Add & Norm]
        -> [Cross-Attention with Encoder -> Add & Norm]
        -> [FFN -> Add & Norm]
        -> output

其中：
- Masked Self-Attention: 使用遮罩防止看到未來的詞
- Cross-Attention: Query 來自解碼器，Key 和 Value 來自編碼器輸出
"""
import torch
import torch.nn as nn
from transformer.multi_head_attention import MultiHeadAttention
from transformer.feed_forward import FeedForward


class DecoderLayer(nn.Module):
    """
    解碼器層（Decoder Layer）

    解碼器的基本單元，包含自注意力、交叉注意力和前饋網絡三個子層，
    各自配備殘差連接和層歸一化。

    參數：
        d_model (int): 模型的特徵維度
        n_heads (int): 注意力頭的數量
        d_ff (int): 前饋網絡隱藏層的維度
        dropout (float): Dropout 機率，預設為 0.1

    輸入：
        tgt (Tensor): 目標序列張量，形狀為 (batch_size, tgt_seq_len, d_model)
        src (Tensor): 編碼器輸出（memory），形狀為 (batch_size, src_seq_len, d_model)
        tgt_mask (Tensor, optional): 目標序列遮罩，用於遮蔽未來的詞
        src_mask (Tensor, optional): 源序列遮罩，用於遮蔽填充位置

    輸出：
        Tensor: 輸出張量，形狀為 (batch_size, tgt_seq_len, d_model)
    """

    def __init__(self, d_model, n_heads, d_ff, dropout=0.1):
        super().__init__()

        # 第一個子層：多頭自注意力
        # 用於計算目標序列內部各位置之間的注意力
        # 使用遮罩防止看到未來的詞
        self.self_attn = MultiHeadAttention(d_model, n_heads, dropout)

        # 自注意力子層的 Dropout 和 LayerNorm
        self.dropout1 = nn.Dropout(dropout)
        self.norm1 = nn.LayerNorm(d_model)

        # 第二個子層：多頭交叉注意力
        # Query 來自解碼器當前狀態，Key 和 Value 來自編碼器輸出
        # 用於從編碼器提取相關資訊
        self.cross_attn = MultiHeadAttention(d_model, n_heads, dropout)

        # 交叉注意力子層的 Dropout 和 LayerNorm
        self.dropout2 = nn.Dropout(dropout)
        self.norm2 = nn.LayerNorm(d_model)

        # 第三個子層：前饋網絡
        # 對每個位置的表示進行非線性變換
        self.ffn = FeedForward(d_model, d_ff, dropout)

        # 前饋網絡子層的 Dropout 和 LayerNorm
        self.dropout3 = nn.Dropout(dropout)
        self.norm3 = nn.LayerNorm(d_model)

    def forward(self, tgt, src, tgt_mask=None, src_mask=None):
        """
        解碼器層的前向傳播

        處理流程：
        1. 自注意力子層：tgt -> Masked Self-Attention -> Dropout -> Add & Norm
        2. 交叉注意力子層：x -> Cross-Attention(Q=x, K=src, V=src) -> Dropout -> Add & Norm
        3. 前饋網絡子層：x -> FFN -> Dropout -> Add & Norm

        參數：
            tgt (Tensor): 目標序列，形狀為 (batch_size, tgt_seq_len, d_model)
            src (Tensor): 編碼器輸出（memory），形狀為 (batch_size, src_seq_len, d_model)
            tgt_mask (Tensor, optional): 目標序列遮罩（用於遮蔽未來詞）
            src_mask (Tensor, optional): 源序列遮罩（用於遮蔽填充）

        返回：
            Tensor: 輸出張量，形狀為 (batch_size, tgt_seq_len, d_model)
        """
        # 保存輸入用於殘差連接
        x = tgt

        # 第一個子層：多頭自注意力（帶遮罩）
        # 自注意力：Q = K = V = x
        # 使用 tgt_mask 遮蔽未來的詞（look-ahead mask）
        # 輸出形狀：(batch_size, tgt_seq_len, d_model)
        output = self.self_attn(x, x, x, tgt_mask)

        # 殘差連接 + LayerNorm
        x = self.norm1(x + self.dropout1(output))

        # 第二個子層：多頭交叉注意力
        # Query 來自解碼器當前狀態 x
        # Key 和 Value 來自編碼器輸出 src (memory)
        # 使用 src_mask 遮蔽編碼器中的填充位置
        # 輸出形狀：(batch_size, tgt_seq_len, d_model)
        output = self.cross_attn(x, src, src, src_mask)

        # 殘差連接 + LayerNorm
        x = self.norm2(x + self.dropout2(output))

        # 第三個子層：前饋網絡
        # 輸出形狀：(batch_size, tgt_seq_len, d_model)
        output = self.ffn(x)

        # 殘差連接 + LayerNorm
        x = self.norm3(x + self.dropout3(output))

        return x


class Decoder(nn.Module):
    """
    Transformer 解碼器（Decoder）

    由多個解碼器層（DecoderLayer）堆疊而成。
    解碼器根據編碼器輸出和目標序列生成最終輸出。

    參數：
        d_model (int): 模型的特徵維度
        n_heads (int): 注意力頭的數量
        d_ff (int): 前饋網絡隱藏層的維度
        num_layers (int): 解碼器層的數量
        dropout (float): Dropout 機率，預設為 0.1

    輸入：
        x (Tensor): 目標序列張量，形狀為 (batch_size, tgt_seq_len, d_model)
        memory (Tensor): 編碼器輸出，形狀為 (batch_size, src_seq_len, d_model)
        tgt_mask (Tensor, optional): 目標序列遮罩
        memory_mask (Tensor, optional): 編碼器輸出遮罩

    輸出：
        Tensor: 解碼器輸出張量，形狀為 (batch_size, tgt_seq_len, d_model)
    """

    def __init__(self, d_model, n_heads, d_ff, num_layers, dropout=0.1):
        super().__init__()

        # 堆疊多個解碼器層
        # 使用 nn.ModuleList 以便 PyTorch 正確註冊這些層
        self.layers = nn.ModuleList(
            [DecoderLayer(d_model, n_heads, d_ff, dropout) for _ in range(num_layers)]
        )

    def forward(self, x, memory, tgt_mask=None, memory_mask=None):
        """
        解碼器的前向傳播

        將目標序列和編碼器輸出依次通過每一層解碼器層。

        參數：
            x (Tensor): 目標序列，形狀為 (batch_size, tgt_seq_len, d_model)
            memory (Tensor): 編碼器輸出，形狀為 (batch_size, src_seq_len, d_model)
            tgt_mask (Tensor, optional): 目標序列遮罩（用於遮蔽未來詞）
            memory_mask (Tensor, optional): 編碼器輸出遮罩（用於遮蔽填充）

        返回：
            Tensor: 解碼器輸出張量，形狀為 (batch_size, tgt_seq_len, d_model)
        """
        # 依次通過每一層解碼器層
        for layer in self.layers:
            x = layer(x, memory, tgt_mask, memory_mask)

        return x
