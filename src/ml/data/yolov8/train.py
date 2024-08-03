from ultralyticsplus import YOLO
import multiprocessing
from pathlib import Path
from loguru import logger


def setup_logging():
    logger.add("training.log", rotation="10 MB")


def get_data_yaml_path():
    current_dir = Path(__file__).parent.absolute()
    data_yaml_path = current_dir / "data.yaml"
    if not data_yaml_path.exists():
        raise FileNotFoundError(f"data.yaml not found at {data_yaml_path}")
    return str(data_yaml_path)


def load_model(model_path):
    if not Path(model_path).exists():
        raise FileNotFoundError(f"Model file not found at {model_path}")
    return YOLO(model_path)


def train_model(model, data_path, img_size, epochs, batch_size):
    try:
        results = model.train(
            data=data_path,
            imgsz=img_size,
            epochs=epochs,
            batch=batch_size,
        )
        return results
    except Exception as e:
        logger.error(f"Training failed: {e}")
        raise


def main():
    setup_logging()

    try:
        data_yaml_path = get_data_yaml_path()
        logger.info(f"Using data.yaml at: {data_yaml_path}")

        model_path = "models/yolov8n.pt"
        model = load_model(model_path)
        logger.info(f"Model loaded from: {model_path}")

        results = train_model(
            model=model,
            data_path=data_yaml_path,
            img_size=256,
            epochs=30,
            batch_size=10,
        )

        logger.success("Training completed successfully.")
        logger.info(f"Results: {results}")

    except Exception as e:
        logger.exception(f"An error occurred: {e}")


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
