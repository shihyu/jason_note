# 可写函数说明
def printinfo(name, sex, age, score):
    "打印任何传入的字符串或数值"
    print("名字: ", name)
    print("性别：", sex)
    print("年龄: ", age)
    print("成绩：", score)
    return


# 调用printinfo函数
printinfo(age=9, name="徐紫月", sex="女", score=95)
