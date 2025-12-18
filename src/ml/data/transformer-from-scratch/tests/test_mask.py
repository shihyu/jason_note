"""
測試 Mask 函數模組
"""
import torch
import pytest


def test_mask_import():
    """測試是否能正確匯入 create_padding_mask"""
    from transformer.mask import create_padding_mask
    assert create_padding_mask is not None


def test_create_padding_mask_basic():
    """測試基本的填充遮罩生成"""
    from transformer.mask import create_padding_mask

    # 建立簡單的輸入序列（0 是填充符號）
    src = torch.tensor([[1, 2, 3, 0, 0],
                       [1, 2, 0, 0, 0],
                       [1, 2, 3, 4, 5]])

    tgt = torch.tensor([[1, 2, 3, 0],
                       [1, 2, 0, 0],
                       [1, 2, 3, 4]])

    src_mask, tgt_mask = create_padding_mask(src, tgt, pad_idx=0)

    # 檢查 src_mask 形狀
    assert src_mask.shape == (3, 1, 1, 5)

    # 檢查 tgt_mask 形狀
    assert tgt_mask.shape == (3, 1, 4, 4)


def test_src_mask_padding():
    """測試源序列填充遮罩的正確性"""
    from transformer.mask import create_padding_mask

    src = torch.tensor([[1, 2, 3, 0, 0],
                       [1, 2, 0, 0, 0]])
    tgt = torch.tensor([[1, 2]])

    src_mask, _ = create_padding_mask(src, tgt, pad_idx=0)

    # 第一個序列：前 3 個是真實詞，後 2 個是填充
    assert src_mask[0, 0, 0, 0] == True  # 真實詞
    assert src_mask[0, 0, 0, 1] == True  # 真實詞
    assert src_mask[0, 0, 0, 2] == True  # 真實詞
    assert src_mask[0, 0, 0, 3] == False  # 填充
    assert src_mask[0, 0, 0, 4] == False  # 填充

    # 第二個序列：前 2 個是真實詞，後 3 個是填充
    assert src_mask[1, 0, 0, 0] == True
    assert src_mask[1, 0, 0, 1] == True
    assert src_mask[1, 0, 0, 2] == False
    assert src_mask[1, 0, 0, 3] == False
    assert src_mask[1, 0, 0, 4] == False


def test_tgt_mask_look_ahead():
    """測試目標序列的 look-ahead 遮罩"""
    from transformer.mask import create_padding_mask

    src = torch.tensor([[1, 2]])
    tgt = torch.tensor([[1, 2, 3, 4]])

    _, tgt_mask = create_padding_mask(src, tgt, pad_idx=0)

    # tgt_mask 應該是下三角矩陣（允許看到自己和之前的詞，遮蔽未來的詞）
    # 第一個位置只能看到自己
    assert tgt_mask[0, 0, 0, 0] == True
    assert tgt_mask[0, 0, 0, 1] == False
    assert tgt_mask[0, 0, 0, 2] == False
    assert tgt_mask[0, 0, 0, 3] == False

    # 第二個位置可以看到前兩個
    assert tgt_mask[0, 0, 1, 0] == True
    assert tgt_mask[0, 0, 1, 1] == True
    assert tgt_mask[0, 0, 1, 2] == False
    assert tgt_mask[0, 0, 1, 3] == False

    # 第四個位置可以看到所有
    assert tgt_mask[0, 0, 3, 0] == True
    assert tgt_mask[0, 0, 3, 1] == True
    assert tgt_mask[0, 0, 3, 2] == True
    assert tgt_mask[0, 0, 3, 3] == True


