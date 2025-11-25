from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

# 使用 WebDriver Manager 自動下載並設定 ChromeDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)
driver.implicitly_wait(10)
driver.get("https://fchart.github.io/test.html")
# 使用Selenium的定位函數
h3 = driver.find_element(By.TAG_NAME, "h3")
print(h3.text)
p = driver.find_element(By.TAG_NAME, "p")
print(p.text)
print("--------------------------------")
html_h3 = h3.get_attribute("innerHTML")
print(html_h3)
html_h3 = h3.get_attribute("outerHTML")
print(html_h3)
driver.quit()