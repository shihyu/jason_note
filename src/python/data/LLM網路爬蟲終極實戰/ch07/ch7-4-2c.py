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
# 定位<form>標籤
form1 = driver.find_element(By.XPATH, "/html/body/form[1]")
print(form1.tag_name)
form2 = driver.find_element(By.XPATH, "//form[1]")
print(form2.tag_name)
form3 = driver.find_element(By.XPATH, "//form[@id='loginForm']")
print(form3.tag_name)
driver.quit()
