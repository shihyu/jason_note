import requests
from lxml import html 

r = requests.get("https://fchart.github.io/test/album.html")
tree = html.fromstring(r.text)

tag_img = tree.xpath("/html/body/main/div/div/div/div[6]/div/img")[0]

for ele in tag_img.getparent().getchildren():
    print(ele.tag)
