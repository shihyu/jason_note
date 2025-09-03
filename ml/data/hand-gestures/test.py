from ultralytics import YOLO
from pathlib import Path
from loguru import logger
import cv2


def setup_logging():
    logger.add("detection_single.log", rotation="10 MB")


def detect_single_image(model_path, image_path):
    # 載入模型
    model = YOLO(model_path)
    logger.info(f"Model loaded from: {model_path}")

    # 進行預測
    results = model(image_path)

    # 處理結果
    for r in results:
        logger.info(f"Detected {len(r.boxes)} objects in {Path(image_path).name}")

        for box in r.boxes:
            class_id = int(box.cls[0])
            class_name = model.names[class_id]
            confidence = float(box.conf[0])
            x1, y1, x2, y2 = box.xyxy[0].tolist()

            logger.info(
                f"  {class_name}: {confidence:.2f} at [{x1:.0f}, {y1:.0f}, {x2:.0f}, {y2:.0f}]"
            )

    # 保存結果
    save_path = f"result_{Path(image_path).name}"

    # 使用 plot() 方法繪製結果
    res_plotted = r.plot()
    cv2.imwrite(save_path, res_plotted)
    logger.info(f"Result saved to {save_path}")

    # 顯示圖片
    cv2.imshow("Detection Result", res_plotted)
    cv2.waitKey(0)  # 等待按鍵
    cv2.destroyAllWindows()  # 關閉所有窗口


def main():
    setup_logging()

    try:
        # 設定模型路徑和測試圖片路徑
        model_path = "./models/best.pt"
        image_path = (
            "./dataset/test/images/fist_frame_1176_png.rf.4efdd209b702f3ddb7b354788661fa33.jpg"
        )

        # 執行檢測
        detect_single_image(model_path, image_path)
        logger.success("Detection completed successfully.")

    except Exception as e:
        logger.exception(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
