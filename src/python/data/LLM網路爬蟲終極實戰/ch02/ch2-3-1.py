import requests

r = requests.get("https://fchart.github.io/test.html")

print(r.text)
print(r.encoding)

r = requests.get("https://fchart.github.io/test.html")
r.encoding = 'ISO-8859-1'

print(r.text)
print(r.encoding)
