import requests

r = requests.get("https://fchart.github.io/test2.html")
print(r.text)
print("----------------------")
r = requests.get("https://fchart.github.io/test2.html")
print(r.content)
print("----------------------")
r = requests.get("https://fchart.github.io/test2.html", stream=True)
print(r.raw)
print(r.raw.read(15))
