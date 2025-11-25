from bs4 import BeautifulSoup 

with open("Example.html", "r", encoding="utf8") as fp:
    soup = BeautifulSoup(fp, "lxml")

tag_div = soup.find("div", id="q2")
# 找出所有標籤串列
tag_all = tag_div.find_all(True)
print(tag_all)
