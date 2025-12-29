"""
測試 FeedForward 模組
"""
import torch
import pytest


def test_feed_forward_import():
    """測試是否能正確匯入 FeedForward"""
    from transformer.feed_forward import FeedForward
    assert FeedForward is not None


def test_feed_forward_initialization():
    """測試 FeedForward 的初始化"""
    from transformer.feed_forward import FeedForward

    d_model = 512
    d_ff = 2048

    ffn = FeedForward(d_model, d_ff)

    # 檢查線性層的維度
    assert ffn.linear1.in_features == d_model
    assert ffn.linear1.out_features == d_ff
    assert ffn.linear2.in_features == d_ff
    assert ffn.linear2.out_features == d_model


def test_feed_forward_output_shape():
    """測試 FeedForward 輸出的形狀"""
    from transformer.feed_forward import FeedForward

    batch_size = 32
    seq_len = 10
    d_model = 512
    d_ff = 2048

    ffn = FeedForward(d_model, d_ff)

    x = torch.randn(batch_size, seq_len, d_model)
    output = ffn(x)

    # 輸出形狀應該與輸入相同
    assert output.shape == (batch_size, seq_len, d_model), \
        f"期望形狀 {(batch_size, seq_len, d_model)}, 但得到 {output.shape}"


def test_feed_forward_different_seq_lengths():
    """測試 FeedForward 對不同序列長度的處理"""
    from transformer.feed_forward import FeedForward

    batch_size = 16
    d_model = 256
    d_ff = 1024

    ffn = FeedForward(d_model, d_ff)

    # 測試不同的序列長度
    for seq_len in [5, 20, 50, 100]:
        x = torch.randn(batch_size, seq_len, d_model)
        output = ffn(x)
        assert output.shape == (batch_size, seq_len, d_model)


def test_feed_forward_activation():
    """測試 FeedForward 使用 ReLU 激活函數"""
    from transformer.feed_forward import FeedForward

    d_model = 128
    d_ff = 512

    ffn = FeedForward(d_model, d_ff, dropout=0.0)

    # 檢查是否使用 ReLU
    assert isinstance(ffn.activation, torch.nn.ReLU)


def test_feed_forward_non_linearity():
    """測試 FeedForward 的非線性特性"""
    from transformer.feed_forward import FeedForward

    batch_size = 8
    seq_len = 10
    d_model = 64
    d_ff = 256

    ffn = FeedForward(d_model, d_ff, dropout=0.0)
    ffn.eval()

    x1 = torch.randn(batch_size, seq_len, d_model)
    x2 = torch.randn(batch_size, seq_len, d_model)

    output1 = ffn(x1)
    output2 = ffn(x2)
    output_sum = ffn(x1 + x2)

    # 由於有 ReLU 非線性，ffn(x1 + x2) 不應該等於 ffn(x1) + ffn(x2)
    # 這驗證了模型確實是非線性的
    assert not torch.allclose(output_sum, output1 + output2, atol=1e-3)


def test_feed_forward_dropout_training_vs_eval():
    """測試 FeedForward 在訓練和評估模式下的行為"""
    from transformer.feed_forward import FeedForward

    batch_size = 16
    seq_len = 20
    d_model = 256
    d_ff = 1024

    ffn = FeedForward(d_model, d_ff, dropout=0.5)

    x = torch.randn(batch_size, seq_len, d_model)

    # 訓練模式：由於 dropout，多次前向傳播應該產生不同的結果
    ffn.train()
    torch.manual_seed(42)
    output_train1 = ffn(x)
    torch.manual_seed(43)
    output_train2 = ffn(x)

    # 在訓練模式下，由於 dropout 的隨機性，輸出應該不同
    assert not torch.allclose(output_train1, output_train2)

    # 評估模式：多次前向傳播應該產生相同的結果
    ffn.eval()
    output_eval1 = ffn(x)
    output_eval2 = ffn(x)

    # 在評估模式下，dropout 被關閉，輸出應該相同
    torch.testing.assert_close(output_eval1, output_eval2)


def test_feed_forward_zero_input():
    """測試 FeedForward 對零輸入的處理"""
    from transformer.feed_forward import FeedForward

    batch_size = 4
    seq_len = 8
    d_model = 128
    d_ff = 512

    ffn = FeedForward(d_model, d_ff, dropout=0.0)

    # 零輸入
    x = torch.zeros(batch_size, seq_len, d_model)
    output = ffn(x)

    # 輸出形狀應該正確
    assert output.shape == (batch_size, seq_len, d_model)


def test_feed_forward_gradient_flow():
    """測試 FeedForward 的梯度流動"""
    from transformer.feed_forward import FeedForward

    batch_size = 8
    seq_len = 10
    d_model = 256
    d_ff = 1024

    ffn = FeedForward(d_model, d_ff)

    x = torch.randn(batch_size, seq_len, d_model, requires_grad=True)
    output = ffn(x)

    # 計算損失並反向傳播
    loss = output.sum()
    loss.backward()

    # 檢查梯度是否存在
    assert x.grad is not None
    assert not torch.all(x.grad == 0), "梯度不應該全為零"


def test_feed_forward_deterministic():
    """測試 FeedForward 在評估模式下是否確定性"""
    from transformer.feed_forward import FeedForward

    batch_size = 16
    seq_len = 15
    d_model = 512
    d_ff = 2048

    ffn = FeedForward(d_model, d_ff)
    ffn.eval()

    x = torch.randn(batch_size, seq_len, d_model)

    output1 = ffn(x)
    output2 = ffn(x)

    # 相同輸入應該產生相同輸出
    torch.testing.assert_close(output1, output2)
