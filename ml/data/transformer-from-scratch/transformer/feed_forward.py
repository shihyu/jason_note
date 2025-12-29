"""
前饋網絡（Feed Forward Network）模組

前饋網絡模塊對每個位置的表示獨立地進行非線性變換，
是 Transformer 中每個編碼器/解碼器層的第二個子層。

結構：
    Linear(d_model -> d_ff) -> ReLU -> Dropout -> Linear(d_ff -> d_model)

公式：
    FFN(x) = max(0, x * W1 + b1) * W2 + b2

其中：
- W1: 第一個線性層的權重矩陣 (d_model, d_ff)
- W2: 第二個線性層的權重矩陣 (d_ff, d_model)
- b1, b2: 偏置項
- max(0, x): ReLU 激活函數

特點：
1. 對序列中每個位置獨立應用（位置無關）
2. 先擴展維度（d_model -> d_ff），再投影回原維度（d_ff -> d_model）
3. 通過 ReLU 提供非線性能力
"""
import torch
import torch.nn as nn


class FeedForward(nn.Module):
    """
    前饋網絡層

    兩層的全連接神經網絡，中間配合 ReLU 激活函數和 Dropout。
    第一層將維度從 d_model 擴展到 d_ff（通常 d_ff = 4 * d_model），
    第二層再將維度投影回 d_model。

    這種結構為模型提供了額外的表達能力，使得每個位置的表示
    能夠經過更複雜的非線性變換。

    參數：
        d_model (int): 輸入和輸出的特徵維度（模型維度）
        d_ff (int): 隱藏層的維度（前饋網絡維度）
                   在原論文中，d_ff = 4 * d_model = 2048
        dropout (float): Dropout 機率，預設為 0.1

    輸入：
        x (Tensor): 形狀為 (batch_size, seq_len, d_model) 的輸入張量

    輸出：
        Tensor: 形狀為 (batch_size, seq_len, d_model) 的輸出張量
    """

    def __init__(self, d_model, d_ff, dropout=0.1):
        super().__init__()

        # 第一個線性層：將維度從 d_model 擴展到 d_ff
        # 輸入：(batch_size, seq_len, d_model)
        # 輸出：(batch_size, seq_len, d_ff)
        self.linear1 = nn.Linear(d_model, d_ff)

        # Dropout 層：用於正則化，防止過擬合
        self.dropout = nn.Dropout(dropout)

        # 第二個線性層：將維度從 d_ff 投影回 d_model
        # 輸入：(batch_size, seq_len, d_ff)
        # 輸出：(batch_size, seq_len, d_model)
        self.linear2 = nn.Linear(d_ff, d_model)

        # ReLU 激活函數：提供非線性能力
        # ReLU(x) = max(0, x)
        self.activation = nn.ReLU()

    def forward(self, x):
        """
        前饋網絡的前向傳播

        處理流程：
        1. 通過第一個線性層擴展維度
        2. 應用 ReLU 激活函數
        3. 應用 Dropout（訓練時隨機丟棄部分神經元）
        4. 通過第二個線性層投影回原維度

        參數：
            x (Tensor): 輸入張量，形狀為 (batch_size, seq_len, d_model)

        返回：
            Tensor: 輸出張量，形狀為 (batch_size, seq_len, d_model)
        """
        # 第一層：擴展維度
        # (batch_size, seq_len, d_model) -> (batch_size, seq_len, d_ff)
        x = self.linear1(x)

        # 應用 ReLU 激活
        # (batch_size, seq_len, d_ff) -> (batch_size, seq_len, d_ff)
        x = self.activation(x)

        # 應用 Dropout
        # (batch_size, seq_len, d_ff) -> (batch_size, seq_len, d_ff)
        x = self.dropout(x)

        # 第二層：投影回原維度
        # (batch_size, seq_len, d_ff) -> (batch_size, seq_len, d_model)
        x = self.linear2(x)

        return x
