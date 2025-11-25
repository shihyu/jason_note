import requests
from bs4 import BeautifulSoup

URL = "https://www.ptt.cc/bbs/Gossiping/index.html"

r = requests.get(URL, cookies={"over18": "1"})
if r.status_code == requests.codes.ok:
    r.encoding = "utf8"
    soup = BeautifulSoup(r.text, "lxml")
    tag_divs = soup.find_all("div", class_="r-ent")
    for tag in tag_divs:
        if tag.find('a'): # 是否有<a>標籤
            tag_a = tag.find("a")
            print(tag_a["href"])
            print(tag_a.text)
            print(tag.find("div", class_="author").string)
else:
    print("HTTP請求錯誤..." + URL)