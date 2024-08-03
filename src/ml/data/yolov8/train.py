from ultralyticsplus import YOLO
import multiprocessing
import os

if __name__ == "__main__":
    multiprocessing.freeze_support()
    # 獲取當前腳本的目錄
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 構建 data.yaml 的絕對路徑
    data_yaml_path = os.path.join(current_dir, "data.yaml")
    print(data_yaml_path)
    input()

    # load model
    model = YOLO("models/yolov8n.pt")
    results = model.train(
        data=data_yaml_path,
        imgsz=256,
        epochs=30,
        batch=10,
    )
