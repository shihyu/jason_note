"""
測試完整的 Transformer 模型
"""
import torch
import pytest


def test_transformer_import():
    """測試是否能正確匯入 Transformer"""
    from transformer.model import Transformer
    assert Transformer is not None


def test_transformer_initialization():
    """測試 Transformer 的初始化"""
    from transformer.model import Transformer

    src_vocab_size = 10000
    tgt_vocab_size = 10000
    d_model = 512
    n_heads = 8
    d_ff = 2048
    num_layers = 6

    model = Transformer(src_vocab_size, tgt_vocab_size, d_model, n_heads, d_ff, num_layers)

    # 檢查各個組件是否存在
    assert hasattr(model, 'encoder_embedding')
    assert hasattr(model, 'decoder_embedding')
    assert hasattr(model, 'positional_encoding')
    assert hasattr(model, 'encoder')
    assert hasattr(model, 'decoder')
    assert hasattr(model, 'fc_out')


def test_transformer_output_shape():
    """測試 Transformer 輸出的形狀"""
    from transformer.model import Transformer

    batch_size = 32
    src_seq_len = 10
    tgt_seq_len = 12
    src_vocab_size = 10000
    tgt_vocab_size = 10000
    d_model = 512
    n_heads = 8
    d_ff = 2048
    num_layers = 6

    model = Transformer(src_vocab_size, tgt_vocab_size, d_model, n_heads, d_ff, num_layers)

    src = torch.randint(0, src_vocab_size, (batch_size, src_seq_len))
    tgt = torch.randint(0, tgt_vocab_size, (batch_size, tgt_seq_len))

    output = model(src, tgt)

    # 輸出形狀應該是 (batch_size, tgt_seq_len, tgt_vocab_size)
    assert output.shape == (batch_size, tgt_seq_len, tgt_vocab_size), \
        f"期望形狀 {(batch_size, tgt_seq_len, tgt_vocab_size)}, 但得到 {output.shape}"


def test_transformer_with_masks():
    """測試 Transformer 使用遮罩"""
    from transformer.model import Transformer
    from transformer.mask import create_padding_mask

    batch_size = 16
    src_seq_len = 10
    tgt_seq_len = 12
    src_vocab_size = 5000
    tgt_vocab_size = 5000
    d_model = 256
    n_heads = 4
    d_ff = 1024
    num_layers = 3

    model = Transformer(src_vocab_size, tgt_vocab_size, d_model, n_heads, d_ff, num_layers)

    src = torch.randint(1, src_vocab_size, (batch_size, src_seq_len))
    tgt = torch.randint(1, tgt_vocab_size, (batch_size, tgt_seq_len))

    # 添加填充
    src[:, -2:] = 0
    tgt[:, -3:] = 0

    # 建立遮罩
    src_mask, tgt_mask = create_padding_mask(src, tgt)

    output_with_mask = model(src, tgt, src_mask, tgt_mask)
    output_without_mask = model(src, tgt)

    # 有遮罩和沒遮罩的輸出應該不同
    assert not torch.allclose(output_with_mask, output_without_mask)


def test_transformer_different_vocab_sizes():
    """測試不同詞彙表大小的 Transformer"""
    from transformer.model import Transformer

    batch_size = 8
    src_seq_len = 15
    tgt_seq_len = 10
    src_vocab_size = 8000
    tgt_vocab_size = 6000
    d_model = 128
    n_heads = 4
    d_ff = 512
    num_layers = 2

    model = Transformer(src_vocab_size, tgt_vocab_size, d_model, n_heads, d_ff, num_layers)

    src = torch.randint(0, src_vocab_size, (batch_size, src_seq_len))
    tgt = torch.randint(0, tgt_vocab_size, (batch_size, tgt_seq_len))

    output = model(src, tgt)

    assert output.shape == (batch_size, tgt_seq_len, tgt_vocab_size)


