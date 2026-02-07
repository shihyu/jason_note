"""pytest 配置檔案

確保在所有測試前正確設定環境
"""

import os
import sys
from pathlib import Path

# 將專案根目錄加入 Python 路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 修正 PyTorch 2.10 的 weights_only 預設值問題
# 必須在導入任何模組之前設定
os.environ['TORCH_LOAD_WEIGHTS_ONLY'] = '0'

import torch

# Monkey patch torch.load 以支援舊版模型
_original_torch_load = torch.load

def _patched_torch_load(*args, **kwargs):
    kwargs.setdefault('weights_only', False)
    return _original_torch_load(*args, **kwargs)

torch.load = _patched_torch_load
