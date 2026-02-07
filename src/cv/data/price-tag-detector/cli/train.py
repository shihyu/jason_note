"""訓練命令列工具"""

import argparse
import sys
from pathlib import Path

# 添加專案根目錄到 Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.trainer import Trainer, TrainingConfig


def main() -> None:
    """訓練命令主函數"""
    parser = argparse.ArgumentParser(description="訓練 YOLO 價格標籤檢測模型")

    parser.add_argument(
        "--data",
        type=str,
        default="data/dataset/data.yaml",
        help="資料集配置文件路徑",
    )
    parser.add_argument(
        "--epochs", type=int, default=50, help="訓練輪數（預設 50）"
    )
    parser.add_argument(
        "--batch", type=int, default=8, help="批次大小（預設 8）"
    )
    parser.add_argument(
        "--imgsz", type=int, default=640, help="圖片大小（預設 640）"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="yolov8n.pt",
        help="基礎模型（預設 yolov8n.pt）",
    )
    parser.add_argument(
        "--project",
        type=str,
        default="runs/train",
        help="輸出專案目錄",
    )
    parser.add_argument(
        "--name",
        type=str,
        default="price_tag_detector",
        help="訓練名稱",
    )
    parser.add_argument(
        "--patience",
        type=int,
        default=50,
        help="早停耐心值（預設 50）",
    )

    args = parser.parse_args()

    # 創建訓練配置
    config = TrainingConfig(
        data_yaml=args.data,
        epochs=args.epochs,
        batch_size=args.batch,
        img_size=args.imgsz,
        base_model=args.model,
        project=args.project,
        name=args.name,
        patience=args.patience,
    )

    # 創建訓練器
    trainer = Trainer(config)

    # 訓練模型
    best_model_path = trainer.train()

    # 驗證模型
    metrics = trainer.validate()

    # 顯示最終結果
    print(f"\n✅ 訓練完成！")
    print(f"最佳模型: {best_model_path}")
    print(f"\n下一步：")
    print(f"  1. 複製模型到 data/models/: cp {best_model_path} data/models/best.pt")
    print(f"  2. 執行檢測: make detect")


if __name__ == "__main__":
    main()
