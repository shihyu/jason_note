"""
測試 Decoder 和 DecoderLayer 模組
"""
import torch
import pytest


def test_decoder_import():
    """測試是否能正確匯入 Decoder 和 DecoderLayer"""
    from transformer.decoder import Decoder, DecoderLayer
    assert Decoder is not None
    assert DecoderLayer is not None


def test_decoder_layer_initialization():
    """測試 DecoderLayer 的初始化"""
    from transformer.decoder import DecoderLayer

    d_model = 512
    n_heads = 8
    d_ff = 2048

    layer = DecoderLayer(d_model, n_heads, d_ff)

    # 檢查子模組是否存在
    assert hasattr(layer, 'self_attn')  # 自注意力
    assert hasattr(layer, 'cross_attn')  # 交叉注意力
    assert hasattr(layer, 'ffn')  # 前饋網絡
    assert hasattr(layer, 'norm1')  # 第一個 LayerNorm
    assert hasattr(layer, 'norm2')  # 第二個 LayerNorm
    assert hasattr(layer, 'norm3')  # 第三個 LayerNorm


def test_decoder_layer_output_shape():
    """測試 DecoderLayer 輸出的形狀"""
    from transformer.decoder import DecoderLayer

    batch_size = 32
    tgt_seq_len = 12
    src_seq_len = 10
    d_model = 512
    n_heads = 8
    d_ff = 2048

    layer = DecoderLayer(d_model, n_heads, d_ff)

    tgt = torch.randn(batch_size, tgt_seq_len, d_model)
    src = torch.randn(batch_size, src_seq_len, d_model)

    output = layer(tgt, src)

    # 輸出形狀應該與目標序列（tgt）相同
    assert output.shape == (batch_size, tgt_seq_len, d_model), \
        f"期望形狀 {(batch_size, tgt_seq_len, d_model)}, 但得到 {output.shape}"


def test_decoder_layer_with_masks():
    """測試 DecoderLayer 使用遮罩"""
    from transformer.decoder import DecoderLayer

    batch_size = 16
    tgt_seq_len = 15
    src_seq_len = 20
    d_model = 256
    n_heads = 4
    d_ff = 1024

    layer = DecoderLayer(d_model, n_heads, d_ff)

    tgt = torch.randn(batch_size, tgt_seq_len, d_model)
    src = torch.randn(batch_size, src_seq_len, d_model)

    # 建立遮罩
    tgt_mask = torch.ones(batch_size, 1, tgt_seq_len, tgt_seq_len).tril()  # 下三角遮罩
    src_mask = torch.ones(batch_size, 1, 1, src_seq_len)

    output_with_mask = layer(tgt, src, tgt_mask, src_mask)
    output_without_mask = layer(tgt, src, None, None)

    # 有遮罩和沒遮罩的輸出應該不同
    assert not torch.allclose(output_with_mask, output_without_mask)


def test_decoder_layer_cross_attention():
    """測試 DecoderLayer 的交叉注意力"""
    from transformer.decoder import DecoderLayer

    batch_size = 8
    tgt_seq_len = 10
    src_seq_len = 15
    d_model = 128
    n_heads = 4
    d_ff = 512

    layer = DecoderLayer(d_model, n_heads, d_ff)

    tgt = torch.randn(batch_size, tgt_seq_len, d_model)
    src1 = torch.randn(batch_size, src_seq_len, d_model)
    src2 = torch.randn(batch_size, src_seq_len, d_model)

    output1 = layer(tgt, src1)
    output2 = layer(tgt, src2)

    # 不同的源序列應該產生不同的輸出
    assert not torch.allclose(output1, output2)


def test_decoder_initialization():
    """測試 Decoder 的初始化"""
    from transformer.decoder import Decoder

    d_model = 512
    n_heads = 8
    d_ff = 2048
    num_layers = 6

    decoder = Decoder(d_model, n_heads, d_ff, num_layers)

    # 檢查層數
    assert len(decoder.layers) == num_layers


def test_decoder_output_shape():
    """測試 Decoder 輸出的形狀"""
    from transformer.decoder import Decoder

    batch_size = 32
    tgt_seq_len = 12
    src_seq_len = 10
    d_model = 512
    n_heads = 8
    d_ff = 2048
    num_layers = 6

    decoder = Decoder(d_model, n_heads, d_ff, num_layers)

    tgt = torch.randn(batch_size, tgt_seq_len, d_model)
    memory = torch.randn(batch_size, src_seq_len, d_model)

    output = decoder(tgt, memory)

    # 輸出形狀應該與目標序列相同
    assert output.shape == (batch_size, tgt_seq_len, d_model), \
        f"期望形狀 {(batch_size, tgt_seq_len, d_model)}, 但得到 {output.shape}"


