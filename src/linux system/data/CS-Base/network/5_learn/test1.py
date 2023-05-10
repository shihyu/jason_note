import os
import re
import requests
import cv2
import numpy as np

# 設置要讀取的文件路徑
file_path = "./learn_network.md"

# 設置下載目標目錄
target_dir = "images"

# 設置轉換後的圖檔格式
target_ext = ".jpg"

# 創建目標目錄
if not os.path.exists(target_dir):
    os.makedirs(target_dir)

# 定義正則表達式來匹配圖像URL
with open(file_path, "r") as f:
    text = f.read()
    pattern = r"\!\[.*?\]\((.*?)\)"
    image_urls = re.findall(pattern, text)

    for img in image_urls:
        print(img)
    input()

    for url in image_urls:
        try:
            print(url)
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                # 取得圖像的文件名和擴展名
                filename = url.split("/")[-1]
                ext = os.path.splitext(filename)[1].lower()
                img_array = np.asarray(bytearray(response.content), dtype=np.uint8)
                img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                filename = os.path.splitext(filename)[0] + target_ext
                filepath = os.path.join(target_dir, filename)
                cv2.imwrite(filepath, img)
                print(filename + " 下載成功")
            else:
                print(filename + " 下載失敗")
        except Exception as e:
            print(f"下載圖像失敗: {e}")

