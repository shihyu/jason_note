"""測試資料集分割器"""

import os
import shutil
import tempfile
from pathlib import Path

import pytest

from utils.dataset_splitter import DatasetSplitter


class TestDatasetSplitter:
    """測試 DatasetSplitter 類別"""

    @pytest.fixture
    def temp_dataset(self, tmp_path: Path) -> Path:
        """創建臨時測試資料集"""
        # 創建 20 個假圖片和標籤
        images_dir = tmp_path / "images"
        labels_dir = tmp_path / "labels"
        images_dir.mkdir()
        labels_dir.mkdir()

        for i in range(20):
            img_file = images_dir / f"image_{i:03d}.jpg"
            label_file = labels_dir / f"image_{i:03d}.txt"
            img_file.write_text(f"fake image {i}")
            label_file.write_text(f"0 0.5 0.5 0.1 0.1")

        return tmp_path

    @pytest.fixture
    def output_dir(self, tmp_path: Path) -> Path:
        """創建臨時輸出目錄"""
        output = tmp_path / "output"
        output.mkdir()
        return output

    def test_split_ratio(self, temp_dataset: Path, output_dir: Path) -> None:
        """測試 train/valid 分割比例正確（80/20）"""
        images_dir = temp_dataset / "images"
        labels_dir = temp_dataset / "labels"

        splitter = DatasetSplitter(
            images_dir=str(images_dir),
            labels_dir=str(labels_dir),
            output_dir=str(output_dir),
            split_ratio=0.8,
            random_seed=42,
        )

        splitter.split()

        # 驗證分割比例
        train_images = list((output_dir / "train" / "images").glob("*.jpg"))
        valid_images = list((output_dir / "valid" / "images").glob("*.jpg"))

        total = len(train_images) + len(valid_images)
        assert total == 20, f"總圖片數應為 20，實際為 {total}"

        train_ratio = len(train_images) / total
        valid_ratio = len(valid_images) / total

        # 允許 ±5% 的誤差
        assert 0.75 <= train_ratio <= 0.85, f"train 比例 {train_ratio:.2%} 不在 75-85% 範圍"
        assert 0.15 <= valid_ratio <= 0.25, f"valid 比例 {valid_ratio:.2%} 不在 15-25% 範圍"

    def test_no_overlap(self, temp_dataset: Path, output_dir: Path) -> None:
        """測試 train 和 valid 沒有重疊的圖片"""
        images_dir = temp_dataset / "images"
        labels_dir = temp_dataset / "labels"

        splitter = DatasetSplitter(
            images_dir=str(images_dir),
            labels_dir=str(labels_dir),
            output_dir=str(output_dir),
            split_ratio=0.8,
            random_seed=42,
        )

        splitter.split()

        train_images = {f.name for f in (output_dir / "train" / "images").glob("*.jpg")}
        valid_images = {f.name for f in (output_dir / "valid" / "images").glob("*.jpg")}

        overlap = train_images & valid_images
        assert len(overlap) == 0, f"發現 {len(overlap)} 個重疊的圖片"

    def test_labels_exist(self, temp_dataset: Path, output_dir: Path) -> None:
        """測試每個圖片都有對應的標籤檔案"""
        images_dir = temp_dataset / "images"
        labels_dir = temp_dataset / "labels"

        splitter = DatasetSplitter(
            images_dir=str(images_dir),
            labels_dir=str(labels_dir),
            output_dir=str(output_dir),
            split_ratio=0.8,
            random_seed=42,
        )

        splitter.split()

        # 檢查 train
        for img_file in (output_dir / "train" / "images").glob("*.jpg"):
            label_file = output_dir / "train" / "labels" / f"{img_file.stem}.txt"
            assert label_file.exists(), f"train 標籤檔案不存在: {label_file}"

        # 檢查 valid
        for img_file in (output_dir / "valid" / "images").glob("*.jpg"):
            label_file = output_dir / "valid" / "labels" / f"{img_file.stem}.txt"
            assert label_file.exists(), f"valid 標籤檔案不存在: {label_file}"

    def test_random_seed_reproducible(self, temp_dataset: Path, tmp_path: Path) -> None:
        """測試使用固定 seed 結果可重現"""
        images_dir = temp_dataset / "images"
        labels_dir = temp_dataset / "labels"

        output_dir1 = tmp_path / "output1"
        output_dir2 = tmp_path / "output2"
        output_dir1.mkdir()
        output_dir2.mkdir()

        # 第一次分割
        splitter1 = DatasetSplitter(
            images_dir=str(images_dir),
            labels_dir=str(labels_dir),
            output_dir=str(output_dir1),
            split_ratio=0.8,
            random_seed=42,
        )
        splitter1.split()

        # 第二次分割（相同 seed）
        splitter2 = DatasetSplitter(
            images_dir=str(images_dir),
            labels_dir=str(labels_dir),
            output_dir=str(output_dir2),
            split_ratio=0.8,
            random_seed=42,
        )
        splitter2.split()

        # 驗證結果相同
        train_images1 = {f.name for f in (output_dir1 / "train" / "images").glob("*.jpg")}
        train_images2 = {f.name for f in (output_dir2 / "train" / "images").glob("*.jpg")}

        assert train_images1 == train_images2, "使用相同 seed 應該產生相同的分割結果"

    def test_creates_data_yaml(self, temp_dataset: Path, output_dir: Path) -> None:
        """測試生成 data.yaml 配置檔案"""
        import yaml

        images_dir = temp_dataset / "images"
        labels_dir = temp_dataset / "labels"

        splitter = DatasetSplitter(
            images_dir=str(images_dir),
            labels_dir=str(labels_dir),
            output_dir=str(output_dir),
            split_ratio=0.8,
            random_seed=42,
        )

        splitter.split()

        # 驗證 data.yaml 存在
        data_yaml = output_dir / "data.yaml"
        assert data_yaml.exists(), "data.yaml 應該被創建"

        # 驗證內容
        with open(data_yaml) as f:
            config = yaml.safe_load(f)

        assert "train" in config, "data.yaml 缺少 train 欄位"
        assert "val" in config, "data.yaml 缺少 val 欄位"
        assert config["train"] != config["val"], "train 和 val 不應該相同"
