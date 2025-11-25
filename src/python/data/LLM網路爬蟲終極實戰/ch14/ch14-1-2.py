import httpx

async def crawl():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:11235/crawl",
            json={
                "urls": [
                    "https://example.com"
                ],
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
        )
        return response.json()
    
import asyncio
import json

async def main():
    result = await crawl()
    if result:
        print("爬取成功！")
        print(json.dumps(result, indent=2,
                         ensure_ascii=False))
    else:
        print("爬取失敗！")

asyncio.run(main())