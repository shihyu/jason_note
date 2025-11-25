from bs4 import BeautifulSoup 

soup = BeautifulSoup("<p><b>One</b></p>", "lxml")  
tag = soup.b  
new_tag = soup.new_tag("i")
new_tag.string = "Two"
tag.replace_with(new_tag)
print(soup.p)
