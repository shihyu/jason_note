import re

str1 = "  Python, is   a, \nprogramming, \n\nlanguage.\n\r   "

list1 = str1.split(",")
for item in list1:
    item = re.sub(r"\n+", "", item)
    item = re.sub(r" +", " ", item)
    item = item.strip()
    print("'" + item + "'")
    