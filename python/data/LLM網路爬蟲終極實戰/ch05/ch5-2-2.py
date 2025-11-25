from bs4 import BeautifulSoup 

with open("Example.html", "r", encoding="utf8") as fp:
    soup = BeautifulSoup(fp, "lxml")
tag_div = soup.select("#q2") # 找到第2題
tag_ul = tag_div[0].ul       # 走訪到之下的<ul>
# 使用屬性取得父標籤
print(tag_ul.parent.name)
# 使用函數取得父標籤
print(tag_ul.find_parent().name)
