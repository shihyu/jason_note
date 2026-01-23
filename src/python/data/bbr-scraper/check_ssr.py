import requests

url = "https://www.bbr.com/articles/all?pageSize=24&page=1"
response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
print(response.text[:1000])
if "Profiles on Burgundy" in response.text:
    print("FOUND ARTICLE TITLE")
else:
    print("NOT FOUND ARTICLE TITLE")
