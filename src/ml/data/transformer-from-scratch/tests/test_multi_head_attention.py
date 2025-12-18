"""
測試 MultiHeadAttention 模組
"""
import torch
import pytest
import math


def test_multi_head_attention_import():
    """測試是否能正確匯入 MultiHeadAttention"""
    from transformer.multi_head_attention import MultiHeadAttention
    assert MultiHeadAttention is not None


def test_multi_head_attention_initialization():
    """測試 MultiHeadAttention 的初始化"""
    from transformer.multi_head_attention import MultiHeadAttention

    d_model = 512
    n_heads = 8

    mha = MultiHeadAttention(d_model, n_heads)

    # 檢查 d_k 是否正確計算
    assert mha.d_k == d_model // n_heads
    assert mha.d_model == d_model
    assert mha.n_heads == n_heads


def test_multi_head_attention_invalid_params():
    """測試當 d_model 無法被 n_heads 整除時應該拋出錯誤"""
    from transformer.multi_head_attention import MultiHeadAttention

    d_model = 512
    n_heads = 7  # 512 無法被 7 整除

    with pytest.raises(AssertionError):
        MultiHeadAttention(d_model, n_heads)


def test_multi_head_attention_output_shape():
    """測試 MultiHeadAttention 輸出的形狀"""
    from transformer.multi_head_attention import MultiHeadAttention

    batch_size = 32
    seq_len = 10
    d_model = 512
    n_heads = 8

    mha = MultiHeadAttention(d_model, n_heads)

    Q = torch.randn(batch_size, seq_len, d_model)
    K = torch.randn(batch_size, seq_len, d_model)
    V = torch.randn(batch_size, seq_len, d_model)

    output = mha(Q, K, V)

    # 輸出形狀應該與輸入 Q 相同
    assert output.shape == (batch_size, seq_len, d_model), \
        f"期望形狀 {(batch_size, seq_len, d_model)}, 但得到 {output.shape}"


def test_multi_head_attention_with_mask():
    """測試帶遮罩的 MultiHeadAttention"""
    from transformer.multi_head_attention import MultiHeadAttention

    batch_size = 16
    seq_len = 20
    d_model = 512
    n_heads = 8

    mha = MultiHeadAttention(d_model, n_heads)

    Q = torch.randn(batch_size, seq_len, d_model)
    K = torch.randn(batch_size, seq_len, d_model)
    V = torch.randn(batch_size, seq_len, d_model)

    # 建立遮罩（遮蔽後半部分）
    mask = torch.ones(batch_size, 1, 1, seq_len)
    mask[:, :, :, seq_len//2:] = 0  # 遮蔽後半部

    output_with_mask = mha(Q, K, V, mask)
    output_without_mask = mha(Q, K, V, None)

    # 有遮罩和沒遮罩的輸出應該不同
    assert not torch.allclose(output_with_mask, output_without_mask)

    # 輸出形狀應該相同
    assert output_with_mask.shape == output_without_mask.shape


def test_multi_head_attention_different_qkv_lengths():
    """測試 Q, K, V 序列長度不同的情況（用於編碼器-解碼器注意力）"""
    from transformer.multi_head_attention import MultiHeadAttention

    batch_size = 8
    q_seq_len = 12
    kv_seq_len = 20
    d_model = 512
    n_heads = 8

    mha = MultiHeadAttention(d_model, n_heads)

    Q = torch.randn(batch_size, q_seq_len, d_model)
    K = torch.randn(batch_size, kv_seq_len, d_model)
    V = torch.randn(batch_size, kv_seq_len, d_model)

    output = mha(Q, K, V)

    # 輸出長度應該與 Q 的序列長度相同
    assert output.shape == (batch_size, q_seq_len, d_model)


def test_multi_head_attention_self_attention():
    """測試自注意力（Q=K=V）"""
    from transformer.multi_head_attention import MultiHeadAttention

    batch_size = 16
    seq_len = 15
    d_model = 512
    n_heads = 8

    mha = MultiHeadAttention(d_model, n_heads)

    x = torch.randn(batch_size, seq_len, d_model)

    # 自注意力：Q = K = V
    output = mha(x, x, x)

    assert output.shape == (batch_size, seq_len, d_model)


def test_multi_head_attention_scaled_dot_product():
    """測試縮放點積注意力的計算"""
    from transformer.multi_head_attention import MultiHeadAttention

    batch_size = 4
    seq_len = 8
    d_model = 64
    n_heads = 4

    mha = MultiHeadAttention(d_model, n_heads, dropout=0.0)  # 不使用 dropout 以便測試

    Q = torch.randn(batch_size, n_heads, seq_len, mha.d_k)
    K = torch.randn(batch_size, n_heads, seq_len, mha.d_k)
    V = torch.randn(batch_size, n_heads, seq_len, mha.d_k)

    output = mha.scaled_dot_product_attention(Q, K, V)

    # 檢查輸出形狀
    assert output.shape == (batch_size, n_heads, seq_len, mha.d_k)


def test_multi_head_attention_attention_weights_sum_to_one():
    """測試注意力權重總和為 1（透過 softmax）"""
    from transformer.multi_head_attention import MultiHeadAttention
    import torch.nn.functional as F

    batch_size = 2
    seq_len = 5
    d_model = 32
    n_heads = 2

    mha = MultiHeadAttention(d_model, n_heads, dropout=0.0)

    Q = torch.randn(batch_size, n_heads, seq_len, mha.d_k)
    K = torch.randn(batch_size, n_heads, seq_len, mha.d_k)

    # 計算注意力分數
    scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(mha.d_k)
    attn_weights = F.softmax(scores, dim=-1)

    # 檢查每一行的權重總和是否為 1
    weights_sum = attn_weights.sum(dim=-1)
    expected_sum = torch.ones_like(weights_sum)
    torch.testing.assert_close(weights_sum, expected_sum, atol=1e-6, rtol=1e-5)


def test_multi_head_attention_deterministic():
    """測試在相同輸入下輸出是否確定（eval 模式下）"""
    from transformer.multi_head_attention import MultiHeadAttention

    batch_size = 8
    seq_len = 10
    d_model = 256
    n_heads = 4

    mha = MultiHeadAttention(d_model, n_heads)
    mha.eval()  # 設為 eval 模式以關閉 dropout

    Q = torch.randn(batch_size, seq_len, d_model)
    K = torch.randn(batch_size, seq_len, d_model)
    V = torch.randn(batch_size, seq_len, d_model)

    output1 = mha(Q, K, V)
    output2 = mha(Q, K, V)

    # 在 eval 模式下，相同輸入應該產生相同輸出
    torch.testing.assert_close(output1, output2)
