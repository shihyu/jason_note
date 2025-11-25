# 驗證安裝是否成功
from importlib.metadata import version, PackageNotFoundError

try:
    pkg_version = version("scrapegraphai")
    print(f"ScrapeGraphAI版本: {pkg_version}")
except PackageNotFoundError:
    print("無法取得 ScrapeGraphAI 的版本資訊")

# 檢查Playwright是否正常運作
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto("https://example.com")
    print("Playwright安裝成功")
    browser.close()