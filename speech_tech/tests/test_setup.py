"""
基本設定測試
驗證測試框架和環境配置
"""

import sys
from pathlib import Path


def test_imports():
    """測試必要套件是否可以正常導入"""
    import sherpa_onnx
    import numpy
    import scipy
    import requests

    assert sherpa_onnx is not None
    assert numpy is not None
    assert scipy is not None
    assert requests is not None


def test_project_structure(project_root, fixtures_dir, outputs_dir):
    """測試專案目錄結構"""
    # 檢查目錄存在
    assert project_root.exists()
    assert fixtures_dir.exists()
    assert outputs_dir.exists()

    # 檢查關鍵目錄
    src_dir = project_root / "src" / "sherpa_onnx_demo"
    assert src_dir.exists()
    assert (src_dir / "__init__.py").exists()


def test_python_path(project_root):
    """測試 Python 路徑設定"""
    src_dir = str(project_root / "src")
    assert src_dir in sys.path or any(src_dir in p for p in sys.path)
