from bs4 import BeautifulSoup 

with open("Example.html", "r", encoding="utf8") as fp:
    soup = BeautifulSoup(fp, "lxml")
# 找出指定標籤下的直接子標籤
tag_a = soup.select("p > a")
print(tag_a)  
tag_li = soup.select("ul > li:nth-of-type(2)")
print(tag_li)
tag_span = soup.select("div > #email")
print(tag_span)
