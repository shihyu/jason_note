"""
多頭注意力機制（Multi-Head Attention）模組

多頭注意力機制允許模型在不同的子空間中對序列的不同位置進行關注，
從而綜合不同的位置關係資訊。

核心概念：
1. 將輸入投影到多個子空間（多個頭）
2. 在每個子空間中獨立計算注意力
3. 將所有頭的輸出拼接起來
4. 通過線性變換得到最終輸出

注意力計算公式：
    Attention(Q, K, V) = softmax(Q * K^T / sqrt(d_k)) * V

多頭注意力公式：
    MultiHead(Q, K, V) = Concat(head_1, ..., head_h) * W_O
    其中 head_i = Attention(Q * W_Q^i, K * W_K^i, V * W_V^i)
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
import math


class MultiHeadAttention(nn.Module):
    """
    多頭注意力層

    將輸入分割成多個注意力頭，每個頭在不同的表示子空間中學習注意力模式。
    這使得模型能夠同時關注序列中不同位置的不同方面的資訊。

    參數：
        d_model (int): 模型的特徵維度
        n_heads (int): 注意力頭的數量
        dropout (float): Dropout 機率，預設為 0.1

    輸入：
        Q (Tensor): 查詢張量，形狀為 (batch_size, seq_len_q, d_model)
        K (Tensor): 鍵張量，形狀為 (batch_size, seq_len_k, d_model)
        V (Tensor): 值張量，形狀為 (batch_size, seq_len_v, d_model)
                   註：seq_len_k 必須等於 seq_len_v
        mask (Tensor, optional): 遮罩張量，形狀為 (batch_size, 1, seq_len_q, seq_len_k)
                                或可廣播的形狀

    輸出：
        Tensor: 形狀為 (batch_size, seq_len_q, d_model) 的輸出張量
    """

    def __init__(self, d_model, n_heads, dropout=0.1):
        super().__init__()
        self.d_model = d_model
        self.n_heads = n_heads
        self.d_k = d_model // n_heads

        # 確保 d_model 可以被 n_heads 整除
        assert (
            self.d_k * n_heads == d_model
        ), f"d_model {d_model} 無法被 n_heads {n_heads} 整除"

        # 定義線性投影層（不使用 bias，與原論文一致）
        # W_q, W_k, W_v: 將輸入投影到查詢、鍵、值空間
        self.W_q = nn.Linear(d_model, d_model, bias=False)
        self.W_k = nn.Linear(d_model, d_model, bias=False)
        self.W_v = nn.Linear(d_model, d_model, bias=False)

        # W_o: 將多頭輸出投影回 d_model 維度
        self.W_o = nn.Linear(d_model, d_model)

        # Dropout 層，用於注意力權重
        self.dropout = nn.Dropout(dropout)

    def scaled_dot_product_attention(self, Q, K, V, mask=None):
        """
        縮放點積注意力（Scaled Dot-Product Attention）

        計算步驟：
        1. 計算注意力分數：Q * K^T / sqrt(d_k)
        2. 應用遮罩（如果提供）
        3. 應用 softmax 得到注意力權重
        4. 應用 dropout
        5. 使用注意力權重對 V 進行加權求和

        參數：
            Q (Tensor): 查詢張量，形狀為 (batch_size, n_heads, seq_len_q, d_k)
            K (Tensor): 鍵張量，形狀為 (batch_size, n_heads, seq_len_k, d_k)
            V (Tensor): 值張量，形狀為 (batch_size, n_heads, seq_len_v, d_k)
            mask (Tensor, optional): 遮罩張量，0 表示需要遮蔽的位置

        返回：
            Tensor: 注意力輸出，形狀為 (batch_size, n_heads, seq_len_q, d_k)
        """
        # 計算注意力分數
        # Q @ K^T: (batch_size, n_heads, seq_len_q, d_k) @ (batch_size, n_heads, d_k, seq_len_k)
        #        = (batch_size, n_heads, seq_len_q, seq_len_k)
        scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(self.d_k)

        # 應用遮罩
        if mask is not None:
            # 將遮罩為 0 的位置設為極小值，使得 softmax 後接近 0
            scores = scores.masked_fill(mask == 0, -1e9)

        # 計算注意力權重（在最後一個維度上進行 softmax）
        # 形狀：(batch_size, n_heads, seq_len_q, seq_len_k)
        attn_weights = F.softmax(scores, dim=-1)

        # 應用 dropout
        attn_weights = self.dropout(attn_weights)

        # 使用注意力權重對值進行加權求和
        # attn_weights @ V: (batch_size, n_heads, seq_len_q, seq_len_k) @ (batch_size, n_heads, seq_len_k, d_k)
        #                 = (batch_size, n_heads, seq_len_q, d_k)
        output = torch.matmul(attn_weights, V)

        return output

    def forward(self, Q, K, V, mask=None):
        """
        多頭注意力的前向傳播

        參數：
            Q (Tensor): 查詢張量，形狀為 (batch_size, seq_len_q, d_model)
            K (Tensor): 鍵張量，形狀為 (batch_size, seq_len_k, d_model)
            V (Tensor): 值張量，形狀為 (batch_size, seq_len_v, d_model)
            mask (Tensor, optional): 遮罩張量

        返回：
            Tensor: 輸出張量，形狀為 (batch_size, seq_len_q, d_model)
        """
        batch_size = Q.size(0)

        # 線性投影並重塑為多頭格式
        # (batch_size, seq_len, d_model) -> (batch_size, seq_len, n_heads, d_k)
        # -> (batch_size, n_heads, seq_len, d_k)

        # 投影 Q, K, V
        Q = self.W_q(Q).view(batch_size, -1, self.n_heads, self.d_k).transpose(1, 2)
        K = self.W_k(K).view(batch_size, -1, self.n_heads, self.d_k).transpose(1, 2)
        V = self.W_v(V).view(batch_size, -1, self.n_heads, self.d_k).transpose(1, 2)

        # 計算縮放點積注意力
        # 輸出形狀：(batch_size, n_heads, seq_len_q, d_k)
        attn_output = self.scaled_dot_product_attention(Q, K, V, mask)

        # 將多頭輸出拼接回 d_model 維度
        # (batch_size, n_heads, seq_len_q, d_k) -> (batch_size, seq_len_q, n_heads, d_k)
        # -> (batch_size, seq_len_q, d_model)
        attn_output = (
            attn_output.transpose(1, 2)
            .contiguous()
            .view(batch_size, -1, self.d_model)
        )

        # 通過輸出投影層
        output = self.W_o(attn_output)

        return output
