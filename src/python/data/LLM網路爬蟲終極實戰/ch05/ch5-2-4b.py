from bs4 import BeautifulSoup  
from bs4.element import NavigableString

with open("Example.html", "r", encoding="utf8") as fp:
    soup = BeautifulSoup(fp, "lxml")    
tag_div = soup.find(id="q1")
for element in tag_div.previous_elements:
    if not isinstance(element, NavigableString):
        print(element.name)
        