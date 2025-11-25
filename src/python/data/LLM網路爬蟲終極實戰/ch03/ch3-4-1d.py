from bs4 import BeautifulSoup 

with open("Example.html", "r", encoding="utf8") as fp:
    soup = BeautifulSoup(fp, "lxml")
# 使用文字內容來搜尋標籤
tag_str = soup.find(string="請問你的性別?")
print(tag_str)
tag_str = soup.find(string="10")
print(tag_str)
print(type(tag_str))        # NavigableString型態
print(tag_str.parent.name)  # 父標籤名稱
tag_str = soup.find(string="男-")
print(tag_str)
