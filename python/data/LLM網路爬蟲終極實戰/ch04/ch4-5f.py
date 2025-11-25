from bs4 import BeautifulSoup 

with open("Example.html", "r", encoding="utf8") as fp:
    soup = BeautifulSoup(fp, "lxml")
# 使用select_one()方法搜尋標籤
tag_a = soup.select_one("a[href]")
print(tag_a)
