from bs4 import BeautifulSoup
from bs4.element import NavigableString 

soup = BeautifulSoup("<b></b>", "lxml")    
tag = soup.b
tag.append("Joe")
print(tag)
new_str = NavigableString(" Chen")
tag.append(new_str)
print(tag)
new_tag = soup.new_tag("a", href="http://www.example.com")
tag.append(new_tag)
print(tag)
