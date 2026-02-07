"""資料集分割器 - 將資料集分割成 train 和 valid"""

import os
import random
import shutil
from pathlib import Path
from typing import List, Tuple

import yaml


class DatasetSplitter:
    """資料集分割器

    將圖片和標籤資料分割成訓練集和驗證集

    Attributes:
        images_dir: 原始圖片目錄
        labels_dir: 原始標籤目錄
        output_dir: 輸出目錄
        split_ratio: 訓練集佔比（預設 0.8）
        random_seed: 隨機種子（預設 42，確保可重現）
    """

    def __init__(
        self,
        images_dir: str,
        labels_dir: str,
        output_dir: str,
        split_ratio: float = 0.8,
        random_seed: int = 42,
    ) -> None:
        """初始化資料集分割器

        Args:
            images_dir: 原始圖片目錄路徑
            labels_dir: 原始標籤目錄路徑
            output_dir: 輸出目錄路徑
            split_ratio: 訓練集佔比，範圍 [0, 1]
            random_seed: 隨機種子，用於確保結果可重現
        """
        self.images_dir = Path(images_dir)
        self.labels_dir = Path(labels_dir)
        self.output_dir = Path(output_dir)
        self.split_ratio = split_ratio
        self.random_seed = random_seed

        # 驗證輸入
        if not self.images_dir.exists():
            raise ValueError(f"圖片目錄不存在: {self.images_dir}")
        if not self.labels_dir.exists():
            raise ValueError(f"標籤目錄不存在: {self.labels_dir}")
        if not 0 < split_ratio < 1:
            raise ValueError(f"split_ratio 必須在 (0, 1) 範圍內，目前為 {split_ratio}")

    def split(self) -> Tuple[int, int]:
        """執行資料集分割

        Returns:
            (train_count, valid_count): 訓練集和驗證集的圖片數量
        """
        # 設定隨機種子
        random.seed(self.random_seed)

        # 獲取所有圖片
        image_files = self._get_image_files()

        if not image_files:
            raise ValueError(f"在 {self.images_dir} 中沒有找到圖片")

        # 隨機打亂
        random.shuffle(image_files)

        # 計算分割點
        split_idx = int(len(image_files) * self.split_ratio)
        train_files = image_files[:split_idx]
        valid_files = image_files[split_idx:]

        # 創建輸出目錄
        self._create_directories()

        # 複製檔案
        self._copy_files(train_files, "train")
        self._copy_files(valid_files, "valid")

        # 生成 data.yaml
        self._create_data_yaml()

        return len(train_files), len(valid_files)

    def _get_image_files(self) -> List[Path]:
        """獲取所有圖片檔案

        Returns:
            圖片檔案路徑列表
        """
        extensions = [".jpg", ".jpeg", ".png", ".JPG", ".JPEG", ".PNG"]
        image_files = []

        for ext in extensions:
            image_files.extend(self.images_dir.glob(f"*{ext}"))

        return sorted(image_files)

    def _create_directories(self) -> None:
        """創建輸出目錄結構"""
        dirs = [
            self.output_dir / "train" / "images",
            self.output_dir / "train" / "labels",
            self.output_dir / "valid" / "images",
            self.output_dir / "valid" / "labels",
        ]

        for directory in dirs:
            directory.mkdir(parents=True, exist_ok=True)

    def _copy_files(self, image_files: List[Path], split: str) -> None:
        """複製圖片和標籤到指定的 split 目錄

        Args:
            image_files: 圖片檔案列表
            split: "train" 或 "valid"
        """
        images_dest = self.output_dir / split / "images"
        labels_dest = self.output_dir / split / "labels"

        for img_path in image_files:
            # 複製圖片
            shutil.copy(img_path, images_dest / img_path.name)

            # 複製標籤（如果存在）
            label_name = img_path.stem + ".txt"
            label_path = self.labels_dir / label_name

            if label_path.exists():
                shutil.copy(label_path, labels_dest / label_name)

    def _create_data_yaml(self) -> None:
        """生成 YOLO 格式的 data.yaml 配置檔案"""
        config = {
            "path": str(self.output_dir.absolute()),
            "train": "train/images",
            "val": "valid/images",
            "nc": 2,  # 預設類別數
            "names": ["yellow_price", "green_price"],  # 預設類別名稱
        }

        yaml_path = self.output_dir / "data.yaml"

        with open(yaml_path, "w") as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)


def main() -> None:
    """命令列介面"""
    import argparse

    parser = argparse.ArgumentParser(description="資料集分割工具")
    parser.add_argument("--images", required=True, help="圖片目錄路徑")
    parser.add_argument("--labels", required=True, help="標籤目錄路徑")
    parser.add_argument("--output", required=True, help="輸出目錄路徑")
    parser.add_argument("--ratio", type=float, default=0.8, help="訓練集佔比（預設 0.8）")
    parser.add_argument("--seed", type=int, default=42, help="隨機種子（預設 42）")

    args = parser.parse_args()

    splitter = DatasetSplitter(
        images_dir=args.images,
        labels_dir=args.labels,
        output_dir=args.output,
        split_ratio=args.ratio,
        random_seed=args.seed,
    )

    train_count, valid_count = splitter.split()

    print(f"\n{'='*60}")
    print("資料集分割完成！")
    print(f"{'='*60}")
    print(f"訓練集: {train_count} 張圖片")
    print(f"驗證集: {valid_count} 張圖片")
    print(f"輸出目錄: {args.output}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
