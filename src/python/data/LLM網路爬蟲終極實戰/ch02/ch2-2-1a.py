import requests 

r = requests.get("http://www.google.com")
if r.status_code == 200:
    print("HTTP請求成功...")
else:
    print("HTTP請求失敗...")
    