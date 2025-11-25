from bs4 import BeautifulSoup 

soup = BeautifulSoup("<p><b>One</b></p>", "lxml")  
tag = soup.b  
new_tag = soup.new_tag("i")
new_tag.string = "Two"
tag.insert_before(new_tag)
print(soup.p)
new_string = soup.new_string("Three")
tag.insert_after(new_string)
print(soup.p)
tag.clear()
print(soup.p)
