# -*- coding: utf-8 -*-
from fb_graphql_scraper.facebook_graphql_scraper import (
    FacebookGraphqlScraper as fb_graphql_scraper,
)
import json


def print_results(res):
    """統一的結果輸出格式"""
    # 簡潔輸出
    print("=" * 60)
    print(f"用戶: {res['profile'][0]}")
    print(f"追蹤者: {res['profile'][-1]}")
    print(f"共 {len(res['data'])} 篇貼文")
    print("=" * 60)

    for i, post in enumerate(res["data"], 1):
        print(f"\n【貼文 {i}】{post['published_date2']}")
        print(
            f"👍 {post['reaction_count.count']} | 💬 {post['comment_rendering_instance.comments.total_count']} | 📤 {post['share_count.count']}"
        )

        # 顯示內容（前80字）
        content = post["context"].replace("\n", " ")
        # if len(content) > 80:
        #    content = content[:80] + "..."
        print(f"📝 {content}")
        print("-" * 40)

    # 儲存完整資料到 JSON
    with open("facebook_data.json", "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2, ensure_ascii=False, default=str)
    print(f"\n✅ 完整資料已儲存到 facebook_data.json")


## Example.1 - without logging in
if __name__ == "__main__":
    # 設定目標用戶
    facebook_user_name = ""
    facebook_user_id = "100077534854138"
    days_limit = 60  # Number of days within which to scrape posts

    # 修正 1: 使用正確的 Linux ChromeDriver 路徑或設為 None
    driver_path = None  # 讓系統自動尋找，或使用你的實際路徑
    # driver_path = "/usr/local/bin/chromedriver"  # 如果你手動安裝了 ChromeDriver

    print("🔍 開始爬取 Facebook 資料（未登入模式）...")

    try:
        fb_spider = fb_graphql_scraper(driver_path=driver_path, open_browser=False)
        res = fb_spider.get_user_posts(
            fb_username_or_userid=facebook_user_id,
            days_limit=days_limit,
            display_progress=True,
        )

        # 使用統一的輸出格式
        print_results(res)

        # 如果需要查看原始 JSON 格式，取消下面的註解
        # print("\n" + "="*60)
        # print("原始 JSON 資料:")
        # print("="*60)
        # print(json.dumps(res, indent=2, ensure_ascii=False, default=str))

    except Exception as e:
        print(f"❌ 錯誤: {e}")

## Example.2 - login in your facebook account to collect data
# if __name__ == "__main__":
#     # 登入帳號設定
#     facebook_user_name = ""
#     facebook_user_id = "100077534854138"
#     fb_account = "your_facebook_email@gmail.com"  # 修正：使用真實帳號
#     fb_pwd = "your_facebook_password"              # 修正：使用真實密碼
#     days_limit = 60  # Number of days within which to scrape posts
#     driver_path = None  # 修正：使用正確路徑
#
#     print("🔐 開始爬取 Facebook 資料（登入模式）...")
#
#     try:
#         fb_spider = fb_graphql_scraper(
#             fb_account=fb_account,
#             fb_pwd=fb_pwd,
#             driver_path=driver_path,
#             open_browser=False
#         )
#         res = fb_spider.get_user_posts(
#             fb_username_or_userid=facebook_user_id,
#             days_limit=days_limit,
#             display_progress=True
#         )
#
#         # 使用統一的輸出格式
#         print_results(res)
#
#     except Exception as e:
#         print(f"❌ 錯誤: {e}")

"""
使用說明:
1. 未登入模式: 直接執行即可，但可能受到限制
2. 登入模式: 
   - 註解掉 Example.1 的 if __name__ == "__main__": 區塊
   - 取消註解 Example.2 的區塊
   - 填入真實的 Facebook 帳號和密碼
   - 執行程式

注意事項:
- 請遵守 Facebook 的服務條款
- 建議只爬取自己的資料或公開資料
- 登入模式可能獲得更多資料，但也有帳號風險
"""
