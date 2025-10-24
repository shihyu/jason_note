"""
工具模組
提供音頻下載、轉換等輔助功能
"""

import os
import tarfile
import zipfile
import requests
from pathlib import Path
from typing import Optional
from tqdm import tqdm


# 模型下載 URL
TTS_MODELS = {
    'vits-piper-en_US-lessac-medium': {
        'url': 'https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/vits-piper-en_US-lessac-medium.tar.bz2',
        'model_file': 'en_US-lessac-medium.onnx',
        'tokens': 'tokens.txt',
        'data_dir': 'espeak-ng-data'
    }
}

ASR_MODELS = {
    'zipformer-bilingual-zh-en': {
        'url': 'https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-streaming-zipformer-bilingual-zh-en-2023-02-20.tar.bz2',
        'encoder': 'encoder-epoch-99-avg-1.onnx',
        'decoder': 'decoder-epoch-99-avg-1.onnx',
        'joiner': 'joiner-epoch-99-avg-1.onnx',
        'tokens': 'tokens.txt'
    }
}


def get_cache_dir() -> Path:
    """
    取得緩存目錄

    Returns:
        緩存目錄路徑
    """
    cache_dir = Path.home() / '.cache' / 'sherpa-onnx'
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def download_file(url: str, output_path: Path, desc: Optional[str] = None) -> Path:
    """
    下載檔案並顯示進度條

    Args:
        url: 下載 URL
        output_path: 輸出檔案路徑
        desc: 進度條描述

    Returns:
        下載的檔案路徑
    """
    if output_path.exists():
        print(f"✓ 檔案已存在: {output_path}")
        return output_path

    print(f"正在下載: {url}")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    response = requests.get(url, stream=True)
    response.raise_for_status()

    total_size = int(response.headers.get('content-length', 0))

    with open(output_path, 'wb') as f:
        with tqdm(total=total_size, unit='B', unit_scale=True, desc=desc) as pbar:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    pbar.update(len(chunk))

    print(f"✓ 下載完成: {output_path}")
    return output_path


def extract_archive(archive_path: Path, extract_to: Path) -> Path:
    """
    解壓縮檔案

    Args:
        archive_path: 壓縮檔路徑
        extract_to: 解壓縮目標目錄

    Returns:
        解壓縮後的目錄路徑
    """
    print(f"正在解壓縮: {archive_path}")
    extract_to.mkdir(parents=True, exist_ok=True)

    if archive_path.suffix == '.zip':
        with zipfile.ZipFile(archive_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
    elif archive_path.name.endswith(('.tar.gz', '.tgz')):
        with tarfile.open(archive_path, 'r:gz') as tar_ref:
            tar_ref.extractall(extract_to)
    elif archive_path.name.endswith(('.tar.bz2', '.tbz2')):
        with tarfile.open(archive_path, 'r:bz2') as tar_ref:
            tar_ref.extractall(extract_to)
    elif archive_path.name.endswith('.tar'):
        with tarfile.open(archive_path, 'r') as tar_ref:
            tar_ref.extractall(extract_to)
    else:
        raise ValueError(f"不支援的壓縮格式: {archive_path}")

    print(f"✓ 解壓縮完成: {extract_to}")
    return extract_to


def download_tts_model(model_name: str) -> Path:
    """
    下載 TTS 模型

    Args:
        model_name: 模型名稱

    Returns:
        模型目錄路徑
    """
    if model_name not in TTS_MODELS:
        raise ValueError(f"未知的 TTS 模型: {model_name}")

    model_info = TTS_MODELS[model_name]
    cache_dir = get_cache_dir() / 'tts' / model_name

    # 檢查模型是否已下載
    model_file = cache_dir / model_info['model_file']
    if model_file.exists():
        print(f"✓ TTS 模型已緩存: {cache_dir}")
        return cache_dir

    # 下載模型
    url = model_info['url']
    archive_name = url.split('/')[-1]
    archive_path = cache_dir.parent / archive_name

    download_file(url, archive_path, desc=f"下載 {model_name}")

    # 解壓縮
    extract_archive(archive_path, cache_dir.parent)

    # 清理壓縮檔
    archive_path.unlink()

    # 重命名解壓縮的目錄
    extracted_dir = cache_dir.parent / archive_name.replace('.tar.bz2', '')
    if extracted_dir != cache_dir and extracted_dir.exists():
        if cache_dir.exists():
            import shutil
            shutil.rmtree(cache_dir)
        extracted_dir.rename(cache_dir)

    print(f"✓ TTS 模型已準備好: {cache_dir}")
    return cache_dir


def download_asr_model(model_name: str) -> Path:
    """
    下載 ASR 模型

    Args:
        model_name: 模型名稱

    Returns:
        模型目錄路徑
    """
    if model_name not in ASR_MODELS:
        raise ValueError(f"未知的 ASR 模型: {model_name}")

    model_info = ASR_MODELS[model_name]
    cache_dir = get_cache_dir() / 'asr' / model_name

    # 檢查模型是否已下載
    encoder_file = cache_dir / model_info['encoder']
    if encoder_file.exists():
        print(f"✓ ASR 模型已緩存: {cache_dir}")
        return cache_dir

    # 下載模型
    url = model_info['url']
    archive_name = url.split('/')[-1]
    archive_path = cache_dir.parent / archive_name

    download_file(url, archive_path, desc=f"下載 {model_name}")

    # 解壓縮
    extract_archive(archive_path, cache_dir.parent)

    # 清理壓縮檔
    archive_path.unlink()

    # 重命名解壓縮的目錄
    extracted_dir = cache_dir.parent / archive_name.replace('.tar.bz2', '')
    if extracted_dir != cache_dir and extracted_dir.exists():
        if cache_dir.exists():
            import shutil
            shutil.rmtree(cache_dir)
        extracted_dir.rename(cache_dir)

    print(f"✓ ASR 模型已準備好: {cache_dir}")
    return cache_dir


def download_audio(url: str, output_path: Optional[Path] = None) -> Path:
    """
    從網路下載音頻檔案

    Args:
        url: 音頻檔案 URL
        output_path: 輸出路徑（可選）

    Returns:
        下載的音頻檔案路徑
    """
    if output_path is None:
        filename = url.split('/')[-1]
        output_path = get_cache_dir() / 'audio' / filename

    return download_file(url, output_path, desc="下載音頻檔案")
