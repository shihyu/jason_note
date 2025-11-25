import json
import os
import requests

# 偽裝成瀏覽器的 headers
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
}

# 載入 JSON 檔案
with open('pttbeauty.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# 圖片儲存資料夾
save_folder = 'downloaded_images'
os.makedirs(save_folder, exist_ok=True)

# 處理每一篇文章
for index, post in enumerate(data, start=1):
    file_urls = post.get("file_urls", [])
    
    if not file_urls:
        print(f"[{index}] 無圖片，略過：{post['title']}")
        continue

    print(f"[{index}] 下載文章：{post['title']}，共 {len(file_urls)} 張圖")

    for i, url in enumerate(file_urls, start=1):
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()  # 若狀態碼非 200，會拋出例外

            # 從 URL 擷取檔名
            filename = url.split("/")[-1]
            filepath = os.path.join(save_folder, filename)

            # 寫入檔案
            with open(filepath, "wb") as f:
                f.write(response.content)

            print(f"    ✅ 圖片 {i}: {filename} 下載完成")

        except Exception as e:
            print(f"    ❌ 圖片 {i}: {url} 下載失敗，錯誤：{e}")

print("\n所有圖片處理完畢！")
