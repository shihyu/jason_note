from urllib.parse import urljoin

URL = "http://books.toscrape.com/catalogue/"
PTT = "https://wwww.ptt.cc/bbs/movie/index.html"

catalog = ["movie", "NBA", "Gossiping"]

for i in range(1, 5):
    url = urljoin(URL, "page-{0}.html".format(i)) 
    print(url)
for item in catalog:
    url = urljoin(PTT, "../{0}/index.html".format(item))
    print(url)