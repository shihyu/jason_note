from bs4 import BeautifulSoup 

with open("Example.html", "r", encoding="utf8") as fp:
    soup = BeautifulSoup(fp, "lxml")
# 搜尋<a>標籤
tag_a = soup.find("a") 
print(tag_a.string)
# 呼叫多次find()函數
tag_p = soup.find(name="p")
tag_a = tag_p.find(name="a")
print(tag_p.a.string)
print(tag_a.string)
