#!/usr/bin/env python3
"""
批次辨識手機圖片（只載入一次模型）
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.recognizer import PhoneRecognizer
from src.database import PhoneDatabase


def main():
    """批次辨識範例"""
    # 要辨識的圖片列表
    images = [
        "data/phones/apple_iphone_15_pro/reference.jpg",
        "data/phones/apple_iphone_14_pro/reference.jpg",
        # 可以加入更多圖片...
    ]

    print("=" * 60)
    print("批次手機圖片辨識")
    print("=" * 60)

    # 1. 載入模型（只載入一次）
    print("\n[1/3] 載入 MobileCLIP 模型...")
    t1 = time.time()
    recognizer = PhoneRecognizer()
    recognizer.load_model()
    print(f"✓ 模型載入完成 ({(time.time()-t1)*1000:.0f} ms)")

    # 2. 載入資料庫（只載入一次）
    print("\n[2/3] 準備手機資料庫...")
    t2 = time.time()
    db = PhoneDatabase()
    db.load_data()

    phone_database = {}
    project_root = Path(__file__).parent

    for phone_id, phone_info in db.phones.items():
        features_path = project_root / phone_info["features_path"]
        features = recognizer.load_phone_features(features_path)

        if features is None:
            image_path = project_root / phone_info["image_path"]
            if image_path.exists():
                features = recognizer.extract_features(image_path)
                recognizer.save_phone_features(features, features_path)

        if features is not None:
            phone_database[phone_id] = {
                "features": features,
                "info": phone_info
            }

    print(f"✓ 準備完成，共 {len(phone_database)} 支手機 ({(time.time()-t2)*1000:.0f} ms)")

    # 3. 批次辨識圖片（速度很快）
    print(f"\n[3/3] 辨識 {len(images)} 張圖片...")
    print("=" * 60)

    total_recognize_time = 0

    for i, image_path in enumerate(images, 1):
        if not Path(image_path).exists():
            print(f"\n[{i}/{len(images)}] ✗ 圖片不存在: {image_path}")
            continue

        # 辨識圖片
        t = time.time()
        result = recognizer.recognize(image_path, phone_database)
        elapsed = time.time() - t
        total_recognize_time += elapsed

        # 顯示結果
        print(f"\n[{i}/{len(images)}] {image_path}")
        if result:
            print(f"  ✓ {result['info']['name']} (信心度: {result['similarity']:.1%}, {elapsed*1000:.0f} ms)")
        else:
            print(f"  ✗ 無法辨識 ({elapsed*1000:.0f} ms)")

    # 統計
    print("\n" + "=" * 60)
    print("⏱️  效能統計")
    print("=" * 60)
    print(f"圖片數量：{len(images)} 張")
    print(f"總辨識時間：{total_recognize_time*1000:.0f} ms")
    print(f"平均每張：{total_recognize_time/len(images)*1000:.0f} ms")
    print("=" * 60)


if __name__ == "__main__":
    main()
