mystr = input("请输入一行字符串：")  # 调用input()函数输入字符串
myletters = 0  # 定义整型变量，用来统计字母的个数
myspaces = 0  # 定义整型变量，用来统计空格的个数
mynums = 0  # 定义整型变量，用来统计数字的个数
others = 0  # 定义整型变量，其他字符的个数
i = 0  # 定义整型变量，用来统计循环次数
while i < len(mystr):
    mychar = mystr[i]  # 定义字符串变量，提取mystr中的每个字符
    i = i + 1  # 统计循环次数的变量加1
    if mychar.isalpha():  # 调用字符串的isalpha()，统计字母的个数
        myletters = myletters + 1
    elif mychar.isspace():
        myspaces = myspaces + 1
    elif mychar.isdigit():
        mynums = mynums + 1
    else:
        others = others + 1
print("\n字母的个数为：%d" % myletters)
print("空格的个数为： %d" % myspaces)
print("数字的个数为： %d" % mynums)
print("其他字符的个数为： %d" % others)
