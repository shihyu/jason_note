"""
手機資料庫管理模組
負責載入、查詢、管理 phone_data.json 中的手機資料
"""
import json
from pathlib import Path
from typing import Dict, List, Optional
import argparse


class PhoneDatabase:
    """手機資料庫管理類別"""

    def __init__(self, data_file: Path = None):
        """
        初始化資料庫

        Args:
            data_file: phone_data.json 路徑，預設使用 data/phone_data.json
        """
        if data_file is None:
            self.project_root = Path(__file__).parent.parent
            self.data_file = self.project_root / "data" / "phone_data.json"
        else:
            self.data_file = Path(data_file)

        self.phones = {}  # 以 phone_id 為 key 的字典

    def load_data(self):
        """
        載入 phone_data.json

        Raises:
            FileNotFoundError: 檔案不存在
        """
        if not self.data_file.exists():
            raise FileNotFoundError(f"檔案不存在: {self.data_file}")

        with open(self.data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 將手機資料轉換為字典格式（以 id 為 key）
        self.phones = {}
        for phone in data.get("phones", []):
            phone_id = phone.get("id")
            if phone_id:
                self.phones[phone_id] = phone

    def get_phone_by_id(self, phone_id: str) -> Optional[Dict]:
        """
        根據 ID 查詢手機

        Args:
            phone_id: 手機 ID

        Returns:
            Optional[Dict]: 手機資料字典，不存在返回 None
        """
        return self.phones.get(phone_id)

    def get_all_phones(self) -> List[Dict]:
        """
        取得所有手機資料

        Returns:
            List[Dict]: 手機資料列表
        """
        return list(self.phones.values())

    def search_by_brand(self, brand: str) -> List[Dict]:
        """
        根據品牌搜尋手機

        Args:
            brand: 品牌名稱（不區分大小寫）

        Returns:
            List[Dict]: 符合的手機列表
        """
        brand_lower = brand.lower()
        results = []

        for phone in self.phones.values():
            if phone.get("brand", "").lower() == brand_lower:
                results.append(phone)

        return results

    def search_by_price_range(self, min_price: int, max_price: int) -> List[Dict]:
        """
        根據價格範圍搜尋手機

        Args:
            min_price: 最低價格
            max_price: 最高價格

        Returns:
            List[Dict]: 符合的手機列表
        """
        results = []

        for phone in self.phones.values():
            price = phone.get("price", 0)
            if min_price <= price <= max_price:
                results.append(phone)

        return results

    def get_phone_count(self) -> int:
        """
        取得手機數量

        Returns:
            int: 手機數量
        """
        return len(self.phones)

    def phone_exists(self, phone_id: str) -> bool:
        """
        檢查手機是否存在

        Args:
            phone_id: 手機 ID

        Returns:
            bool: 是否存在
        """
        return phone_id in self.phones

    def get_phone_image_path(self, phone_id: str) -> Optional[str]:
        """
        取得手機圖片路徑

        Args:
            phone_id: 手機 ID

        Returns:
            Optional[str]: 圖片路徑，不存在返回 None
        """
        phone = self.get_phone_by_id(phone_id)
        if phone:
            return phone.get("image_path")
        return None

    def list_phones(self):
        """列出所有手機（CLI 輸出）"""
        if not self.phones:
            print("資料庫中沒有手機資料")
            return

        print(f"\n手機資料庫 (共 {len(self.phones)} 支手機)")
        print("=" * 80)

        for i, phone in enumerate(self.phones.values(), 1):
            print(f"\n[{i}] {phone['name']}")
            print(f"    品牌: {phone['brand']}")
            print(f"    價格: NT$ {phone['price']:,}")
            print(f"    ID: {phone['id']}")

            # 顯示規格
            if "specs" in phone:
                print(f"    規格:")
                for key, value in phone["specs"].items():
                    print(f"      - {key}: {value}")

        print("\n" + "=" * 80)

    def format_phone_info(self, phone: Dict) -> str:
        """
        格式化手機資訊為字串

        Args:
            phone: 手機資料字典

        Returns:
            str: 格式化的手機資訊
        """
        lines = []
        lines.append("=" * 60)
        lines.append(f"手機型號：{phone['name']}")
        lines.append(f"品牌：{phone['brand']}")
        lines.append(f"價格：NT$ {phone['price']:,}")
        lines.append("")
        lines.append("規格：")

        # 顯示規格
        if "specs" in phone:
            for key, value in phone["specs"].items():
                lines.append(f"  • {key}: {value}")

        # 顯示介紹
        if "description" in phone:
            lines.append("")
            lines.append("介紹：")
            lines.append(f"  {phone['description']}")

        lines.append("=" * 60)

        return "\n".join(lines)


def main():
    """主程式入口"""
    parser = argparse.ArgumentParser(description="手機資料庫管理程式")
    parser.add_argument(
        "--list",
        action="store_true",
        help="列出所有手機"
    )
    parser.add_argument(
        "--id",
        type=str,
        help="查詢指定 ID 的手機"
    )
    parser.add_argument(
        "--brand",
        type=str,
        help="搜尋指定品牌的手機"
    )

    args = parser.parse_args()

    # 建立資料庫實例
    db = PhoneDatabase()

    try:
        db.load_data()
    except FileNotFoundError as e:
        print(f"錯誤: {e}")
        print("請先執行 'make init-data' 初始化手機資料")
        return

    # 執行對應操作
    if args.list:
        db.list_phones()
    elif args.id:
        phone = db.get_phone_by_id(args.id)
        if phone:
            print(db.format_phone_info(phone))
        else:
            print(f"找不到手機: {args.id}")
    elif args.brand:
        phones = db.search_by_brand(args.brand)
        if phones:
            print(f"\n找到 {len(phones)} 支 {args.brand} 手機:")
            for phone in phones:
                print(f"  - {phone['name']} (NT$ {phone['price']:,})")
        else:
            print(f"找不到 {args.brand} 品牌的手機")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
