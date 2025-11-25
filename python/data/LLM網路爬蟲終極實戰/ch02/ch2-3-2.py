import requests 

r = requests.get("http://www.google.com")
print(r.status_code)
print(r.status_code == requests.codes.ok)

r = requests.get("http://www.google.com/404")
print(r.status_code)
print(r.status_code == requests.codes.ok)

r = requests.get("http://www.google.com")
print(r.status_code)
print(r.status_code == requests.codes.all_good)
