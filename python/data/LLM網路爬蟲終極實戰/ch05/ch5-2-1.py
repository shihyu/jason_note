from bs4 import BeautifulSoup 

with open("Example.html", "r", encoding="utf8") as fp:
    soup = BeautifulSoup(fp, "lxml")
# 使用屬性向下走訪
print(soup.html.head.title.string)
print(soup.html.head.meta["charset"])
# 使用div屬性取得第1個<div>標籤
print(soup.html.body.div.div.p.a.string)