def test_tgt_mask_combined():
    """測試目標序列同時有填充和 look-ahead 遮罩"""
    from transformer.mask import create_padding_mask

    src = torch.tensor([[1, 2]])
    tgt = torch.tensor([[1, 2, 3, 0]])  # 最後一個是填充

    _, tgt_mask = create_padding_mask(src, tgt, pad_idx=0)

    # 第三個位置應該可以看到前三個，但不能看到填充的第四個
    assert tgt_mask[0, 0, 2, 0] == True
    assert tgt_mask[0, 0, 2, 1] == True
    assert tgt_mask[0, 0, 2, 2] == True
    assert tgt_mask[0, 0, 2, 3] == False  # 填充位置

    # 第一個位置只能看到自己，不能看到填充
    assert tgt_mask[0, 0, 0, 0] == True
    assert tgt_mask[0, 0, 0, 1] == False  # 未來詞
    assert tgt_mask[0, 0, 0, 2] == False  # 未來詞
    assert tgt_mask[0, 0, 0, 3] == False  # 填充


def test_mask_with_different_pad_idx():
    """測試使用不同的填充索引"""
    from transformer.mask import create_padding_mask

    # 使用 -1 作為填充符號
    src = torch.tensor([[1, 2, 3, -1, -1]])
    tgt = torch.tensor([[1, 2, -1]])

    src_mask, _ = create_padding_mask(src, tgt, pad_idx=-1)

    # 檢查填充位置
    assert src_mask[0, 0, 0, 0] == True
    assert src_mask[0, 0, 0, 1] == True
    assert src_mask[0, 0, 0, 2] == True
    assert src_mask[0, 0, 0, 3] == False  # 填充（-1）
    assert src_mask[0, 0, 0, 4] == False  # 填充（-1）


def test_mask_batch_processing():
    """測試批次處理的遮罩生成"""
    from transformer.mask import create_padding_mask

    batch_size = 16
    src_len = 20
    tgt_len = 15

    src = torch.randint(1, 100, (batch_size, src_len))
    tgt = torch.randint(1, 100, (batch_size, tgt_len))

    # 隨機添加一些填充
    src[:, -5:] = 0
    tgt[:, -3:] = 0

    src_mask, tgt_mask = create_padding_mask(src, tgt)

    # 檢查形狀
    assert src_mask.shape == (batch_size, 1, 1, src_len)
    assert tgt_mask.shape == (batch_size, 1, tgt_len, tgt_len)

    # 檢查類型
    assert src_mask.dtype == torch.bool
    assert tgt_mask.dtype == torch.bool


def test_mask_no_padding():
    """測試沒有填充的情況"""
    from transformer.mask import create_padding_mask

    src = torch.tensor([[1, 2, 3, 4, 5]])
    tgt = torch.tensor([[1, 2, 3]])

    src_mask, tgt_mask = create_padding_mask(src, tgt)

    # src_mask 應該全為 True（沒有填充）
    assert torch.all(src_mask == True)

    # tgt_mask 應該是下三角矩陣
    expected_tgt_mask = torch.tensor([
        [True, False, False],
        [True, True, False],
        [True, True, True]
    ])

    # 比較遮罩（去除批次和頭維度）
    assert torch.all(tgt_mask[0, 0] == expected_tgt_mask)


def test_mask_device_consistency():
    """測試遮罩的設備一致性"""
    from transformer.mask import create_padding_mask

    # 測試 CPU
    src_cpu = torch.tensor([[1, 2, 3, 0, 0]])
    tgt_cpu = torch.tensor([[1, 2, 0]])

    src_mask_cpu, tgt_mask_cpu = create_padding_mask(src_cpu, tgt_cpu)

    assert src_mask_cpu.device == src_cpu.device
    assert tgt_mask_cpu.device == tgt_cpu.device

    # 如果有 GPU，測試 GPU
    if torch.cuda.is_available():
        src_gpu = src_cpu.cuda()
        tgt_gpu = tgt_cpu.cuda()

        src_mask_gpu, tgt_mask_gpu = create_padding_mask(src_gpu, tgt_gpu)

        assert src_mask_gpu.device == src_gpu.device
        assert tgt_mask_gpu.device == tgt_gpu.device
