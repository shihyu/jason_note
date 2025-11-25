from bs4 import BeautifulSoup

with open("Example.html", "r", encoding="utf8") as fp:
    soup = BeautifulSoup(fp, "lxml")
# 找出class和id屬性值的標籤
tag_div = soup.select("#q1")
print(tag_div[0].p.a.string)
tag_span = soup.select("span#email")
print(tag_span[0].string)
tag_div = soup.select("#q1, #q2")  # 多個id屬性
for item in tag_div:
    print(item.p.a.string)
print("-----------")
tag_div = soup.find("div")  # 第1個<div>標籤
tag_p = tag_div.select(".question")   
for item in tag_p:
    print(item.a["href"])
tag_li = soup.select("[class~=selected]")
for item in tag_li:
    print(item)
    