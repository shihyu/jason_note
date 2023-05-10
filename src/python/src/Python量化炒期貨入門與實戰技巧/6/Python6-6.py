def printinfo(name, score, age=13, sex="女"):
    print("名字: ", name)
    print("性别：", sex)
    print("年龄: ", age)
    print("成绩：", score)
    return


# 第一次调用printinfo函数
printinfo(age=12, name="张红", sex="男", score=97)
print("------------------------")
# 第二次调用printinfo函数
printinfo(name="李丝丝", score=85)
