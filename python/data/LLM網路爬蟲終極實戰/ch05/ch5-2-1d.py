from bs4 import BeautifulSoup 

with open("Example.html", "r", encoding="utf8") as fp:
    soup = BeautifulSoup(fp, "lxml")
# 使用屬性取得所有子孫的文字內容
tag_div = soup.select("#q2") # 找到第2題
tag_ul = tag_div[0].ul       # 走訪到之下的<ul>
for string in tag_ul.strings:
    print(string.replace('\n', ''))
    