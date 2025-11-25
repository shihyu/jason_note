import re
from bs4 import BeautifulSoup 

with open("Example.html", "r", encoding="utf8") as fp:
    soup = BeautifulSoup(fp, "lxml")
# 使用正規運算式搜尋URL網址
url_regexp = re.compile("^http:")
tag_href = soup.find(href=url_regexp)
print(tag_href)
print("---------------------")
tag_list = soup.find_all(href=url_regexp)
print(tag_list)
