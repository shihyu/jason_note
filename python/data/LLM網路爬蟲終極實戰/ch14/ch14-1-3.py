import requests

browser_config = {
    "type": "BrowserConfig",
    "params": {"headless": True}
}
crawler_config = {
    "type": "CrawlerRunConfig",
    "params": {"stream": False,
               "cache_mode": "bypass"} 
}
payload = {
    "urls": ["https://fchart.github.io/"],
    "browser_config": browser_config,
    "crawler_config": crawler_config
}
response = requests.post(
    "http://localhost:11235/crawl", 
    json=payload
)
print(f"狀態碼: {response.status_code}")
if response.ok:
    print(response.json()["results"][0]
          ["html"][:200])
    print("------------------")
    print(response.json()["results"][0]
          ["markdown"]["raw_markdown"][:200])
else:
    print(f"錯誤: {response.text}")