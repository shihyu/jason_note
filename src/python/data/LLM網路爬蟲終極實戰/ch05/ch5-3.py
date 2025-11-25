from bs4 import BeautifulSoup 

soup = BeautifulSoup("<b class='score'>Joe</b>", "lxml")    
tag = soup.b
tag.name = "p"
tag["class"] = "question"
tag["id"] = "name"
print(tag)
del tag["class"]
print(tag)
