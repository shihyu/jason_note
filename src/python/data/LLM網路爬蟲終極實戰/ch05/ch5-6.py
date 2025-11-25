import requests

url = "https://fchart.github.io/img/Butterfly.png"
path = "Butterfly.png"
response = requests.get(url, stream=True)
if response.status_code == 200:
    with open(path, 'wb') as fp:
        for chunk in response:
            fp.write(chunk)
    print("圖檔Butterfly.png已經下載")
else:
    print("錯誤! HTTP請求失敗...")
   