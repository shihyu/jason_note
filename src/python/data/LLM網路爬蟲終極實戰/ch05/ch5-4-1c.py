baseUrl = "http://example.com"
list1 = ["http://www.example.com/test", "http://example.com/word",
         "media/ex.jpg", "http://www.example.com/index.html"]

def getUrl(baseUrl, source):
    if source.startswith("http://www."):
        url = "http://" + source[11:]
    elif source.startswith("http://"):
        url = source
    elif source.startswith("www"):
        url = source[4:]
        url = "http://" + source
    else:
        url = baseUrl + "/" + source
        
    if baseUrl not in url:
        return None
    return url

for item in list1:
    print(getUrl(baseUrl, item))
    