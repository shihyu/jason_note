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
# 定位密碼欄位
pwd1 = driver.find_element(By.XPATH, "//form/input[2][@name='password']")
print(pwd1.get_attribute("type"))
pwd2 = driver.find_element(By.XPATH, "//form[@id='loginForm']/input[2]")
print(pwd2.get_attribute("type"))
pwd3 = driver.find_element(By.XPATH, "//input[@name='password']")
print(pwd3.get_attribute("type"))
driver.quit()
