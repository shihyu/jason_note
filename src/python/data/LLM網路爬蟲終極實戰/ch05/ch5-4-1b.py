import string

str1 = "#$%^Python -is- *a* $%programming_ language.$"

print(string.punctuation)
list1 = str1.split(" ")
for item in list1:
    print(item.strip(string.punctuation))
    