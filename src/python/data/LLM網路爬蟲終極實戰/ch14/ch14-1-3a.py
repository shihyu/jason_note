import requests

schema = {
    "name": "News Items",
    "baseSelector": "div.card",
    "fields": [
       {"name": "image_url", "selector": ".card-img-top",
        "type": "attribute", "attribute": "src" },
       {"name": "description", "selector": ".card-text", "type": "text"},
       {"name": "sponsor_amount", "selector": ".pull-right.price",
        "type": "text"},
       {"name": "reviews_count", "selector": ".text-muted", "type": "text"}
    ]
}
crawler_config = {
    "type": "CrawlerRunConfig",
    "params": {
               "excluded_tags":["header", "footer"],
               "css_selector":"div.row",
               "stream": False,
               "cache_mode": "bypass",
               "extraction_strategy":{
                   "type": "JsonCssExtractionStrategy",
                   "params": { "schema": schema }    
               }
              } 
}
payload = {
    "urls": ["https://fchart.github.io/test/album.html"],
    "crawler_config": crawler_config
}
response = requests.post(
    "http://localhost:11235/crawl", 
    json=payload
)
print(f"狀態碼: {response.status_code}")
if response.ok:
    print(response.json()["results"][0]
          ["extracted_content"])
else:
    print(f"錯誤: {response.text}")