from bs4 import BeautifulSoup 

html_str = "<p><!-- 註解文字 --></p>"
soup = BeautifulSoup(html_str, "lxml")
comment = soup.p.string
print(comment)
print(type(comment))   # Comment型態
