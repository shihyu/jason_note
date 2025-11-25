import requests 

url_params = {'name': '陳會安', 'score': 95}
r = requests.get("http://httpbin.org/get", params=url_params)
print(r.url)
