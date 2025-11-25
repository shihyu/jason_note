from bs4 import BeautifulSoup 

with open("Example.html", "r", encoding="utf8") as fp:
    soup = BeautifulSoup(fp, "lxml")
# 找出所有問卷的題目串列
tag_list = soup.find_all("p", class_="question")
print(tag_list)

for question in tag_list:
    print(question.a.string)
    