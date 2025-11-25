from bs4 import BeautifulSoup 

with open("Example.html", "r", encoding="utf8") as fp:
    soup = BeautifulSoup(fp, "lxml")
# 找出前2個問卷的題目串列
tag_list = soup.find_all("p", class_="question", limit=2)
print(tag_list)

for question in tag_list:
    print(question.a.string)
    