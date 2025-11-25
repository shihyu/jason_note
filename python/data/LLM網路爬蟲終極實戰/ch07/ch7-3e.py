from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# 使用 WebDriver Manager 自動下載並設定 ChromeDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)
driver.implicitly_wait(10)
driver.get("https://fchart.github.io/test.html")
# 使用BeautifulSoup剖析HTML網頁
soup = BeautifulSoup(driver.page_source, "lxml")
tag_h3 = soup.find("h3") 
print(tag_h3.string)
tag_p = soup.find("p") 
print(tag_p.string)
driver.quit()