from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

# 設定 Chrome 瀏覽器選項
chrome_options = Options()
chrome_options.add_argument('--start-maximized')  # 啟動時最大化視窗

# 使用 WebDriver Manager 自動安裝並建立 Chrome WebDriver Service
service = Service(ChromeDriverManager().install())

# 建立 WebDriver 物件並開啟 Chrome 瀏覽器
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    # 開啟登入頁面
    driver.get("https://fchart.github.io/test/login.html")

    # 等待頁面載入
    time.sleep(1)

    # 輸入使用者名稱 "mary" 至文字欄位
    username_field = driver.find_element(By.CSS_SELECTOR, '.login-form-field[type="text"]')
    username_field.send_keys('mary')

    # 輸入密碼 "12345678" 至密碼欄位
    password_field = driver.find_element(By.CSS_SELECTOR, '.login-form-field[type="password"]')
    password_field.send_keys('12345678')

    # 按下登入按鈕
    login_button = driver.find_element(By.CSS_SELECTOR, '#login-form-submit')
    login_button.click()

    # 等待彈出確認對話框
    time.sleep(1)

    # 切換至 alert 對話框並按下 Enter（接受）
    alert = driver.switch_to.alert
    alert.accept()

    # 等待網頁跳轉完成
    time.sleep(1)

    # 抓取 <title> 標籤內容並顯示
    page_title = driver.title
    print("登入後的網頁標題是：", page_title)

finally:
    # 關閉瀏覽器
    driver.quit()

