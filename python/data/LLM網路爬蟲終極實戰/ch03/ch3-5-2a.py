import re
from bs4 import BeautifulSoup 

with open("Example.html", "r", encoding="utf8") as fp:
    soup = BeautifulSoup(fp, "lxml")
# 使用正規運算式搜尋電子郵件地址
email_regexp = re.compile("\w+@\w+\.\w+")
tag_str = soup.find(string=email_regexp)
print(tag_str)
print("---------------------")
tag_list = soup.find_all(string=email_regexp)
print(tag_list)