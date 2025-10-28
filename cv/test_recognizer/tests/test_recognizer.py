"""
測試 recognizer.py 模組
"""
import json
import os
import pytest
import numpy as np
from pathlib import Path
from PIL import Image
import sys

# 將 src 目錄加入路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.recognizer import PhoneRecognizer


class TestPhoneRecognizer:
    """測試 PhoneRecognizer 類別"""

    @pytest.fixture
    def recognizer(self):
        """建立 PhoneRecognizer 實例"""
        return PhoneRecognizer()

    @pytest.fixture
    def test_image(self, tmp_path):
        """建立測試圖片"""
        # 建立一個簡單的測試圖片
        img = Image.new('RGB', (224, 224), color='red')
        img_path = tmp_path / "test_phone.jpg"
        img.save(img_path)
        return img_path

    @pytest.fixture
    def test_phone_data(self, tmp_path):
        """建立測試用的 phone_data.json"""
        phone_data = {
            "phones": [
                {
                    "id": "test_phone_1",
                    "name": "Test Phone 1",
                    "brand": "TestBrand",
                    "price": 10000,
                    "image_path": "data/phones/test_phone_1/reference.jpg",
                    "features_path": "data/phones/test_phone_1/features.npy"
                }
            ]
        }

        phone_data_file = tmp_path / "phone_data.json"
        with open(phone_data_file, 'w', encoding='utf-8') as f:
            json.dump(phone_data, f, ensure_ascii=False, indent=2)

        # 建立測試圖片
        phones_dir = tmp_path / "data" / "phones" / "test_phone_1"
        phones_dir.mkdir(parents=True)

        img = Image.new('RGB', (224, 224), color='blue')
        img_path = phones_dir / "reference.jpg"
        img.save(img_path)

        return phone_data_file

    def test_load_model(self, recognizer):
        """測試載入 MobileCLIP 模型"""
        recognizer.load_model()

        assert recognizer.model is not None
        assert recognizer.preprocess is not None

    def test_extract_features(self, recognizer, test_image):
        """測試提取圖片特徵"""
        recognizer.load_model()
        features = recognizer.extract_features(test_image)

        assert features is not None
        assert isinstance(features, np.ndarray)
        assert len(features.shape) == 1  # 應該是一維向量
        assert features.shape[0] > 0  # 特徵向量長度 > 0

    def test_extract_features_from_pil(self, recognizer, test_image):
        """測試從 PIL Image 提取特徵"""
        recognizer.load_model()

        # 載入圖片為 PIL Image
        img = Image.open(test_image)
        features = recognizer.extract_features(img)

        assert features is not None
        assert isinstance(features, np.ndarray)

    def test_extract_features_invalid_image(self, recognizer):
        """測試提取無效圖片的特徵"""
        recognizer.load_model()

        with pytest.raises(Exception):
            recognizer.extract_features("nonexistent_image.jpg")

    def test_compute_similarity(self, recognizer):
        """測試計算相似度"""
        # 建立兩個測試特徵向量
        features1 = np.array([1.0, 2.0, 3.0, 4.0])
        features2 = np.array([1.0, 2.0, 3.0, 4.0])

        similarity = recognizer.compute_similarity(features1, features2)

        # 相同向量的相似度應該接近 1
        assert similarity > 0.99
        assert similarity <= 1.0

    def test_compute_similarity_different_vectors(self, recognizer):
        """測試計算不同向量的相似度"""
        features1 = np.array([1.0, 0.0, 0.0, 0.0])
        features2 = np.array([0.0, 1.0, 0.0, 0.0])

        similarity = recognizer.compute_similarity(features1, features2)

        # 正交向量的相似度應該是 0
        assert abs(similarity) < 0.01

    def test_load_phone_features(self, recognizer, tmp_path):
        """測試載入手機特徵"""
        # 建立測試特徵檔案
        features = np.array([1.0, 2.0, 3.0, 4.0])
        features_path = tmp_path / "features.npy"
        np.save(features_path, features)

        loaded_features = recognizer.load_phone_features(features_path)

        assert loaded_features is not None
        assert np.array_equal(loaded_features, features)

    def test_load_phone_features_not_found(self, recognizer):
        """測試載入不存在的特徵檔案"""
        result = recognizer.load_phone_features("nonexistent.npy")
        assert result is None

    def test_save_phone_features(self, recognizer, tmp_path):
        """測試儲存手機特徵"""
        features = np.array([1.0, 2.0, 3.0, 4.0])
        features_path = tmp_path / "features.npy"

        recognizer.save_phone_features(features, features_path)

        # 檢查檔案是否存在
        assert features_path.exists()

        # 載入並驗證
        loaded_features = np.load(features_path)
        assert np.array_equal(loaded_features, features)

    def test_find_best_match(self, recognizer, test_image):
        """測試尋找最佳匹配"""
        recognizer.load_model()

        # 建立測試資料庫
        test_db = {
            "phone1": {
                "features": np.random.rand(512),
                "info": {"name": "Phone 1", "price": 10000}
            },
            "phone2": {
                "features": np.random.rand(512),
                "info": {"name": "Phone 2", "price": 20000}
            }
        }

        # 提取測試圖片特徵
        query_features = recognizer.extract_features(test_image)

        # 尋找最佳匹配
        best_match, similarity = recognizer.find_best_match(query_features, test_db)

        # 應該返回匹配結果
        assert best_match in ["phone1", "phone2"]
        assert 0 <= similarity <= 1

    def test_recognize_threshold(self, recognizer):
        """測試辨識閾值"""
        # 預設閾值應該在合理範圍內
        assert 0 < recognizer.threshold < 1
        assert recognizer.threshold == 0.5  # plan.md 定義 < 0.5 視為無法辨識
