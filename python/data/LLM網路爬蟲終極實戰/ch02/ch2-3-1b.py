import requests 

r = requests.get("http://httpbin.org/user-agent")
print(r.text)
print(type(r.text))
print("----------------------")
print(r.json())
print(type(r.json()))
