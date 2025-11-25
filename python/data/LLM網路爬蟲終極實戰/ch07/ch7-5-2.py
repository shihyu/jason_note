from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# 使用 WebDriver Manager 自動下載並設定 ChromeDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)
driver.implicitly_wait(10)
url = "http://127.0.0.1:8888"
driver.get(url)

keyword = driver.find_element(By.CSS_SELECTOR, "input#q")
keyword.send_keys("XPath")
keyword.send_keys(Keys.ENTER)

items = driver.find_elements(By.XPATH, "//article[contains(@class, 'result')]")

for item in items:
    p = item.find_element(By.CSS_SELECTOR, "p.content")
    print(p.text)
    a = item.find_element(By.TAG_NAME, "a")   
    print(a.get_attribute("href"))
    
driver.quit()