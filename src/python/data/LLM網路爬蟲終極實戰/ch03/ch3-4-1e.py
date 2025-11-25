from bs4 import BeautifulSoup 

with open("Example.html", "r", encoding="utf8") as fp:
    soup = BeautifulSoup(fp, "lxml")
# 使用多條件來搜尋HTML標籤
tag_div = soup.find("div", class_="question")
print(tag_div)
tag_p = soup.find("p", class_="question")
print(tag_p)
