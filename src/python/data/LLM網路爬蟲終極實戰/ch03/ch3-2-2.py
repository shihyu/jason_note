from bs4 import BeautifulSoup

with open("test2.txt", "r", encoding="utf8") as fp:
    soup = BeautifulSoup(fp, "lxml")
    print(soup.prettify())
