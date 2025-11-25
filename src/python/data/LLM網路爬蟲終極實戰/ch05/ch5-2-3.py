from bs4 import BeautifulSoup 

with open("Example.html", "r", encoding="utf8") as fp:
    soup = BeautifulSoup(fp, "lxml")
tag_div = soup.select("#q2") # 找到第2題
first_li = tag_div[0].ul.li  # 第1個<li>
print(first_li)
# 使用next_sibling屬性取得下一個兄弟標籤
second_li = first_li.next_sibling.next_sibling
print(second_li)
# 呼叫next_sibling()函數取得下一個兄弟標籤
third_li = second_li.find_next_sibling()
print(third_li)
print("---------------------------------------")
# 呼叫next_siblings()函數取得所有兄弟標籤
for tag in first_li.find_next_siblings():
    print(tag.name, tag.span.string)
    