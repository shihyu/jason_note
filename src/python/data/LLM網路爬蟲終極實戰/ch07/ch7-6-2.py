from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time, csv

URL="https://fchart.github.io/ML/nba_items.html"

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.implicitly_wait(10)
driver.get(URL)
pages_remaining = True
page_num = 1
while pages_remaining:
    soup = BeautifulSoup(driver.page_source, "lxml")
    tag_table = soup.select_one("#our-table")
    rows = tag_table.find_all("tr")
    csvfile = "NBA_Products" + str(page_num) + ".csv"
    with open(csvfile, 'w+', newline='', encoding='utf-8-sig') as fp:
        writer = csv.writer(fp)
        for row in rows:
            lst = []
            for cell in row.find_all(["td", "th"]):
                lst.append(cell.text.replace("\n","").
                           replace("\r","").
                           strip())
            writer.writerow(lst)
    print("儲存頁面:", page_num)
    try:   
        next_link = driver.find_element(By.CLASS_NAME, "nextbtn")
        if next_link:
            next_link.click()
            time.sleep(5)
            page_num = page_num + 1
        else:
            pages_remaining = False
    except Exception:
        pages_remaining = False        
driver.quit()