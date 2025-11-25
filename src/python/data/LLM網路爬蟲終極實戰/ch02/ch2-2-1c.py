import requests 

data = {'name': '陳會安', 'score': 95}
r = requests.get("http://httpbin.org/get", params=data)
print(r.text)
