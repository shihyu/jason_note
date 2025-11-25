from bs4 import BeautifulSoup 

with open("Example.html", "r", encoding="utf8") as fp:
    soup = BeautifulSoup(fp, "lxml")
tag_div = soup.select("#q2") # 找到第2題
tag_li = tag_div[0].ul.li  # 第1個<li>
third_li = tag_li.find_next_sibling().find_next_sibling()
print(third_li)
# 使用previous_sibling屬性取得前一個兄弟標籤
second_li = third_li.previous_sibling.previous_sibling
print(second_li)
# 呼叫previous_sibling()函數取得前一個兄弟標籤
first_li = second_li.find_previous_sibling()
print(first_li)
print("---------------------------------------")
# 呼叫previous_siblings()函數取得所有兄弟標籤
for tag in third_li.find_previous_siblings():
    print(tag.name, tag.span.string)
    