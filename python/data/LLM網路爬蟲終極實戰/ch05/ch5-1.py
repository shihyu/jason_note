from bs4 import BeautifulSoup 

with open("Example.html", "r", encoding="utf8") as fp:
    soup = BeautifulSoup(fp, "lxml")
# 使用childen屬性取得子標籤
tag_div = soup.select("#q2") # 找到第2題
tag_ul = tag_div[0].ul       # 走訪到之下的<ul>
for child in tag_ul.children:
    print(type(child))
    