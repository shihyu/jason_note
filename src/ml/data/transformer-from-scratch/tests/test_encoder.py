"""
測試 Encoder 和 EncoderLayer 模組
"""
import torch
import pytest


def test_encoder_import():
    """測試是否能正確匯入 Encoder 和 EncoderLayer"""
    from transformer.encoder import Encoder, EncoderLayer
    assert Encoder is not None
    assert EncoderLayer is not None


def test_encoder_layer_initialization():
    """測試 EncoderLayer 的初始化"""
    from transformer.encoder import EncoderLayer

    d_model = 512
    n_heads = 8
    d_ff = 2048

    layer = EncoderLayer(d_model, n_heads, d_ff)

    # 檢查子模組是否存在
    assert hasattr(layer, 'self_attn')
    assert hasattr(layer, 'ffn')
    assert hasattr(layer, 'norm1')
    assert hasattr(layer, 'norm2')
    assert hasattr(layer, 'dropout1')
    assert hasattr(layer, 'dropout2')


def test_encoder_layer_output_shape():
    """測試 EncoderLayer 輸出的形狀"""
    from transformer.encoder import EncoderLayer

    batch_size = 32
    seq_len = 10
    d_model = 512
    n_heads = 8
    d_ff = 2048

    layer = EncoderLayer(d_model, n_heads, d_ff)

    x = torch.randn(batch_size, seq_len, d_model)
    output = layer(x)

    # 輸出形狀應該與輸入相同
    assert output.shape == (batch_size, seq_len, d_model), \
        f"期望形狀 {(batch_size, seq_len, d_model)}, 但得到 {output.shape}"


def test_encoder_layer_with_mask():
    """測試 EncoderLayer 使用遮罩"""
    from transformer.encoder import EncoderLayer

    batch_size = 16
    seq_len = 20
    d_model = 256
    n_heads = 4
    d_ff = 1024

    layer = EncoderLayer(d_model, n_heads, d_ff)

    x = torch.randn(batch_size, seq_len, d_model)

    # 建立遮罩（遮蔽後半部分）
    mask = torch.ones(batch_size, 1, 1, seq_len)
    mask[:, :, :, seq_len//2:] = 0

    output_with_mask = layer(x, mask)
    output_without_mask = layer(x, None)

    # 有遮罩和沒遮罩的輸出應該不同
    assert not torch.allclose(output_with_mask, output_without_mask)


def test_encoder_layer_residual_connection():
    """測試 EncoderLayer 的殘差連接"""
    from transformer.encoder import EncoderLayer

    batch_size = 8
    seq_len = 15
    d_model = 128
    n_heads = 4
    d_ff = 512

    layer = EncoderLayer(d_model, n_heads, d_ff, dropout=0.0)
    layer.eval()

    x = torch.randn(batch_size, seq_len, d_model)
    output = layer(x)

    # 輸出應該與輸入形狀相同
    assert output.shape == x.shape

    # 由於有殘差連接，輸出不應該完全等於輸入
    assert not torch.allclose(output, x)


def test_encoder_initialization():
    """測試 Encoder 的初始化"""
    from transformer.encoder import Encoder

    d_model = 512
    n_heads = 8
    d_ff = 2048
    num_layers = 6

    encoder = Encoder(d_model, n_heads, d_ff, num_layers)

    # 檢查層數
    assert len(encoder.layers) == num_layers


def test_encoder_output_shape():
    """測試 Encoder 輸出的形狀"""
    from transformer.encoder import Encoder

    batch_size = 32
    seq_len = 10
    d_model = 512
    n_heads = 8
    d_ff = 2048
    num_layers = 6

    encoder = Encoder(d_model, n_heads, d_ff, num_layers)

    x = torch.randn(batch_size, seq_len, d_model)
    output = encoder(x)

    # 輸出形狀應該與輸入相同
    assert output.shape == (batch_size, seq_len, d_model), \
        f"期望形狀 {(batch_size, seq_len, d_model)}, 但得到 {output.shape}"


def test_encoder_with_different_num_layers():
    """測試不同層數的 Encoder"""
    from transformer.encoder import Encoder

    batch_size = 16
    seq_len = 20
    d_model = 256
    n_heads = 4
    d_ff = 1024

    for num_layers in [1, 3, 6, 12]:
        encoder = Encoder(d_model, n_heads, d_ff, num_layers)
        x = torch.randn(batch_size, seq_len, d_model)
        output = encoder(x)

        assert output.shape == (batch_size, seq_len, d_model)
        assert len(encoder.layers) == num_layers


def test_encoder_with_mask():
    """測試 Encoder 使用遮罩"""
    from transformer.encoder import Encoder

    batch_size = 8
    seq_len = 15
    d_model = 128
    n_heads = 4
    d_ff = 512
    num_layers = 3

    encoder = Encoder(d_model, n_heads, d_ff, num_layers)

    x = torch.randn(batch_size, seq_len, d_model)

    # 建立遮罩
    mask = torch.ones(batch_size, 1, 1, seq_len)
    mask[:, :, :, seq_len//2:] = 0

    output_with_mask = encoder(x, mask)
    output_without_mask = encoder(x, None)

    # 有遮罩和沒遮罩的輸出應該不同
    assert not torch.allclose(output_with_mask, output_without_mask)


def test_encoder_gradient_flow():
    """測試 Encoder 的梯度流動"""
    from transformer.encoder import Encoder

    batch_size = 4
    seq_len = 8
    d_model = 128
    n_heads = 4
    d_ff = 512
    num_layers = 2

    encoder = Encoder(d_model, n_heads, d_ff, num_layers)

    x = torch.randn(batch_size, seq_len, d_model, requires_grad=True)
    output = encoder(x)

    # 計算損失並反向傳播
    loss = output.sum()
    loss.backward()

    # 檢查梯度是否存在
    assert x.grad is not None
    assert not torch.all(x.grad == 0), "梯度不應該全為零"


def test_encoder_deterministic():
    """測試 Encoder 在評估模式下是否確定性"""
    from transformer.encoder import Encoder

    batch_size = 16
    seq_len = 12
    d_model = 256
    n_heads = 8
    d_ff = 1024
    num_layers = 4

    encoder = Encoder(d_model, n_heads, d_ff, num_layers)
    encoder.eval()

    x = torch.randn(batch_size, seq_len, d_model)

    output1 = encoder(x)
    output2 = encoder(x)

    # 相同輸入應該產生相同輸出
    torch.testing.assert_close(output1, output2)


def test_encoder_final_norm():
    """測試 Encoder 最後的 LayerNorm"""
    from transformer.encoder import Encoder

    batch_size = 8
    seq_len = 10
    d_model = 128
    n_heads = 4
    d_ff = 512
    num_layers = 2

    encoder = Encoder(d_model, n_heads, d_ff, num_layers)

    # 檢查是否有最終的 norm 層
    assert hasattr(encoder, 'norm')
