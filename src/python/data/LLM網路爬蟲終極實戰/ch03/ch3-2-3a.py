from bs4 import BeautifulSoup 

html_str = "<div id='msg' class='body strikeout'>Hello World!</div>"
soup = BeautifulSoup(html_str, "lxml")
tag = soup.div
print(tag.string)        # 標籤內容
print(type(tag.string))  # NavigableString型態
