import requests
import time

URL = "http://books.toscrape.com/catalogue/page-{0}.html"

for i in range(1, 10):
    url = URL.format(i) 
    r = requests.get(url)
    print(r.status_code)
    print("等待5秒鐘...")
    time.sleep(5) 
