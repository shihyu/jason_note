"""
手機圖片辨識模組
使用 MobileCLIP 提取圖片特徵並進行相似度比對
"""
import os
import warnings

# 抑制警告訊息
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=UserWarning)
os.environ['CUDA_VISIBLE_DEVICES'] = ''  # 明確指定不使用 CUDA

import numpy as np
import torch
import mobileclip
from pathlib import Path
from PIL import Image
from typing import Union, Tuple, Dict, Optional
import argparse


class PhoneRecognizer:
    """手機圖片辨識器"""

    def __init__(self, model_name: str = "mobileclip_s0", threshold: float = 0.5):
        """
        初始化辨識器

        Args:
            model_name: MobileCLIP 模型名稱 (mobileclip_s0, mobileclip_s1, mobileclip_s2)
            threshold: 相似度閾值（< threshold 視為無法辨識）
        """
        self.model_name = model_name
        self.threshold = threshold
        self.model = None
        self.preprocess = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

    def load_model(self):
        """載入 MobileCLIP 模型"""
        print(f"載入模型: {self.model_name} (device: {self.device})")

        # 取得模型路徑
        project_root = Path(__file__).parent.parent
        model_path = project_root / "ml-mobileclip" / "checkpoints" / f"{self.model_name}.pt"

        if not model_path.exists():
            raise FileNotFoundError(
                f"模型檔案不存在: {model_path}\n"
                f"請先執行: bash ml-mobileclip/get_pretrained_models.sh"
            )

        # 載入模型
        self.model, _, self.preprocess = mobileclip.create_model_and_transforms(
            self.model_name,
            pretrained=str(model_path)
        )

        self.model.to(self.device)
        self.model.eval()

        print("✓ 模型載入完成")

    @torch.no_grad()
    def extract_features(self, image: Union[str, Path, Image.Image]) -> np.ndarray:
        """
        從圖片提取特徵向量

        Args:
            image: 圖片路徑或 PIL Image

        Returns:
            np.ndarray: 特徵向量

        Raises:
            Exception: 圖片無法載入或處理
        """
        if self.model is None:
            raise RuntimeError("模型尚未載入，請先呼叫 load_model()")

        # 載入圖片
        if isinstance(image, (str, Path)):
            if not Path(image).exists():
                raise FileNotFoundError(f"圖片不存在: {image}")
            img = Image.open(image).convert('RGB')
        elif isinstance(image, Image.Image):
            img = image.convert('RGB')
        else:
            raise ValueError("image 必須是檔案路徑或 PIL Image")

        # 預處理圖片
        image_tensor = self.preprocess(img).unsqueeze(0).to(self.device)

        # 提取特徵
        features = self.model.encode_image(image_tensor)

        # L2 正規化
        features = features / features.norm(dim=-1, keepdim=True)

        return features.cpu().numpy().flatten()

    def compute_similarity(self, features1: np.ndarray, features2: np.ndarray) -> float:
        """
        計算兩個特徵向量的餘弦相似度

        Args:
            features1: 特徵向量 1
            features2: 特徵向量 2

        Returns:
            float: 相似度 (0-1)
        """
        # 確保向量已正規化
        features1 = features1 / np.linalg.norm(features1)
        features2 = features2 / np.linalg.norm(features2)

        # 計算餘弦相似度
        similarity = np.dot(features1, features2)

        return float(similarity)

    def load_phone_features(self, features_path: Union[str, Path]) -> Optional[np.ndarray]:
        """
        載入手機特徵向量

        Args:
            features_path: 特徵檔案路徑 (.npy)

        Returns:
            Optional[np.ndarray]: 特徵向量，失敗返回 None
        """
        features_path = Path(features_path)

        if not features_path.exists():
            return None

        try:
            features = np.load(features_path)
            return features
        except Exception as e:
            print(f"載入特徵失敗: {features_path}")
            print(f"錯誤: {e}")
            return None

    def save_phone_features(self, features: np.ndarray, features_path: Union[str, Path]):
        """
        儲存手機特徵向量

        Args:
            features: 特徵向量
            features_path: 儲存路徑 (.npy)
        """
        features_path = Path(features_path)
        features_path.parent.mkdir(parents=True, exist_ok=True)

        np.save(features_path, features)

    def find_best_match(
        self,
        query_features: np.ndarray,
        phone_database: Dict[str, Dict]
    ) -> Tuple[Optional[str], float]:
        """
        在資料庫中尋找最佳匹配

        Args:
            query_features: 查詢圖片的特徵向量
            phone_database: 手機資料庫 {phone_id: {"features": ..., "info": ...}}

        Returns:
            Tuple[Optional[str], float]: (最佳匹配的 phone_id, 相似度)
        """
        best_phone_id = None
        best_similarity = 0.0

        for phone_id, data in phone_database.items():
            phone_features = data["features"]
            similarity = self.compute_similarity(query_features, phone_features)

            if similarity > best_similarity:
                best_similarity = similarity
                best_phone_id = phone_id

        return best_phone_id, best_similarity

    def recognize(
        self,
        image_path: Union[str, Path],
        phone_database: Dict[str, Dict],
        verbose: bool = False
    ) -> Optional[Dict]:
        """
        辨識手機圖片

        Args:
            image_path: 圖片路徑
            phone_database: 手機資料庫
            verbose: 是否顯示詳細資訊

        Returns:
            Optional[Dict]: 辨識結果，包含手機資訊和相似度
        """
        if verbose:
            print(f"\n正在辨識: {image_path}")

        # 提取查詢圖片特徵
        try:
            query_features = self.extract_features(image_path)
        except Exception as e:
            print(f"✗ 圖片處理失敗: {e}")
            return None

        if verbose:
            print("✓ 特徵提取完成")

        # 尋找最佳匹配
        best_phone_id, similarity = self.find_best_match(query_features, phone_database)

        if verbose:
            print(f"最佳匹配: {best_phone_id} (相似度: {similarity:.4f})")

        # 判斷是否達到閾值
        if similarity < self.threshold:
            if verbose:
                print(f"✗ 相似度低於閾值 {self.threshold}，無法辨識")
            return None

        # 返回辨識結果
        result = {
            "phone_id": best_phone_id,
            "similarity": similarity,
            "info": phone_database[best_phone_id]["info"]
        }

        return result


