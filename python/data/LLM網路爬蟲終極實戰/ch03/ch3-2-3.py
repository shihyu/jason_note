from bs4 import BeautifulSoup 

html_str = "<div id='msg' class='body strikeout'>Hello World!</div>"
soup = BeautifulSoup(html_str, "lxml")
tag = soup.div
print(type(tag))     # Tag型態
print(tag.name)      # 標籤名稱
print(tag["id"])     # 標籤屬性
print(tag["class"])  # 多重值屬性的值串列
print(tag.attrs)     # 標籤所有屬性值的字典