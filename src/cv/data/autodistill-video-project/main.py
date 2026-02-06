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

def process_video(video_path: str, data_root: str = "data"):
    """
    處理單一影片：提取影格、標記、產生資料集
    """
    # 取得影片檔名（不含副檔名）作為資料夾名稱
    video_name = os.path.splitext(os.path.basename(video_path))[0]

    # 為這個影片建立獨立的目錄
    IMAGES_DIR = os.path.join(data_root, "images", video_name)
    DATASET_DIR = os.path.join(data_root, "datasets", video_name)
    TEMP_DIR = os.path.join(data_root, "temp_images", video_name)

    print(f"\n{'='*60}")
    print(f"Processing video: {video_name}")
    print(f"{'='*60}")

    # 1. 提取影格
    extract_frames(video_path, IMAGES_DIR, stride=20)

    # 2. 定義 Ontology
    ontology = CaptionOntology({
        "yellow price tag with dollar amount": "yellow_price",
        "green price tag with dollar amount": "green_price"
    })

    # 3. 初始化模型並標記
    base_model = GroundedSAM(
        ontology=ontology,
        box_threshold=0.22,
        text_threshold=0.20
    )

    print("Starting auto-labeling with Grounded SAM (Limited to 30 images)...")

    # 限制圖片數量以便快速驗證
    limited_images = sorted(glob.glob(os.path.join(IMAGES_DIR, "*.jpg")))[:30]

    if not limited_images:
        print(f"Warning: No images found for {video_name}, skipping...")
        return

    # 建立臨時目錄來存放這 30 張圖
    os.makedirs(TEMP_DIR, exist_ok=True)
    import shutil
    for img in limited_images:
        shutil.copy(img, TEMP_DIR)

    # 執行標記
    base_model.label(
        input_folder=TEMP_DIR,
        extension=".jpg",
        output_folder=DATASET_DIR
    )

    print(f"✓ Dataset created at: {DATASET_DIR}")

def main():
    # 路徑設定
    DATA_ROOT = "data"
    VIDEOS_DIR = os.path.join(DATA_ROOT, "videos")

    # 1. 檢查 videos 目錄是否存在
    if not os.path.exists(VIDEOS_DIR):
        print(f"Error: Videos directory {VIDEOS_DIR} not found!")
        print("Please create the directory and add video files (.mp4)")
        return

    # 2. 掃描所有影片檔案
    video_files = glob.glob(os.path.join(VIDEOS_DIR, "*.mp4"))

    if not video_files:
        print(f"Error: No video files (.mp4) found in {VIDEOS_DIR}")
        return

    print(f"Found {len(video_files)} video(s) to process:")
    for video in video_files:
        print(f"  - {os.path.basename(video)}")

    # 3. 處理每個影片
    for video_path in video_files:
        try:
            process_video(video_path, DATA_ROOT)
        except Exception as e:
            print(f"Error processing {os.path.basename(video_path)}: {e}")
            continue

    print(f"\n{'='*60}")
    print("All videos processed!")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
