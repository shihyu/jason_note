from bs4 import BeautifulSoup 

with open("Example.html", "r", encoding="utf8") as fp:
    soup = BeautifulSoup(fp, "lxml")
# 找出兄弟標籤
tag_div = soup.find(id="q1")
print(tag_div.p.a.string)
print("-----------")
tag_div = soup.select("#q1 ~ .survey")
for item in tag_div:            
    print(item.p.a.string)  
print("-----------")
tag_div = soup.select("#q1 + .survey")
for item in tag_div:            
    print(item.p.a.string)
