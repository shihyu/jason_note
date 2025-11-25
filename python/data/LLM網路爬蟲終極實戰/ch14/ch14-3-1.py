import requests
import json
import time

# Step 1：輸入關鍵字使用SearXNG進行搜尋。
searxng_url = "http://localhost:8888/search"
query = "fChart程式語言教學工具"
params = {
    "q": query,
    "format": "json",
}
response = requests.get(searxng_url, params=params)
results = response.json()
# Step 2：取得搜尋結果的URL清單(只取出前5筆)。
urls = []
for result in results.get("results", [])[:5]:
    urls.append(result.get("url"))
# Step 3：逐一將URL送入Crawl4AI API來爬取資料。
crawl4ai_url = "http://localhost:11235/crawl"
browser_config = {
    "type": "BrowserConfig",
    "params": {
        "headless": True,
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
}
crawler_config = {
    "type": "CrawlerRunConfig",
    "params": {"stream": False,
               "cache_mode": "bypass"} 
}
crawled_data = []
for url in urls:
    payload = {
        "urls": [url],
        "browser_config": browser_config,
        "crawler_config": crawler_config
    }    
    try:
        # 送出 HTTP 請求且指定超時時間
        res = requests.post(crawl4ai_url, json=payload,
                            timeout=30)
        # 檢查HTTP狀態碼
        if res.status_code != 200:
            print(f"API請求失敗，狀態碼: {res.status_code}")
            print(f"回應內容: {res.text[:200]}")
            continue        
        # 檢查回應內容是否為空
        if not res.text.strip():
            print(f"伺服器回應是空的，跳過此URL: {url}")
            continue        
        # 嘗試剖析JSON
        try:
            data = res.json()
        except json.JSONDecodeError as e:
            print(f"JSON剖析失敗: {e}")
             # 顯示前500個字元
            print(f"原始回應內容: {res.text[:500]}") 
            continue        
        # 檢查回應資料結構
        if "results" not in data:
            print(f"缺少'results'鍵: {data}")
            continue        
        if not data["results"] or len(data["results"]) == 0:
            print(f"'results'資料是空的，跳過URL: {url}")
            continue        
        # 檢查指定的鍵是否存在
        result = data["results"][0]
        if "markdown" not in result:
            print(f"缺少'markdown'鍵，跳過URL: {url}")
            continue        
        if "raw_markdown" not in result["markdown"]:
            print(f"缺少'raw_markdown'鍵，跳過URL: {url}")
            continue        
        # 將爬取結果加入串列
        crawled_data.append({
            "url": url,
            "text": result["markdown"]["raw_markdown"]
        })        
        print(f"已經成功爬取: {url}")        
    except requests.exceptions.RequestException as e:
        print(f"網路請求錯誤 ({url}): {e}")
        continue
    except Exception as e:
        print(f"處理URL時發生未預期錯誤 ({url}): {e}")
        continue    
    # 在 HTTP 請求之間稍作停頓，以避免過於頻繁的請求
    time.sleep(1)
# Step 4：儲存爬取結果的資料，儲存成 JSON 檔案。
with open("results.json", "w", encoding="utf-8") as f:
    json.dump(crawled_data, f, ensure_ascii=False,
              indent=2)
print("已經成功儲存爬取結果至 results.json")