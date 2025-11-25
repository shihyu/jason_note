# 匯入必要模組
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time

# 建立 WebDriver Service 物件
service = Service(ChromeDriverManager().install())

# 使用 WebDriver 建立 Chrome 瀏覽器實例
driver = webdriver.Chrome(service=service)

try:
    # 打開登入頁面網址
    driver.get("https://fchart.github.io/test/login.html")

    # 稍等幾秒，確保網頁元素已載入（可視情況調整）
    time.sleep(2)

    # 找到帳號輸入欄位，輸入 'joe'
    username_field = driver.find_element(By.CSS_SELECTOR, '.login-form-field[type="text"]')
    username_field.send_keys("joe")

    # 找到密碼輸入欄位，輸入 '12345678'
    password_field = driver.find_element(By.CSS_SELECTOR, '.login-form-field[type="password"]')
    password_field.send_keys("12345678")

    # 找到登入按鈕並點擊
    login_button = driver.find_element(By.CSS_SELECTOR, '#login-form-submit')
    login_button.click()

    # 等待頁面跳轉或登入處理完成
    time.sleep(2)

    # 取得並顯示 <title> 標籤的內容
    page_title = driver.title
    print(f"登入後的網頁標題是：{page_title}")

finally:
    # 關閉瀏覽器
    driver.quit()

