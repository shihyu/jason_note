import re

list1 = ["", "/", "path/", "/path", "/path/", "//path/", "/path///"]

def getPath(path):
    if path:
        if path[0] != "/":
            path = "/" + path
        if path[-1] != "/":
            path = path + "/"
        path = re.sub(r"/{2,}", "/", path)
    else:
        path = "/"
        
    return path

for item in list1:
    item = getPath(item)
    print(item)
    