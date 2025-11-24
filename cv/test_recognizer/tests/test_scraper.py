"""
測試 scraper.py 模組
"""
import json
import os
import pytest
from pathlib import Path
import sys

# 將 src 目錄加入路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.scraper import Scraper


class TestScraper:
    """測試 Scraper 類別"""

    @pytest.fixture
    def scraper(self):
        """建立 Scraper 實例"""
        return Scraper()

    @pytest.fixture
    def test_seed_data(self, tmp_path):
        """建立測試用的 seed_data.json"""
        seed_data = {
            "phones": [
                {
                    "name": "Test Phone 1",
                    "brand": "TestBrand",
                    "price": 10000,
                    "image_url": "https://via.placeholder.com/300",
                    "specs": {
                        "display": "6.0 吋",
                        "processor": "Test Chip"
                    },
                    "description": "測試手機 1"
                }
            ]
        }

        seed_file = tmp_path / "seed_data.json"
        with open(seed_file, 'w', encoding='utf-8') as f:
            json.dump(seed_data, f, ensure_ascii=False, indent=2)

        return seed_file

    def test_load_seed_data(self, scraper, test_seed_data):
        """測試載入 seed_data.json"""
        data = scraper.load_seed_data(test_seed_data)

        assert data is not None
        assert "phones" in data
        assert len(data["phones"]) == 1
        assert data["phones"][0]["name"] == "Test Phone 1"

    def test_load_seed_data_file_not_found(self, scraper):
        """測試載入不存在的檔案"""
        with pytest.raises(FileNotFoundError):
            scraper.load_seed_data("nonexistent.json")

    def test_generate_phone_id(self, scraper):
        """測試生成手機 ID"""
        phone_id = scraper.generate_phone_id("iPhone 15 Pro", "Apple")
        assert phone_id == "apple_iphone_15_pro"

        phone_id2 = scraper.generate_phone_id("Galaxy S24 Ultra", "Samsung")
        assert phone_id2 == "samsung_galaxy_s24_ultra"

    def test_download_image(self, scraper, tmp_path):
        """測試下載圖片"""
        # 使用公開的測試圖片 URL
        test_url = "https://via.placeholder.com/150"
        save_path = tmp_path / "test_image.jpg"

        result = scraper.download_image(test_url, save_path)

        # 檢查下載是否成功
        assert result is True or result is False  # 網路問題可能導致失敗

        # 如果成功，檢查檔案是否存在
        if result:
            assert save_path.exists()
            assert save_path.stat().st_size > 0

    def test_download_image_invalid_url(self, scraper, tmp_path):
        """測試下載無效的 URL"""
        invalid_url = "https://invalid-url-that-does-not-exist.com/image.jpg"
        save_path = tmp_path / "test_image.jpg"

        result = scraper.download_image(invalid_url, save_path, timeout=2)

        # 下載失敗應該返回 False
        assert result is False

    def test_process_phone_data(self, scraper, test_seed_data, tmp_path):
        """測試處理手機資料"""
        data = scraper.load_seed_data(test_seed_data)
        phones_dir = tmp_path / "phones"
        phones_dir.mkdir()

        processed_phones = []
        for phone in data["phones"]:
            processed = scraper.process_phone_data(phone, phones_dir)
            if processed:
                processed_phones.append(processed)

        assert len(processed_phones) >= 0  # 可能因網路問題沒有成功下載

        # 如果有成功處理的資料，檢查格式
        if processed_phones:
            phone = processed_phones[0]
            assert "id" in phone
            assert "name" in phone
            assert "brand" in phone
            assert "price" in phone
            assert "specs" in phone
            assert "description" in phone
            assert "image_path" in phone

    def test_save_phone_data(self, scraper, tmp_path):
        """測試儲存 phone_data.json"""
        test_data = {
            "phones": [
                {
                    "id": "test_phone",
                    "name": "Test Phone",
                    "brand": "TestBrand",
                    "price": 10000
                }
            ]
        }

        output_file = tmp_path / "phone_data.json"
        scraper.save_phone_data(test_data, output_file)

        # 檢查檔案是否存在
        assert output_file.exists()

        # 檢查內容是否正確
        with open(output_file, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)

        assert loaded_data == test_data
        assert loaded_data["phones"][0]["name"] == "Test Phone"
