import requests 

url = "http://httpbin.org/user-agent"

r = requests.get(url)
print(r.text)
print("----------------------")
url_headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}
r = requests.get(url, headers=url_headers)
print(r.text)
