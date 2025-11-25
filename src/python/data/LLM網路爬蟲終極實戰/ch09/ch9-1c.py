import requests
from bs4 import BeautifulSoup

URL = "https://www.ptt.cc/bbs/NBA/index.html"
DELETED = BeautifulSoup("<a href='Deleted'>本文已刪除</a>", "lxml").a

r = requests.get(URL)
if r.status_code == requests.codes.ok:
    r.encoding = "utf8"
    soup = BeautifulSoup(r.text, "lxml")
    tag_divs = soup.find_all("div", class_="r-ent")
    for tag in tag_divs:
        tag_a = tag.find("a") or DELETED
        print(tag_a["href"])
        print(tag_a.text)
        print(tag.find("div", class_="author").string)
else:
    print("HTTP請求錯誤..." + URL)
