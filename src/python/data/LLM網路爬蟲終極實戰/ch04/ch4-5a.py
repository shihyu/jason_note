from bs4 import BeautifulSoup 

with open("Example.html", "r", encoding="utf8") as fp:
    soup = BeautifulSoup(fp, "lxml")
# 找出<title>標籤, 和<div>標籤下的所有<a>標籤
tag_title = soup.select("html head title")
print(tag_title[0].string)    
tag_a = soup.select("body div a")
print(tag_a)
