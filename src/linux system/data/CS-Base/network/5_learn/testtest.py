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
                # 提取圖像文件名稱
                filename = url.split("/")[-1]
                # 構造目標文件路徑
                filepath = os.path.join(target_dir, filename)
                # 寫入文件
                with open(filepath, "wb") as img_file:
                    img_file.write(response.content)
                    print(f"下載圖像 {filename} 成功！")
        except Exception as e:
            print(f"下載圖像失敗: {e}")
