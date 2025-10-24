"""
pytest 測試配置檔案
定義共用的 fixtures 和測試路徑
"""

import os
import sys
from pathlib import Path
import pytest

# 將 src 目錄加入 Python 路徑
PROJECT_ROOT = Path(__file__).parent.parent
SRC_DIR = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

# 定義測試路徑
TESTS_DIR = Path(__file__).parent
FIXTURES_DIR = TESTS_DIR / "fixtures"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"


@pytest.fixture(scope="session")
def project_root():
    """專案根目錄"""
    return PROJECT_ROOT


@pytest.fixture(scope="session")
def fixtures_dir():
    """測試 fixtures 目錄"""
    FIXTURES_DIR.mkdir(exist_ok=True)
    return FIXTURES_DIR


@pytest.fixture(scope="session")
def outputs_dir():
    """輸出檔案目錄"""
    OUTPUTS_DIR.mkdir(exist_ok=True)
    return OUTPUTS_DIR


@pytest.fixture(autouse=True)
def cleanup_temp_files(request):
    """
    自動清理測試產生的臨時檔案
    在每個測試完成後執行
    """
    yield

    # 測試完成後，清理 fixtures 目錄中的臨時檔案
    # 保留 .gitkeep 和預先準備的測試檔案
    if FIXTURES_DIR.exists():
        for file in FIXTURES_DIR.glob("temp_*"):
            if file.is_file():
                try:
                    file.unlink()
                except Exception as e:
                    print(f"Warning: Failed to delete {file}: {e}")
