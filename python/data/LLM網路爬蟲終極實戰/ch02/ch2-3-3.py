import requests 

r = requests.get("http://www.google.com")

print(r.headers.get('Content-Type', '無此欄位'))
print(r.headers.get('Content-Length', '無此欄位'))
print(r.headers.get('Date', '無此欄位'))
print(r.headers.get('Server', '無此欄位'))
