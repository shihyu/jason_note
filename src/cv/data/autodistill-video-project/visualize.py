import os
import cv2
import supervision as sv
import glob
from autodistill_grounded_sam import GroundedSAM
from autodistill.detection import CaptionOntology

def main():
    DATA_ROOT = "data"
    IMAGES_DIR = os.path.join(DATA_ROOT, "images")
    OUTPUT_PATH = os.path.join(DATA_ROOT, "annotated_sample.jpg")

    # 1. 挑選一張有影格的圖片
    sample_images = glob.glob(os.path.join(IMAGES_DIR, "*.jpg"))
    if not sample_images:
        print("Error: No images found in data/images")
        return
    
    # 我們選取第 5 張
    sample_path = sample_images[min(4, len(sample_images)-1)]
    print(f"Annotating sample image: {sample_path}")

    # 2. 定義模型: 方案 A - 最精確（明確指定包含金額數字）
    ontology = CaptionOntology({
        "yellow price tag with dollar amount": "yellow_price",
        "green price tag with dollar amount": "green_price"
    })
    base_model = GroundedSAM(
        ontology=ontology,
        box_threshold=0.22,
        text_threshold=0.20
    )

    # 3. 執行偵測
    image = cv2.imread(sample_path)
    detections = base_model.predict(sample_path)

    if len(detections) == 0:
        print("No butterflies detected in this specific frame. Trying another one...")
        # 遍歷尋找有東西的影格
        for path in sample_images:
            detections = base_model.predict(path)
            if len(detections) > 0:
                sample_path = path
                image = cv2.imread(path)
                break
    
    print(f"Detected {len(detections)} butterflies in {sample_path}")

    # 4. 繪製匡線與標籤
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

    # 5. 儲存結果
    cv2.imwrite(OUTPUT_PATH, annotated_frame)
    print(f"Successfully saved annotated image to: {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
