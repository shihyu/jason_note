# 匯入所需模組
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time

# 建立 Chrome 瀏覽器的 Service 物件
service = Service(ChromeDriverManager().install())

# 設定 Chrome 瀏覽器選項（可視需求調整，例如加上 headless 模式）
options = webdriver.ChromeOptions()
options.add_argument('--start-maximized')  # 最大化視窗

# 啟動 Chrome 瀏覽器
driver = webdriver.Chrome(service=service, options=options)

# 前往登入頁面
driver.get('https://fchart.github.io/test/login.html')

# 等待網頁載入
time.sleep(2)

# 輸入帳號 "tom" 至文字欄位（使用 CSS 選擇器）
username_input = driver.find_element(By.CSS_SELECTOR, '.login-form-field[type="text"]')
username_input.send_keys('tom')

# 輸入密碼 "12345678" 至密碼欄位
password_input = driver.find_element(By.CSS_SELECTOR, '.login-form-field[type="password"]')
password_input.send_keys('12345678')

# 點擊登入按鈕
login_button = driver.find_element(By.CSS_SELECTOR, '#login-form-submit')
login_button.click()

# 等待對話框出現
time.sleep(2)

# 點擊對話框中的確認按鈕
confirm_button = driver.find_element(By.CSS_SELECTOR, '#dialog_example button')
confirm_button.click()

# 等待頁面更新
time.sleep(1)

# 取得 <title> 標籤的文字內容
page_title = driver.title
print("頁面標題為：", page_title)

# 關閉瀏覽器
driver.quit()
