import re
from bs4 import BeautifulSoup 

with open("Example.html", "r", encoding="utf8") as fp:
    soup = BeautifulSoup(fp, "lxml")
# 使用正規運算式搜尋文字內容
regexp = re.compile("男-")
tag_str = soup.find(string=regexp)
print(tag_str)
regexp = re.compile("\w+-")
tag_list = soup.find_all(string=regexp)
print(tag_list)
