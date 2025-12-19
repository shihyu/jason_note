"""
測試 PositionalEncoding 模組
"""
import torch
import pytest
import math


def test_positional_encoding_import():
    """測試是否能正確匯入 PositionalEncoding"""
    from transformer.positional_encoding import PositionalEncoding
    assert PositionalEncoding is not None


def test_positional_encoding_shape():
    """測試位置編碼輸出的形狀是否正確"""
    from transformer.positional_encoding import PositionalEncoding

    d_model = 512
    max_len = 100
    batch_size = 32
    seq_len = 10

    pe = PositionalEncoding(d_model, max_len)
    x = torch.randn(batch_size, seq_len, d_model)
    output = pe(x)

    # 檢查輸出形狀應該與輸入相同
    assert output.shape == (batch_size, seq_len, d_model), \
        f"期望形狀 {(batch_size, seq_len, d_model)}, 但得到 {output.shape}"


def test_positional_encoding_values():
    """測試位置編碼的值是否符合公式"""
    from transformer.positional_encoding import PositionalEncoding

    d_model = 4  # 使用較小的維度方便測試
    max_len = 10

    pe = PositionalEncoding(d_model, max_len)

    # 取得位置編碼（不含輸入）
    pe_values = pe.pe[0, :5, :]  # 取前 5 個位置

    # 手動計算第 0 個位置的編碼（應該都是 0 和 1）
    # PE(0, 2i) = sin(0) = 0
    # PE(0, 2i+1) = cos(0) = 1
    expected_pos_0 = torch.tensor([0.0, 1.0, 0.0, 1.0])
    torch.testing.assert_close(pe_values[0], expected_pos_0, atol=1e-6, rtol=1e-5)

    # 測試位置 1
    position = 1.0
    div_term = torch.exp(torch.arange(0, d_model, 2).float() * -(math.log(10000.0) / d_model))
    expected_pos_1 = torch.zeros(d_model)
    expected_pos_1[0::2] = torch.sin(position * div_term)
    expected_pos_1[1::2] = torch.cos(position * div_term)
    torch.testing.assert_close(pe_values[1], expected_pos_1, atol=1e-6, rtol=1e-5)


def test_positional_encoding_different_seq_lengths():
    """測試位置編碼對不同序列長度的處理"""
    from transformer.positional_encoding import PositionalEncoding

    d_model = 512
    max_len = 5000
    batch_size = 16

    pe = PositionalEncoding(d_model, max_len)

    # 測試不同的序列長度
    for seq_len in [10, 50, 100]:
        x = torch.randn(batch_size, seq_len, d_model)
        output = pe(x)
        assert output.shape == (batch_size, seq_len, d_model)


def test_positional_encoding_deterministic():
    """測試位置編碼是否是確定性的（每次輸出相同）"""
    from transformer.positional_encoding import PositionalEncoding

    d_model = 512
    max_len = 100
    batch_size = 8
    seq_len = 20

    pe = PositionalEncoding(d_model, max_len)
    x = torch.randn(batch_size, seq_len, d_model)

    output1 = pe(x)
    output2 = pe(x)

    # 兩次前向傳播應該產生相同的結果
    torch.testing.assert_close(output1, output2)


def test_positional_encoding_max_len_exceeded():
    """測試當序列長度超過 max_len 時是否會失敗"""
    from transformer.positional_encoding import PositionalEncoding

    d_model = 512
    max_len = 50
    batch_size = 4
    seq_len = 100  # 超過 max_len

    pe = PositionalEncoding(d_model, max_len)
    x = torch.randn(batch_size, seq_len, d_model)

    # 應該會因為超過 max_len 而出錯
    with pytest.raises((RuntimeError, IndexError)):
        pe(x)
