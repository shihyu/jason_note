"""
測試 database.py 模組
"""
import json
import os
import pytest
from pathlib import Path
import sys

# 將 src 目錄加入路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.database import PhoneDatabase


class TestPhoneDatabase:
    """測試 PhoneDatabase 類別"""

    @pytest.fixture
    def test_phone_data(self, tmp_path):
        """建立測試用的 phone_data.json"""
        phone_data = {
            "phones": [
                {
                    "id": "apple_iphone_15_pro",
                    "name": "iPhone 15 Pro",
                    "brand": "Apple",
                    "price": 36900,
                    "currency": "TWD",
                    "specs": {
                        "display": "6.1 吋 Super Retina XDR",
                        "processor": "A17 Pro 晶片",
                        "camera": "48MP 主鏡頭"
                    },
                    "description": "採用航太級鈦金屬設計",
                    "image_path": "data/phones/apple_iphone_15_pro/reference.jpg",
                    "image_url": "https://example.com/iphone.jpg",
                    "features_path": "data/phones/apple_iphone_15_pro/features.npy"
                },
                {
                    "id": "samsung_galaxy_s24_ultra",
                    "name": "Samsung Galaxy S24 Ultra",
                    "brand": "Samsung",
                    "price": 42900,
                    "currency": "TWD",
                    "specs": {
                        "display": "6.8 吋 Dynamic AMOLED 2X",
                        "processor": "Snapdragon 8 Gen 3",
                        "camera": "200MP 主鏡頭"
                    },
                    "description": "旗艦級 Android 手機",
                    "image_path": "data/phones/samsung_galaxy_s24_ultra/reference.jpg",
                    "image_url": "https://example.com/s24.jpg",
                    "features_path": "data/phones/samsung_galaxy_s24_ultra/features.npy"
                }
            ]
        }

        phone_data_file = tmp_path / "phone_data.json"
        with open(phone_data_file, 'w', encoding='utf-8') as f:
            json.dump(phone_data, f, ensure_ascii=False, indent=2)

        return phone_data_file

    @pytest.fixture
    def database(self, test_phone_data):
        """建立 PhoneDatabase 實例"""
        return PhoneDatabase(data_file=test_phone_data)

    def test_load_data(self, database):
        """測試載入資料"""
        database.load_data()

        assert database.phones is not None
        assert len(database.phones) == 2
        assert "apple_iphone_15_pro" in database.phones
        assert "samsung_galaxy_s24_ultra" in database.phones

    def test_load_data_file_not_found(self):
        """測試載入不存在的檔案"""
        db = PhoneDatabase(data_file="nonexistent.json")

        with pytest.raises(FileNotFoundError):
            db.load_data()

    def test_get_phone_by_id(self, database):
        """測試根據 ID 查詢手機"""
        database.load_data()

        phone = database.get_phone_by_id("apple_iphone_15_pro")

        assert phone is not None
        assert phone["name"] == "iPhone 15 Pro"
        assert phone["brand"] == "Apple"
        assert phone["price"] == 36900

    def test_get_phone_by_id_not_found(self, database):
        """測試查詢不存在的手機"""
        database.load_data()

        phone = database.get_phone_by_id("nonexistent_phone")

        assert phone is None

    def test_get_all_phones(self, database):
        """測試取得所有手機"""
        database.load_data()

        all_phones = database.get_all_phones()

        assert len(all_phones) == 2
        assert all_phones[0]["name"] == "iPhone 15 Pro"
        assert all_phones[1]["name"] == "Samsung Galaxy S24 Ultra"

    def test_list_phones(self, database, capsys):
        """測試列出所有手機（CLI 輸出）"""
        database.load_data()
        database.list_phones()

        captured = capsys.readouterr()
        output = captured.out

        # 檢查輸出包含手機資訊
        assert "iPhone 15 Pro" in output
        assert "Apple" in output
        assert "36,900" in output  # 價格有千分位逗號
        assert "Samsung Galaxy S24 Ultra" in output

    def test_search_by_brand(self, database):
        """測試根據品牌搜尋"""
        database.load_data()

        apple_phones = database.search_by_brand("Apple")

        assert len(apple_phones) == 1
        assert apple_phones[0]["name"] == "iPhone 15 Pro"

    def test_search_by_brand_case_insensitive(self, database):
        """測試品牌搜尋（不區分大小寫）"""
        database.load_data()

        apple_phones = database.search_by_brand("apple")

        assert len(apple_phones) == 1
        assert apple_phones[0]["brand"] == "Apple"

    def test_search_by_price_range(self, database):
        """測試根據價格範圍搜尋"""
        database.load_data()

        # 搜尋 30000-40000 的手機
        phones = database.search_by_price_range(30000, 40000)

        assert len(phones) == 1
        assert phones[0]["name"] == "iPhone 15 Pro"

    def test_get_phone_count(self, database):
        """測試取得手機數量"""
        database.load_data()

        count = database.get_phone_count()

        assert count == 2

    def test_phone_exists(self, database):
        """測試檢查手機是否存在"""
        database.load_data()

        assert database.phone_exists("apple_iphone_15_pro") is True
        assert database.phone_exists("nonexistent_phone") is False

    def test_get_phone_image_path(self, database):
        """測試取得手機圖片路徑"""
        database.load_data()

        image_path = database.get_phone_image_path("apple_iphone_15_pro")

        assert image_path == "data/phones/apple_iphone_15_pro/reference.jpg"

    def test_get_phone_image_path_not_found(self, database):
        """測試取得不存在手機的圖片路徑"""
        database.load_data()

        image_path = database.get_phone_image_path("nonexistent_phone")

        assert image_path is None
