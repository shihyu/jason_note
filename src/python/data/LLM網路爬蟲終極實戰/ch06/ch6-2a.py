import requests
from lxml import html 

r = requests.get("https://fchart.github.io/test/album.html")
tree = html.fromstring(r.text)

tag_img = tree.xpath("/html/body/main/div/div/div/div[6]/div/img")[0]
print(tag_img)
print(tag_img.tag)
print(tag_img.attrib["src"])
print("-------------------------------")
tag_p = tree.xpath("/html/body/main/div/div/div/div[6]/div/div/p")[0]
print(tag_p)
print(tag_p.tag)
print(tag_p.text_content())


