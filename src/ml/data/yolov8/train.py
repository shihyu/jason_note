from ultralyticsplus import YOLO
import multiprocessing
import os

if __name__ == "__main__":
    multiprocessing.freeze_support()

    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # load model
    model = YOLO("models/yolov8n.pt")
    results = model.train(
        data="dataset.yaml",
        imgsz=256,
        epochs=30,
        batch=10,
    )
