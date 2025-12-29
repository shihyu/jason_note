"""
遮罩（Mask）生成函數

在 Transformer 中，遮罩用於：
1. **填充遮罩（Padding Mask）**：遮蔽序列中的填充位置
   - 防止模型關注填充符號
   - 適用於編碼器和解碼器的填充位置

2. **未來遮罩（Look-ahead Mask）**：遮蔽未來的詞
   - 防止解碼器在生成當前詞時看到未來的詞
   - 僅適用於解碼器的自注意力層
   - 通常是下三角矩陣

本模組提供生成這些遮罩的函數。
"""
import torch


def create_padding_mask(src, tgt, pad_idx=0):
    """
    建立填充遮罩和未來遮罩

    為源序列和目標序列生成遮罩張量：
    - 源序列遮罩（src_mask）：遮蔽填充位置
    - 目標序列遮罩（tgt_mask）：同時遮蔽填充位置和未來詞

    參數：
        src (Tensor): 源序列張量，形狀為 (batch_size, src_seq_len)
                     每個元素是詞彙表中的索引
        tgt (Tensor): 目標序列張量，形狀為 (batch_size, tgt_seq_len)
                     每個元素是詞彙表中的索引
        pad_idx (int): 填充符號的索引，預設為 0
                      在序列中，pad_idx 的位置會被遮蔽

    返回：
        tuple: (src_mask, tgt_mask)
            - src_mask: 源序列遮罩，形狀為 (batch_size, 1, 1, src_seq_len)
                       True 表示允許關注，False 表示遮蔽
            - tgt_mask: 目標序列遮罩，形狀為 (batch_size, 1, tgt_seq_len, tgt_seq_len)
                       結合了填充遮罩和未來遮罩

    範例：
        >>> src = torch.tensor([[1, 2, 3, 0, 0]])  # 0 是填充
        >>> tgt = torch.tensor([[1, 2, 3, 0]])
        >>> src_mask, tgt_mask = create_padding_mask(src, tgt)
        >>> print(src_mask.shape)  # (1, 1, 1, 5)
        >>> print(tgt_mask.shape)  # (1, 1, 4, 4)
    """
    # ===== 建立源序列填充遮罩 =====
    # src != pad_idx: 創建布林張量，True 表示非填充位置
    # unsqueeze(1).unsqueeze(2): 添加兩個維度以便廣播
    # 最終形狀：(batch_size, 1, 1, src_seq_len)
    src_mask = (src != pad_idx).unsqueeze(1).unsqueeze(2)

    # ===== 建立目標序列填充遮罩 =====
    # tgt != pad_idx: 創建布林張量，True 表示非填充位置
    # unsqueeze(1).unsqueeze(3): 添加維度以便與 look-ahead mask 結合
    # 最終形狀：(batch_size, 1, tgt_seq_len, 1)
    tgt_mask = (tgt != pad_idx).unsqueeze(1).unsqueeze(3)

    # ===== 建立未來遮罩（Look-ahead Mask）=====
    # 創建下三角矩陣，防止看到未來的詞
    tgt_len = tgt.size(1)

    # torch.ones: 創建全 1 的矩陣
    # tril(): 保留下三角部分（包括對角線），上三角部分設為 0
    # bool(): 轉換為布林類型
    # unsqueeze(0).unsqueeze(0): 添加 batch 和 head 維度
    # 最終形狀：(1, 1, tgt_len, tgt_len)
    look_ahead_mask = torch.ones(tgt_len, tgt_len).tril().bool().unsqueeze(0).unsqueeze(0)

    # 將 look-ahead mask 移到與 tgt 相同的設備（CPU 或 GPU）
    look_ahead_mask = look_ahead_mask.to(tgt.device)

    # ===== 合併目標序列的填充遮罩和未來遮罩 =====
    # 使用邏輯與（&）運算符合併兩個遮罩
    # 只有當兩個遮罩都為 True 時，最終遮罩才為 True
    # tgt_mask 形狀從 (batch_size, 1, tgt_len, 1) 廣播到 (batch_size, 1, tgt_len, tgt_len)
    # 最終形狀：(batch_size, 1, tgt_len, tgt_len)
    tgt_mask = tgt_mask & look_ahead_mask

    return src_mask, tgt_mask
