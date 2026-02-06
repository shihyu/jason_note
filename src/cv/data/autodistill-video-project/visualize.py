import os
import cv2
import supervision as sv
import glob
from autodistill_grounded_sam import GroundedSAM
from autodistill.detection import CaptionOntology

def main():
    DATA_ROOT = "data"
    IMAGES_ROOT = os.path.join(DATA_ROOT, "images")
    OUTPUT_DIR = os.path.join(DATA_ROOT, "visualizations")

    # 1. 掃描所有影片的影格目錄
    if not os.path.exists(IMAGES_ROOT):
        print(f"Error: Images directory {IMAGES_ROOT} not found. Run 'make run' first.")
        return

    video_dirs = [d for d in os.listdir(IMAGES_ROOT)
                  if os.path.isdir(os.path.join(IMAGES_ROOT, d))]

    if not video_dirs:
        print(f"Error: No video directories found in {IMAGES_ROOT}")
        return

    # 2. 收集所有影格
    all_images = []
    for video_dir in video_dirs:
        images_path = os.path.join(IMAGES_ROOT, video_dir)
        images = glob.glob(os.path.join(images_path, "*.jpg"))
        all_images.extend(images)

    if not all_images:
        print("Error: No images found")
        return

    # 選取第 5 張（或最後一張如果不足 5 張）
    sample_path = all_images[min(4, len(all_images)-1)]
    print(f"Annotating sample image: {sample_path}")

    # 3. 定義模型
    ontology = CaptionOntology({
        "yellow price tag with dollar amount": "yellow_price",
        "green price tag with dollar amount": "green_price"
    })
    base_model = GroundedSAM(
        ontology=ontology,
        box_threshold=0.22,
        text_threshold=0.20
    )

    # 4. 執行偵測
    image = cv2.imread(sample_path)
    detections = base_model.predict(sample_path)

    if len(detections) == 0:
        print("No objects detected in this frame. Trying another one...")
        # 遍歷尋找有檢測結果的影格
        for path in all_images[:20]:  # 最多嘗試前 20 張
            detections = base_model.predict(path)
            if len(detections) > 0:
                sample_path = path
                image = cv2.imread(path)
                break

    print(f"Detected {len(detections)} object(s) in {sample_path}")

    # 5. 繪製匡線與標籤
    box_annotator = sv.BoxAnnotator()
    label_annotator = sv.LabelAnnotator()

    labels = [
        f"{base_model.ontology.classes()[class_id]} {confidence:0.2f}"
        for class_id, confidence in zip(detections.class_id, detections.confidence)
    ]

    annotated_frame = box_annotator.annotate(
        scene=image.copy(),
        detections=detections
    )
    annotated_frame = label_annotator.annotate(
        scene=annotated_frame,
        detections=detections,
        labels=labels
    )

    # 6. 儲存結果
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_filename = os.path.basename(sample_path).replace(".jpg", "_annotated.jpg")
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    cv2.imwrite(output_path, annotated_frame)
    print(f"Successfully saved annotated image to: {output_path}")

if __name__ == "__main__":
    main()