def main():
    """主程式入口"""
    import time

    parser = argparse.ArgumentParser(description="手機圖片辨識程式")
    parser.add_argument(
        "--image",
        type=str,
        required=True,
        help="手機圖片路徑"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="顯示詳細資訊"
    )
    parser.add_argument(
        "--benchmark",
        action="store_true",
        help="顯示效能統計"
    )

    args = parser.parse_args()

    # 檢查圖片是否存在
    if not Path(args.image).exists():
        print(f"錯誤: 圖片不存在: {args.image}")
        return

    total_start = time.time()

    print("=" * 60)
    print("手機圖片辨識系統")
    print("=" * 60)

    # 初始化辨識器
    recognizer = PhoneRecognizer()

    # 載入模型
    print("\n[1/4] 載入 MobileCLIP 模型...")
    t1 = time.time()
    recognizer.load_model()
    t1_elapsed = time.time() - t1
    if args.benchmark:
        print(f"      ⏱️  模型載入時間: {t1_elapsed*1000:.0f} ms")

    # 載入手機資料庫
    print("\n[2/4] 載入手機資料庫...")
    t2 = time.time()
    from database import PhoneDatabase

    db = PhoneDatabase()
    try:
        db.load_data()
    except FileNotFoundError:
        print("錯誤: phone_data.json 不存在")
        print("請先執行 'python src/scraper.py --init' 初始化資料")
        return

    print(f"✓ 載入 {db.get_phone_count()} 支手機資料")
    t2_elapsed = time.time() - t2
    if args.benchmark:
        print(f"      ⏱️  資料庫載入時間: {t2_elapsed*1000:.0f} ms")

    # 建立手機資料庫（提取或載入特徵）
    print("\n[3/4] 準備手機特徵資料庫...")
    t3 = time.time()
    phone_database = {}
    project_root = Path(__file__).parent.parent

    for phone_id, phone_info in db.phones.items():
        features_path = project_root / phone_info["features_path"]

        # 嘗試載入已存在的特徵
        features = recognizer.load_phone_features(features_path)

        if features is None:
            # 特徵不存在，從圖片提取
            print(f"  提取特徵: {phone_info['name']}")
            image_path = project_root / phone_info["image_path"]

            if not image_path.exists():
                print(f"  ✗ 圖片不存在，跳過: {image_path}")
                continue

            try:
                features = recognizer.extract_features(image_path)
                recognizer.save_phone_features(features, features_path)
                print(f"  ✓ 特徵已儲存: {features_path}")
            except Exception as e:
                print(f"  ✗ 特徵提取失敗: {e}")
                continue

        phone_database[phone_id] = {
            "features": features,
            "info": phone_info
        }

    print(f"✓ 準備完成，共 {len(phone_database)} 支手機可供比對")
    t3_elapsed = time.time() - t3
    if args.benchmark:
        print(f"      ⏱️  特徵準備時間: {t3_elapsed*1000:.0f} ms")

    # 辨識圖片
    print("\n[4/4] 辨識手機圖片...")
    t4 = time.time()
    result = recognizer.recognize(args.image, phone_database, verbose=args.verbose)
    t4_elapsed = time.time() - t4
    if args.benchmark:
        print(f"      ⏱️  圖片辨識時間: {t4_elapsed*1000:.0f} ms")

    # 顯示結果
    print("\n" + "=" * 60)
    if result:
        print("✓ 辨識成功！")
        print(f"\n信心度: {result['similarity']:.1%}")
        print("=" * 60)

        phone = result["info"]
        print(f"\n手機型號：{phone['name']}")
        print(f"品牌：{phone['brand']}")
        print(f"價格：NT$ {phone['price']:,}")

        if "specs" in phone:
            print(f"\n規格：")
            for key, value in phone["specs"].items():
                print(f"  • {key}: {value}")

        if "description" in phone:
            print(f"\n介紹：")
            print(f"  {phone['description']}")

        print("=" * 60)
    else:
        print("✗ 無法辨識此手機")
        print("可能原因：")
        print("  • 圖片品質不佳或角度不正確")
        print("  • 手機型號不在資料庫中")
        print("  • 相似度低於閾值（0.5）")
        print("=" * 60)

    # 效能統計
    if args.benchmark:
        total_elapsed = time.time() - total_start
        print("\n" + "=" * 60)
        print("⏱️  效能統計")
        print("=" * 60)
        print(f"模型載入：{t1_elapsed*1000:>8.0f} ms  ({t1_elapsed/total_elapsed*100:>5.1f}%)")
        print(f"資料庫載入：{t2_elapsed*1000:>6.0f} ms  ({t2_elapsed/total_elapsed*100:>5.1f}%)")
        print(f"特徵準備：{t3_elapsed*1000:>7.0f} ms  ({t3_elapsed/total_elapsed*100:>5.1f}%)")
        print(f"圖片辨識：{t4_elapsed*1000:>7.0f} ms  ({t4_elapsed/total_elapsed*100:>5.1f}%)")
        print("-" * 60)
        print(f"總時間：{total_elapsed*1000:>9.0f} ms  (100.0%)")
        print("=" * 60)


if __name__ == "__main__":
    main()
