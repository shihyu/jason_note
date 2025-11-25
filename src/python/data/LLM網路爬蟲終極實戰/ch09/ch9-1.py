import requests

URL = "https://www.momoshop.com.tw/search/"

r = requests.get(URL+"searchShop.jsp?keyword=Apple")
if r.status_code == requests.codes.ok:
    print(r.text)        
else:
    print("HTTP請求錯誤..." + URL)
    