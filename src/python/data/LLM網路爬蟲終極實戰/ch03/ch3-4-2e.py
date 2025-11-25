from bs4 import BeautifulSoup 

with open("Example.html", "r", encoding="utf8") as fp:
    soup = BeautifulSoup(fp, "lxml")

tag_div = soup.find("div", id="q2")
# 找出所有<li>子孫標籤
tag_list = tag_div.find_all("li")
print(tag_list)
# 沒有使用遞迴來找出所有<li>標籤
tag_list = tag_div.find_all("li", recursive=False)
print(tag_list)
