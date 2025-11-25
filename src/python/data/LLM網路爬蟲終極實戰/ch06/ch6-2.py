import requests
from lxml import html 

r = requests.get("https://fchart.github.io/test/album.html")
tree = html.fromstring(r.text)
print(tree)
print("-------------------------------")
for ele in tree.getchildren():
    print(ele)


