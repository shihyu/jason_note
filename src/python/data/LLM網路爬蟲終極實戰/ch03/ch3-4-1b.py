from bs4 import BeautifulSoup

with open("Example.html", "r", encoding="utf8") as fp:
    soup = BeautifulSoup(fp, "lxml")
# 使用class屬性搜尋<li>標籤, 和之下的<span>標籤
tag_li = soup.find(attrs={"class": "response"})
tag_span = tag_li.find("span")
print(tag_span.string)
# 搜尋第2題的第1個<li>標籤下的<span>標籤
tag_div = soup.find(id="q2")
tag_li = tag_div.find(class_="response")
tag_span = tag_li.find("span")
print(tag_span.string)
