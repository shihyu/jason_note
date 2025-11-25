from bs4 import BeautifulSoup

with open("Example.html", "r", encoding="utf8") as fp:
    soup = BeautifulSoup(fp, "lxml")
tag_div = soup.select("#q2") # 找到第2題
tag_ul = tag_div[0].ul       # 走訪到之下的<ul>
# 使用屬性取得所有祖先標籤
for tag in tag_ul.parents:
    print(tag.name)
# 使用函數取得所有祖先標籤
for tag in tag_ul.find_parents():
    print(tag.name)
    