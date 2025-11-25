from bs4 import BeautifulSoup 

with open("test.html", "r", encoding="utf8") as fp:
    soup = BeautifulSoup(fp, "lxml")
    print(soup)
