from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# 使用 WebDriver Manager 自動下載並設定 ChromeDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)
driver.implicitly_wait(10)
driver.get("https://fchart.github.io/test.html")
print(driver.title)
soup = BeautifulSoup(driver.page_source, "lxml")
fp = open("test.html", "w", encoding="utf8")
fp.write(soup.prettify())
print("寫入檔案test.html...")
fp.close()
driver.quit()
