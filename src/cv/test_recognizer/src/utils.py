#!/usr/bin/env python3
"""工具函數模組"""

import os
import logging
from datetime import datetime
from pathlib import Path


def setup_logger(name: str, log_file: str = None, level=logging.INFO):
    """設定日誌記錄器"""
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # 控制台處理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)

    # 格式化
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 檔案處理器
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def ensure_dir(directory: str) -> Path:
    """確保目錄存在"""
    path = Path(directory)
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_timestamp() -> str:
    """取得時間戳記"""
    return datetime.now().strftime('%Y%m%d_%H%M%S')


def format_time(seconds: float) -> str:
    """格式化時間顯示"""
    if seconds < 1:
        return f"{seconds * 1000:.2f}ms"
    elif seconds < 60:
        return f"{seconds:.2f}s"
    else:
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes}m {secs:.2f}s"
