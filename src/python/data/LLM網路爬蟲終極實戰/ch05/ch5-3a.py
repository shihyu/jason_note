from bs4 import BeautifulSoup 

soup = BeautifulSoup("<b class='score'>Joe</b>", "lxml")    
tag = soup.b
tag.string = "Mary"
print(tag)
