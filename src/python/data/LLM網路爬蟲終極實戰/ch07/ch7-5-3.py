from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import time

# 使用 WebDriver Manager 自動下載並設定 ChromeDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)
driver.implicitly_wait(10)
url = "https://fchart.github.io/test/dropdown_menu.html"
driver.get(url)

menu = driver.find_element(By.CSS_SELECTOR, "#about-link")
item = driver.find_element(By.CSS_SELECTOR, "#about-dropdown > a:nth-child(2)")

actions = ActionChains(driver)
actions.move_to_element(menu)
actions.click(item)
actions.perform()
time.sleep(5)
driver.quit()