def test_decoder_with_different_num_layers():
    """測試不同層數的 Decoder"""
    from transformer.decoder import Decoder

    batch_size = 16
    tgt_seq_len = 15
    src_seq_len = 20
    d_model = 256
    n_heads = 4
    d_ff = 1024

    for num_layers in [1, 3, 6, 12]:
        decoder = Decoder(d_model, n_heads, d_ff, num_layers)
        tgt = torch.randn(batch_size, tgt_seq_len, d_model)
        memory = torch.randn(batch_size, src_seq_len, d_model)
        output = decoder(tgt, memory)

        assert output.shape == (batch_size, tgt_seq_len, d_model)
        assert len(decoder.layers) == num_layers


def test_decoder_with_masks():
    """測試 Decoder 使用遮罩"""
    from transformer.decoder import Decoder

    batch_size = 8
    tgt_seq_len = 10
    src_seq_len = 15
    d_model = 128
    n_heads = 4
    d_ff = 512
    num_layers = 3

    decoder = Decoder(d_model, n_heads, d_ff, num_layers)

    tgt = torch.randn(batch_size, tgt_seq_len, d_model)
    memory = torch.randn(batch_size, src_seq_len, d_model)

    # 建立遮罩
    tgt_mask = torch.ones(batch_size, 1, tgt_seq_len, tgt_seq_len).tril()
    memory_mask = torch.ones(batch_size, 1, 1, src_seq_len)

    output_with_mask = decoder(tgt, memory, tgt_mask, memory_mask)
    output_without_mask = decoder(tgt, memory, None, None)

    # 有遮罩和沒遮罩的輸出應該不同
    assert not torch.allclose(output_with_mask, output_without_mask)


def test_decoder_with_encoder_output():
    """測試 Decoder 與編碼器輸出的配合"""
    from transformer.decoder import Decoder
    from transformer.encoder import Encoder

    batch_size = 16
    src_seq_len = 20
    tgt_seq_len = 15
    d_model = 256
    n_heads = 4
    d_ff = 1024
    num_layers = 3

    encoder = Encoder(d_model, n_heads, d_ff, num_layers)
    decoder = Decoder(d_model, n_heads, d_ff, num_layers)

    src = torch.randn(batch_size, src_seq_len, d_model)
    tgt = torch.randn(batch_size, tgt_seq_len, d_model)

    # 編碼器輸出作為解碼器的 memory
    encoder_output = encoder(src)
    decoder_output = decoder(tgt, encoder_output)

    assert decoder_output.shape == (batch_size, tgt_seq_len, d_model)


def test_decoder_gradient_flow():
    """測試 Decoder 的梯度流動"""
    from transformer.decoder import Decoder

    batch_size = 4
    tgt_seq_len = 8
    src_seq_len = 10
    d_model = 128
    n_heads = 4
    d_ff = 512
    num_layers = 2

    decoder = Decoder(d_model, n_heads, d_ff, num_layers)

    tgt = torch.randn(batch_size, tgt_seq_len, d_model, requires_grad=True)
    memory = torch.randn(batch_size, src_seq_len, d_model, requires_grad=True)

    output = decoder(tgt, memory)

    # 計算損失並反向傳播
    loss = output.sum()
    loss.backward()

    # 檢查梯度是否存在
    assert tgt.grad is not None
    assert memory.grad is not None
    assert not torch.all(tgt.grad == 0), "tgt 梯度不應該全為零"
    assert not torch.all(memory.grad == 0), "memory 梯度不應該全為零"


def test_decoder_deterministic():
    """測試 Decoder 在評估模式下是否確定性"""
    from transformer.decoder import Decoder

    batch_size = 16
    tgt_seq_len = 12
    src_seq_len = 15
    d_model = 256
    n_heads = 8
    d_ff = 1024
    num_layers = 4

    decoder = Decoder(d_model, n_heads, d_ff, num_layers)
    decoder.eval()

    tgt = torch.randn(batch_size, tgt_seq_len, d_model)
    memory = torch.randn(batch_size, src_seq_len, d_model)

    output1 = decoder(tgt, memory)
    output2 = decoder(tgt, memory)

    # 相同輸入應該產生相同輸出
    torch.testing.assert_close(output1, output2)
