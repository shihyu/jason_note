import requests

url = "http://localhost:11235/crawl"
headers = {
    "Content-Type": "application/json"
}
data = {
    "urls": ["https://example.com"],
    "crawler_config": {
        "type": "CrawlerRunConfig",
        "params": {
            "scraping_strategy": {
                "type": "LXMLWebScrapingStrategy",
                "params": {}
            },
            "exclude_social_media_domains": [
                "facebook.com",
                "twitter.com",
                "x.com",
                "linkedin.com",
                "instagram.com",
                "pinterest.com",
                "tiktok.com",
                "snapchat.com",
                "reddit.com"
            ],
            "stream": True
        }
    }
}

response = requests.post(url, headers=headers, json=data)

# 如果 response 是 stream 的，建議逐行讀取
if response.ok:
    for line in response.iter_lines():
        if line:
            print(line.decode('utf-8'))
else:
    print("Request failed with status code:", response.status_code)
    print(response.text)
