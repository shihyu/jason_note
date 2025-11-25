# 同步程式設計
import requests
import time

def sync_crawl():
    urls = ["https://fchart.github.io", "https://www.google.com/",
            "https://httpbin.org"]
    start_time = time.time()
    for url in urls:
        response = requests.get(url)
        print(f"爬取 {url}: {response.status_code}")
    
    print(f"總耗時: {time.time() - start_time:.2f}秒")

sync_crawl()
