"""
Transformer 模型

這是完整的 Transformer 模型實作，整合了所有組件：
- 詞嵌入（Embedding）
- 位置編碼（Positional Encoding）
- 編碼器（Encoder）
- 解碼器（Decoder）
- 輸出層（Output Layer）

模型架構（基於論文《Attention Is All You Need》）：

    源序列 (src)
        ↓
    詞嵌入 + 位置編碼
        ↓
    編碼器（N 層）
        ↓
    編碼器輸出（memory）
        ↓
    目標序列 (tgt) → 詞嵌入 + 位置編碼
        ↓
    解碼器（N 層，接收 memory）
        ↓
    線性投影（輸出層）
        ↓
    輸出 logits (batch_size, tgt_seq_len, tgt_vocab_size)

訓練時：
- 輸出 logits 送入損失函數（通常是交叉熵）
- 計算損失並進行反向傳播

推理時：
- 使用 softmax 將 logits 轉為機率分布
- 選擇機率最高的詞作為預測結果
- 自回歸生成（逐個生成目標序列）
"""
import torch
import torch.nn as nn
import math
from transformer.positional_encoding import PositionalEncoding
from transformer.encoder import Encoder
from transformer.decoder import Decoder


class Transformer(nn.Module):
    """
    完整的 Transformer 模型

    將編碼器-解碼器架構整合在一起，
    包括詞嵌入、位置編碼和輸出投影層。

    參數：
        src_vocab_size (int): 源語言詞彙表大小
        tgt_vocab_size (int): 目標語言詞彙表大小
        d_model (int): 模型的特徵維度，預設為 512
        n_heads (int): 注意力頭的數量，預設為 8
        d_ff (int): 前饋網絡隱藏層的維度，預設為 2048
        num_layers (int): 編碼器和解碼器的層數，預設為 6
        dropout (float): Dropout 機率，預設為 0.1

    輸入：
        src (Tensor): 源序列，形狀為 (batch_size, src_seq_len)
                     每個元素是詞彙表中的索引
        tgt (Tensor): 目標序列，形狀為 (batch_size, tgt_seq_len)
                     每個元素是詞彙表中的索引
        src_mask (Tensor, optional): 源序列遮罩
        tgt_mask (Tensor, optional): 目標序列遮罩

    輸出：
        Tensor: 輸出 logits，形狀為 (batch_size, tgt_seq_len, tgt_vocab_size)
               每個位置的輸出是詞彙表大小的向量（未經 softmax）
    """

    def __init__(
        self,
        src_vocab_size,
        tgt_vocab_size,
        d_model=512,
        n_heads=8,
        d_ff=2048,
        num_layers=6,
        dropout=0.1
    ):
        super().__init__()

        # ===== 詞嵌入層 =====
        # 將詞索引映射為 d_model 維的向量

        # 編碼器詞嵌入：將源語言的詞索引轉為向量
        self.encoder_embedding = nn.Embedding(src_vocab_size, d_model)

        # 解碼器詞嵌入：將目標語言的詞索引轉為向量
        self.decoder_embedding = nn.Embedding(tgt_vocab_size, d_model)

        # ===== 位置編碼 =====
        # 為序列中的每個位置添加位置資訊
        # 編碼器和解碼器共用同一個位置編碼模組
        self.positional_encoding = PositionalEncoding(d_model)

        # ===== Dropout 層 =====
        # 在嵌入之後應用 dropout，用於正則化
        self.dropout = nn.Dropout(dropout)

        # ===== 編碼器 =====
        # 由 num_layers 個編碼器層堆疊而成
        self.encoder = Encoder(d_model, n_heads, d_ff, num_layers, dropout)

        # ===== 解碼器 =====
        # 由 num_layers 個解碼器層堆疊而成
        self.decoder = Decoder(d_model, n_heads, d_ff, num_layers, dropout)

        # ===== 輸出層 =====
        # 將解碼器輸出投影到目標詞彙表大小
        # 形狀：(d_model) -> (tgt_vocab_size)
        self.fc_out = nn.Linear(d_model, tgt_vocab_size)

    def forward(self, src, tgt, src_mask=None, tgt_mask=None):
        """
        Transformer 的前向傳播

        處理流程：
        1. 源序列詞嵌入 + 縮放 + Dropout + 位置編碼
        2. 通過編碼器得到編碼器輸出（memory）
        3. 目標序列詞嵌入 + 縮放 + Dropout + 位置編碼
        4. 通過解碼器（使用 memory）得到解碼器輸出
        5. 通過輸出層得到最終 logits

        參數：
            src (Tensor): 源序列，形狀為 (batch_size, src_seq_len)
            tgt (Tensor): 目標序列，形狀為 (batch_size, tgt_seq_len)
            src_mask (Tensor, optional): 源序列遮罩
            tgt_mask (Tensor, optional): 目標序列遮罩

        返回：
            Tensor: 輸出 logits，形狀為 (batch_size, tgt_seq_len, tgt_vocab_size)
        """
        # ===== 編碼器部分 =====

        # 1. 源序列詞嵌入
        # (batch_size, src_seq_len) -> (batch_size, src_seq_len, d_model)
        src = self.encoder_embedding(src)

        # 2. 縮放詞嵌入
        # 論文中建議將嵌入向量乘以 sqrt(d_model)
        # 這樣可以穩定訓練，使得嵌入和位置編碼的幅度相當
        src = src * math.sqrt(self.encoder_embedding.embedding_dim)

        # 3. 應用 Dropout
        src = self.dropout(src)

        # 4. 添加位置編碼
        # (batch_size, src_seq_len, d_model) -> (batch_size, src_seq_len, d_model)
        src = self.positional_encoding(src)

        # 5. 通過編碼器
        # 輸出形狀：(batch_size, src_seq_len, d_model)
        enc_output = self.encoder(src, src_mask)

        # ===== 解碼器部分 =====

        # 1. 目標序列詞嵌入
        # (batch_size, tgt_seq_len) -> (batch_size, tgt_seq_len, d_model)
        tgt = self.decoder_embedding(tgt)

        # 2. 縮放詞嵌入
        tgt = tgt * math.sqrt(self.decoder_embedding.embedding_dim)

        # 3. 應用 Dropout
        tgt = self.dropout(tgt)

        # 4. 添加位置編碼
        # (batch_size, tgt_seq_len, d_model) -> (batch_size, tgt_seq_len, d_model)
        tgt = self.positional_encoding(tgt)

        # 5. 通過解碼器
        # 輸入：目標序列和編碼器輸出（memory）
        # 輸出形狀：(batch_size, tgt_seq_len, d_model)
        dec_output = self.decoder(tgt, enc_output, tgt_mask, src_mask)

        # ===== 輸出層 =====

        # 將解碼器輸出投影到詞彙表大小
        # (batch_size, tgt_seq_len, d_model) -> (batch_size, tgt_seq_len, tgt_vocab_size)
        output = self.fc_out(dec_output)

        return output
