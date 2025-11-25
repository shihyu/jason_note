import requests
import json

url = "https://dummyjson.com/auth/login"
data = {
    "username": "emilys",
    "password": "emilyspass"
}
r = requests.post(url, json=data)
if r.status_code == 200:
    token = r.json()['accessToken']
    print("登入成功，取得 token:", token[:50] + "...")
else:
    print("登入失敗")