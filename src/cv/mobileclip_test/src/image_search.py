#!/usr/bin/env python3
"""圖像搜尋核心模組 - 使用 MobileCLIP 進行以圖找圖"""

import torch
import mobileclip
import numpy as np
from PIL import Image
from pathlib import Path
from typing import List, Tuple, Dict
from tqdm import tqdm
import time

from utils import setup_logger, format_time


logger = setup_logger(__name__)


class MobileCLIPSearchEngine:
    """MobileCLIP 圖像搜尋引擎"""

    def __init__(self, model_name: str = 'mobileclip_s1', device: str = None):
        """
        初始化搜尋引擎

        Args:
            model_name: 模型名稱 (mobileclip_s0, mobileclip_s1, mobileclip_s2)
            device: 裝置 (cuda/cpu)
        """
        self.model_name = model_name
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')

        logger.info(f"初始化 {model_name} 於 {self.device}")

        # 載入模型
        model_path = f'ml-mobileclip/checkpoints/{model_name}.pt'
        self.model, _, self.preprocess = mobileclip.create_model_and_transforms(
            model_name,
            pretrained=model_path
        )

        self.model.eval()
        self.model.to(self.device)

        # 特徵資料庫
        self.database_features = None
        self.database_paths = []

        logger.info(f"✓ 模型載入完成")

    @torch.no_grad()
    def extract_features(self, image: Image.Image) -> np.ndarray:
        """
        提取圖片特徵向量

        Args:
            image: PIL Image

        Returns:
            特徵向量 (numpy array)
        """
        # 預處理
        image_tensor = self.preprocess(image).unsqueeze(0).to(self.device)

        # 提取特徵
        features = self.model.encode_image(image_tensor)

        # L2 正規化
        features = features / features.norm(dim=-1, keepdim=True)

        return features.cpu().numpy().flatten()

    def build_index(self, image_dir: str) -> Dict[str, any]:
        """
        建立圖片索引

        Args:
            image_dir: 圖片目錄

        Returns:
            索引資訊
        """
        image_path = Path(image_dir)
        image_files = list(image_path.glob('*.jpg')) + \
                      list(image_path.glob('*.jpeg')) + \
                      list(image_path.glob('*.png'))

        if not image_files:
            raise ValueError(f"在 {image_dir} 找不到圖片檔案")

        logger.info(f"找到 {len(image_files)} 張圖片")

        features_list = []
        paths_list = []

        start_time = time.time()

        for img_file in tqdm(image_files, desc="建立索引"):
            try:
                image = Image.open(img_file).convert('RGB')
                features = self.extract_features(image)

                features_list.append(features)
                paths_list.append(str(img_file))

            except Exception as e:
                logger.warning(f"處理 {img_file} 失敗: {e}")

        # 儲存索引
        self.database_features = np.vstack(features_list)
        self.database_paths = paths_list

        elapsed = time.time() - start_time

        info = {
            'num_images': len(paths_list),
            'feature_dim': self.database_features.shape[1],
            'time': elapsed,
            'avg_time_per_image': elapsed / len(paths_list) if paths_list else 0
        }

        logger.info(f"✓ 索引建立完成: {len(paths_list)} 張圖片, "
                   f"耗時 {format_time(elapsed)}, "
                   f"平均 {info['avg_time_per_image']*1000:.2f}ms/張")

        return info

    def search(self, query_image: Image.Image, top_k: int = 5) -> List[Tuple[str, float]]:
        """
        搜尋相似圖片

        Args:
            query_image: 查詢圖片
            top_k: 返回前 K 個結果

        Returns:
            [(圖片路徑, 相似度分數), ...]
        """
        if self.database_features is None:
            raise RuntimeError("請先使用 build_index() 建立索引")

        # 提取查詢特徵
        query_features = self.extract_features(query_image)

        # 計算相似度 (cosine similarity)
        similarities = np.dot(self.database_features, query_features)

        # 取得 top-k
        top_indices = np.argsort(similarities)[::-1][:top_k]

        results = [
            (self.database_paths[idx], float(similarities[idx]))
            for idx in top_indices
        ]

        return results

    def get_model_info(self) -> Dict[str, any]:
        """取得模型資訊"""
        total_params = sum(p.numel() for p in self.model.parameters())

        return {
            'model_name': self.model_name,
            'device': self.device,
            'total_params': total_params,
            'total_params_m': f"{total_params / 1e6:.1f}M",
        }


def main():
    """測試程式"""
    logger.info("=" * 60)
    logger.info("MobileCLIP 圖像搜尋引擎測試")
    logger.info("=" * 60)

    # 測試三個模型
    models = ['mobileclip_s0', 'mobileclip_s1', 'mobileclip_s2']

    for model_name in models:
        logger.info(f"\n測試 {model_name}...")

        try:
            engine = MobileCLIPSearchEngine(model_name=model_name)
            info = engine.get_model_info()

            logger.info(f"  模型參數: {info['total_params_m']}")
            logger.info(f"  裝置: {info['device']}")

        except Exception as e:
            logger.error(f"  ✗ 測試失敗: {e}")

    logger.info("\n" + "=" * 60)
    logger.info("✓ 所有模型測試完成")
    logger.info("=" * 60)


if __name__ == '__main__':
    main()
