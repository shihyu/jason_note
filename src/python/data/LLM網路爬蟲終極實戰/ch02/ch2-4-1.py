import requests 
from requests.cookies import RequestsCookieJar

url = "http://httpbin.org/cookies"

cookies = dict(name='Joe Chen', score='100')
r = requests.get(url, cookies=cookies)
print(r.text)
