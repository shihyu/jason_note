"""
手機資料爬取模組
負責從 seed_data.json 讀取資料，下載圖片，並生成 phone_data.json
"""
import json
import os
import re
import requests
from pathlib import Path
from typing import Dict, Optional, List
import argparse


class Scraper:
    """手機資料爬取器"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.data_dir = self.project_root / "data"
        self.phones_dir = self.data_dir / "phones"
        self.seed_file = self.data_dir / "seed_data.json"
        self.output_file = self.data_dir / "phone_data.json"

    def load_seed_data(self, seed_file: Path = None) -> Dict:
        """
        載入 seed_data.json

        Args:
            seed_file: seed_data.json 路徑，預設使用 data/seed_data.json

        Returns:
            Dict: 手機資料字典

        Raises:
            FileNotFoundError: 檔案不存在
        """
        if seed_file is None:
            seed_file = self.seed_file

        if not Path(seed_file).exists():
            raise FileNotFoundError(f"檔案不存在: {seed_file}")

        with open(seed_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return data

    def generate_phone_id(self, name: str, brand: str) -> str:
        """
        生成手機 ID（用於目錄名稱和識別）

        Args:
            name: 手機名稱
            brand: 品牌名稱

        Returns:
            str: 手機 ID (例如: apple_iphone_15_pro)
        """
        # 將品牌和名稱轉小寫，移除特殊字元，用底線連接
        combined = f"{brand} {name}".lower()
        # 只保留英文字母、數字和空格
        cleaned = re.sub(r'[^a-z0-9\s]', '', combined)
        # 將空格替換為底線
        phone_id = re.sub(r'\s+', '_', cleaned.strip())

        return phone_id

    def download_image(self, url: str, save_path: Path, timeout: int = 10) -> bool:
        """
        下載圖片

        Args:
            url: 圖片 URL
            save_path: 儲存路徑
            timeout: 超時時間（秒）

        Returns:
            bool: 是否下載成功
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()

            # 確保目錄存在
            save_path.parent.mkdir(parents=True, exist_ok=True)

            # 儲存圖片
            with open(save_path, 'wb') as f:
                f.write(response.content)

            return True

        except Exception as e:
            print(f"下載圖片失敗: {url}")
            print(f"錯誤: {e}")
            return False

    def process_phone_data(self, phone: Dict, phones_dir: Path) -> Optional[Dict]:
        """
        處理單個手機資料（下載圖片、生成完整資料）

        Args:
            phone: 手機資料字典
            phones_dir: 手機圖片儲存目錄

        Returns:
            Optional[Dict]: 處理後的手機資料，失敗返回 None
        """
        try:
            # 生成手機 ID
            phone_id = self.generate_phone_id(phone["name"], phone["brand"])

            # 建立手機專屬目錄
            phone_dir = phones_dir / phone_id
            phone_dir.mkdir(parents=True, exist_ok=True)

            # 下載圖片
            image_path = phone_dir / "reference.jpg"
            image_url = phone["image_url"]

            print(f"正在處理: {phone['name']} ({phone['brand']})")
            print(f"  下載圖片: {image_url}")

            if self.download_image(image_url, image_path):
                print(f"  ✓ 圖片已儲存: {image_path}")

                # 生成完整資料
                processed_phone = {
                    "id": phone_id,
                    "name": phone["name"],
                    "brand": phone["brand"],
                    "price": phone["price"],
                    "currency": "TWD",
                    "specs": phone["specs"],
                    "description": phone["description"],
                    "image_path": str(image_path.relative_to(self.project_root)),
                    "image_url": image_url,
                    "features_path": str((phone_dir / "features.npy").relative_to(self.project_root))
                }

                return processed_phone
            else:
                print(f"  ✗ 圖片下載失敗，跳過此手機")
                return None

        except Exception as e:
            print(f"處理手機資料失敗: {phone.get('name', 'Unknown')}")
            print(f"錯誤: {e}")
            return None

    def save_phone_data(self, data: Dict, output_file: Path = None):
        """
        儲存 phone_data.json

        Args:
            data: 手機資料字典
            output_file: 輸出檔案路徑
        """
        if output_file is None:
            output_file = self.output_file

        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"\n✓ 手機資料已儲存: {output_file}")

    def run(self):
        """執行完整的資料收集流程"""
        print("=" * 60)
        print("手機資料收集程式")
        print("=" * 60)

        # 載入 seed_data.json
        print(f"\n1. 載入 seed_data.json: {self.seed_file}")
        try:
            seed_data = self.load_seed_data()
            phone_count = len(seed_data.get("phones", []))
            print(f"   ✓ 找到 {phone_count} 支手機")
        except FileNotFoundError as e:
            print(f"   ✗ 錯誤: {e}")
            return

        # 確保目錄存在
        self.phones_dir.mkdir(parents=True, exist_ok=True)

        # 處理每支手機
        print(f"\n2. 下載手機圖片到: {self.phones_dir}")
        processed_phones = []

        for i, phone in enumerate(seed_data["phones"], 1):
            print(f"\n[{i}/{phone_count}]")
            processed = self.process_phone_data(phone, self.phones_dir)
            if processed:
                processed_phones.append(processed)

        # 儲存結果
        print(f"\n3. 儲存處理結果")
        result_data = {"phones": processed_phones}
        self.save_phone_data(result_data)

        # 統計
        print("\n" + "=" * 60)
        print(f"完成！成功處理 {len(processed_phones)}/{phone_count} 支手機")
        print("=" * 60)


def main():
    """主程式入口"""
    parser = argparse.ArgumentParser(description="手機資料收集程式")
    parser.add_argument(
        "--init",
        action="store_true",
        help="初始化手機資料（下載圖片並生成 phone_data.json）"
    )

    args = parser.parse_args()

    if args.init:
        scraper = Scraper()
        scraper.run()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
