import requests
from bs4 import BeautifulSoup

r = requests.get("https://fchart.github.io/test.html")
r.encoding = "utf-8"
soup = BeautifulSoup(r.text, "lxml")

fp = open("test.txt", "w", encoding="utf8")
fp.write(soup.prettify())
print("寫入檔案test.txt...")
fp.close()
