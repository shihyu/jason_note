from bs4 import BeautifulSoup 

with open("Example.html", "r", encoding="utf8") as fp:
    soup = BeautifulSoup(fp, "lxml")
# 使用HTML5的data-屬性搜尋<div>標籤
tag_div = soup.find(attrs={"data-custom": "important"})
print(tag_div.string)
