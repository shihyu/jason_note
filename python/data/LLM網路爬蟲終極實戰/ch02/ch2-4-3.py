import requests 

url = "https://www.googleapis.com/books/v1/volumes"

url_params = {'q': 'Python',
              'maxResults': 5, 
              'projection': 'lite'}
r = requests.get(url, params=url_params)
print(r.json())
