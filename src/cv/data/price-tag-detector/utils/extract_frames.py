"""從影片提取圖片幀"""
import cv2
from pathlib import Path
from tqdm import tqdm


def extract_frames(video_path: str, output_dir: str) -> int:
    """從影片提取所有幀

    Args:
        video_path: 影片路徑
        output_dir: 輸出目錄

    Returns:
        提取的幀數
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # 開啟影片
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"❌ 無法開啟影片: {video_path}")
        return 0

    # 獲取總幀數
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    print(f"影片資訊: {total_frames} 幀, {fps:.2f} FPS")

    # 提取所有幀
    frame_count = 0
    with tqdm(total=total_frames, desc="提取進度") as pbar:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # 保存幀
            frame_filename = output_path / f"frame-{frame_count:05d}.jpg"
            cv2.imwrite(str(frame_filename), frame)

            frame_count += 1
            pbar.update(1)

    cap.release()
    return frame_count


def main():
    """主函數：提取所有影片的幀"""
    videos_dir = Path("data/videos")
    images_dir = Path("data/images")

    if not videos_dir.exists():
        print(f"❌ 錯誤: {videos_dir} 不存在")
        return

    print("=" * 60)
    print("從影片提取圖片幀")
    print("=" * 60)

    # 處理所有 MP4 影片
    video_files = sorted(videos_dir.glob("*.mp4"))

    if not video_files:
        print(f"❌ 在 {videos_dir} 中沒有找到 MP4 影片")
        return

    total_frames = 0

    for video_file in video_files:
        video_name = video_file.stem  # video1, video2, video3
        output_dir = images_dir / video_name

        print(f"\n處理 {video_file.name}...")
        frames = extract_frames(str(video_file), str(output_dir))
        total_frames += frames
        print(f"✓ 提取 {frames} 幀到 {output_dir}")

    print(f"\n{'=' * 60}")
    print(f"提取完成！")
    print(f"{'=' * 60}")
    print(f"總共提取: {total_frames} 張圖片")
    print(f"輸出位置: {images_dir}")
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    main()
