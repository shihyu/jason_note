import requests

r = requests.get("https://fchart.github.io/test2.html")
r.encoding = "utf-8"

fp = open("test2.txt", "w", encoding="utf8")
fp.write(r.text)
print("寫入檔案test2.txt...")
fp.close()
