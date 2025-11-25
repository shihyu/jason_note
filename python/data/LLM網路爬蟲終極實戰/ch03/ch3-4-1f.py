from bs4 import BeautifulSoup 

with open("Example.html", "r", encoding="utf8") as fp:
    soup = BeautifulSoup(fp, "lxml")
# 使用函數建立搜尋條件
def is_secondary_question(tag):
    return tag.has_attr("href") and \
           tag.get("href") == "http://example.com/q2"

tag_a = soup.find(is_secondary_question)
print(tag_a)
