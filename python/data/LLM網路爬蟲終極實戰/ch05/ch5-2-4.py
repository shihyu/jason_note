from bs4 import BeautifulSoup 

with open("Example.html", "r", encoding="utf8") as fp:
    soup = BeautifulSoup(fp, "lxml")
tag_html = soup.html # 找到<html>標籤
print(type(tag_html), tag_html.name)
tag_next = tag_html.next_element.next_element
print(type(tag_next), tag_next.name)
tag_title = soup.title # 找到<title>標籤
print(type(tag_title), tag_title.name)
tag_previous = tag_title.previous_element.previous_element
print(type(tag_previous), tag_previous.name)
