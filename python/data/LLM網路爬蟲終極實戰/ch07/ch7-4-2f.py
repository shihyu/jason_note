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
link1 = driver.find_element(By.LINK_TEXT, 'Continue')
print(link1.text)
link2 = driver.find_element(By.PARTIAL_LINK_TEXT, 'Conti')
print(link2.text)
link3 = driver.find_element(By.LINK_TEXT, '取消')
print(link3.text)
link4 = driver.find_element(By.PARTIAL_LINK_TEXT, '取')
print(link4.text)
driver.quit()