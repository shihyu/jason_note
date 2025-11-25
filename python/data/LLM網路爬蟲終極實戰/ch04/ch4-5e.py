from bs4 import BeautifulSoup

with open("Example.html", "r", encoding="utf8") as fp:
    soup = BeautifulSoup(fp, "lxml")
# 找出特定屬性值的標籤
tag_a = soup.select("a[href]")
print(tag_a)
tag_a = soup.select("a[href='http://example.com/q2']")
print(tag_a)
tag_a = soup.select("a[href^='http://example.com']")
print(tag_a)
tag_a = soup.select("a[href$='q3']")
print(tag_a)
tag_a = soup.select("a[href*='q']")
print(tag_a)
