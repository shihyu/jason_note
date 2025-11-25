import requests

URL = "https://www.momoshop.com.tw/search/"

headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
           'AppleWebKit/537.36 (KHTML, like Gecko)'
           'Chrome/63.0.3239.132 Safari/537.36'}
r = requests.get(URL+"searchShop.jsp?keyword=Apple", headers=headers)
if r.status_code == requests.codes.ok:
    print(r.text)        
else:
    print("HTTP請求錯誤..." + URL)