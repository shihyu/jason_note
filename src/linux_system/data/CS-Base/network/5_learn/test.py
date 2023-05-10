import os
import re
import requests

# 設置要讀取的文件路徑
file_path = "./learn_network.md"

# 設置下載目標目錄
target_dir = "images"

# 創建目標目錄
if not os.path.exists(target_dir):
    os.makedirs(target_dir)

# 定義正則表達式來匹配圖像URL
with open(file_path, "r") as f:
    text = f.read()
    pattern = r"\!\[.*?\]\((.*?)\)"
    image_urls = re.findall(pattern, text)

    for url in image_urls:
        try:
            print(url)
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                filename = url.split("/")[-1]
                filepath = os.path.join(target_dir, filename)
                with open(filepath, "wb") as f:
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)
                    f.close()
                print(filename + " 下載成功")
            else:
                print(filename + " 下載失敗")
        except Exception as e:
            print(f"下載圖像失敗: {e}")