def test_transformer_gradient_flow():
    """測試 Transformer 的梯度流動"""
    from transformer.model import Transformer

    batch_size = 4
    src_seq_len = 8
    tgt_seq_len = 10
    src_vocab_size = 1000
    tgt_vocab_size = 1000
    d_model = 128
    n_heads = 4
    d_ff = 512
    num_layers = 2

    model = Transformer(src_vocab_size, tgt_vocab_size, d_model, n_heads, d_ff, num_layers)

    src = torch.randint(0, src_vocab_size, (batch_size, src_seq_len))
    tgt = torch.randint(0, tgt_vocab_size, (batch_size, tgt_seq_len))

    output = model(src, tgt)

    # 計算損失並反向傳播
    loss = output.sum()
    loss.backward()

    # 檢查梯度是否存在
    for name, param in model.named_parameters():
        if param.requires_grad:
            assert param.grad is not None, f"參數 {name} 的梯度不存在"


def test_transformer_deterministic():
    """測試 Transformer 在評估模式下是否確定性"""
    from transformer.model import Transformer

    batch_size = 16
    src_seq_len = 12
    tgt_seq_len = 15
    src_vocab_size = 5000
    tgt_vocab_size = 5000
    d_model = 256
    n_heads = 8
    d_ff = 1024
    num_layers = 4

    model = Transformer(src_vocab_size, tgt_vocab_size, d_model, n_heads, d_ff, num_layers)
    model.eval()

    src = torch.randint(0, src_vocab_size, (batch_size, src_seq_len))
    tgt = torch.randint(0, tgt_vocab_size, (batch_size, tgt_seq_len))

    output1 = model(src, tgt)
    output2 = model(src, tgt)

    # 相同輸入應該產生相同輸出
    torch.testing.assert_close(output1, output2)


def test_transformer_embedding_scaling():
    """測試詞嵌入的縮放"""
    from transformer.model import Transformer

    batch_size = 4
    src_seq_len = 5
    tgt_seq_len = 6
    src_vocab_size = 1000
    tgt_vocab_size = 1000
    d_model = 128
    n_heads = 4
    d_ff = 512
    num_layers = 2

    model = Transformer(src_vocab_size, tgt_vocab_size, d_model, n_heads, d_ff, num_layers)

    # 檢查嵌入維度
    assert model.encoder_embedding.embedding_dim == d_model
    assert model.decoder_embedding.embedding_dim == d_model


def test_transformer_with_example_from_paper():
    """測試使用論文中的範例配置"""
    from transformer.model import Transformer

    # 原論文配置
    batch_size = 32
    src_seq_len = 10
    tgt_seq_len = 12
    src_vocab_size = 10000
    tgt_vocab_size = 10000
    d_model = 512
    n_heads = 8
    d_ff = 2048
    num_layers = 6
    dropout = 0.1

    model = Transformer(
        src_vocab_size, tgt_vocab_size,
        d_model, n_heads, d_ff, num_layers, dropout
    )

    src = torch.randint(0, src_vocab_size, (batch_size, src_seq_len))
    tgt = torch.randint(0, tgt_vocab_size, (batch_size, tgt_seq_len))

    output = model(src, tgt)

    assert output.shape == (batch_size, tgt_seq_len, tgt_vocab_size)


def test_transformer_small_config():
    """測試小型配置的 Transformer（用於快速測試）"""
    from transformer.model import Transformer

    batch_size = 2
    src_seq_len = 5
    tgt_seq_len = 6
    src_vocab_size = 100
    tgt_vocab_size = 100
    d_model = 32
    n_heads = 2
    d_ff = 128
    num_layers = 1

    model = Transformer(src_vocab_size, tgt_vocab_size, d_model, n_heads, d_ff, num_layers)

    src = torch.randint(0, src_vocab_size, (batch_size, src_seq_len))
    tgt = torch.randint(0, tgt_vocab_size, (batch_size, tgt_seq_len))

    output = model(src, tgt)

    assert output.shape == (batch_size, tgt_seq_len, tgt_vocab_size)
