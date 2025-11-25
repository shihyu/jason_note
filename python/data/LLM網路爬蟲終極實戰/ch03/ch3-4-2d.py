from bs4 import BeautifulSoup 

with open("Example.html", "r", encoding="utf8") as fp:
    soup = BeautifulSoup(fp, "lxml")

tag_div = soup.find("div", id="q2")
# 找出所有<p>和<span>標籤
tag_list = tag_div.find_all(["p", "span"])
print(tag_list)
# 找出class屬性值question或selected的所有標籤
tag_list = tag_div.find_all(class_=["question", "selected"])
print(tag_list)
