from bs4 import BeautifulSoup 

with open("Example.html", "r", encoding="utf8") as fp:
    soup = BeautifulSoup(fp, "lxml")
# 找出指定CSS選擇器字串的內容, <title>標籤和第3個<div>標籤
tag_item = soup.select("#q1 > ul > li:nth-child(1) > span")
print(tag_item[0].string)
tag_title = soup.select("title")
print(tag_title[0].string)
tag_first_div = soup.find("div")
tag_div = tag_first_div.select("div:nth-of-type(3)")
print(tag_div[0])
