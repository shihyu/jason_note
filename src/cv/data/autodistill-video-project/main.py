import os
import cv2
import glob
import supervision as sv
from autodistill_grounded_sam import GroundedSAM
from autodistill.detection import CaptionOntology
from tqdm import tqdm

def extract_frames(video_path: str, output_dir: str, stride: int = 10):
    """
    從影片中提取影格。
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    print(f"Opening video: {video_path}")
    container = cv2.VideoCapture(video_path)
    if not container.isOpened():
        print(f"Error: Could not open video {video_path}")
        return

    frame_idx = 0
    saved_count = 0
    while True:
        success, frame = container.read()
        if not success:
            break
        
        if frame_idx % stride == 0:
            output_path = os.path.join(output_dir, f"frame-{saved_count:05d}.jpg")
            cv2.imwrite(output_path, frame)
            saved_count += 1
        
        frame_idx += 1
    
    container.release()
    print(f"Extracted {saved_count} frames to {output_dir}")

def main():
    # 路徑設定
    DATA_ROOT = "data"
    VIDEO_PATH = os.path.join(DATA_ROOT, "2d8131bd-e3d9-4949-8e22-5fdaf4d368a7.mp4")
    IMAGES_DIR = os.path.join(DATA_ROOT, "images")
    DATASET_DIR = os.path.join(DATA_ROOT, "dataset")

    # 1. 確保影片存在
    if not os.path.exists(VIDEO_PATH):
        print(f"Error: Video file {VIDEO_PATH} not found!")
        return

    # 2. 提取影格 (稍微增加密度)
    extract_frames(VIDEO_PATH, IMAGES_DIR, stride=20)

    # 3. 定義 Ontology: 方案 A - 最精確（明確指定包含金額數字）
    ontology = CaptionOntology({
        "yellow price tag with dollar amount": "yellow_price",
        "green price tag with dollar amount": "green_price"
    })

    # 4. 初始化模型並標記
    base_model = GroundedSAM(
        ontology=ontology,
        box_threshold=0.22,
        text_threshold=0.20
    )
    print("Starting auto-labeling with highly sensitive Grounded SAM (Limited to 30 images)...")
    
    # 限制圖片數量以便快速驗證
    limited_images = sorted(glob.glob(os.path.join(IMAGES_DIR, "*.jpg")))[:30]
    
    # 手動建立一個臨時目錄來存放這 30 張圖
    TEMP_DIR = os.path.join(DATA_ROOT, "temp_images")
    os.makedirs(TEMP_DIR, exist_ok=True)
    import shutil
    for img in limited_images:
        shutil.copy(img, TEMP_DIR)

    base_model.label(
        input_folder=TEMP_DIR,
        extension=".jpg",
        output_folder=DATASET_DIR
    )

    print(f"Process complete. YOLOv8 dataset created at: {DATASET_DIR}")

if __name__ == "__main__":
    main()