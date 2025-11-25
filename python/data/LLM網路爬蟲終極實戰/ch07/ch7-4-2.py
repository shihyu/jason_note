from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import os

# 使用 WebDriver Manager 自動下載並設定 ChromeDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)
html_path = "file:///" +os.path.abspath("ch7-4.html")
driver.implicitly_wait(10)
driver.get(html_path)
form = driver.find_element(By.ID, "loginForm")
print(form.tag_name)
print(form.get_attribute("id"))
driver.quit()
