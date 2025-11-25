from bs4 import BeautifulSoup 

html_str = "<div id='msg'>Hello World! <p> Final Test <p></div>"
soup = BeautifulSoup(html_str, "lxml")
tag = soup.div
print(tag.string)        # string屬性
print(tag.text)          # text屬性
print(type(tag.text)) 
print(tag.get_text())    # get_text()函數
print(tag.get_text("-"))
print(tag.get_text("-", strip=True))
