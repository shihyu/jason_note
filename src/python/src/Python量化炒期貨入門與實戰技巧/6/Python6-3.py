def changeme(mylist):
    "修改传入的列表"
    mylist.append([100, 200, 300, 400])
    print("函数内取值: ", mylist)
    return


# 调用changeme函数
mylist = [16, 112, 189]
changeme(mylist)
print()
print("函数外取值: ", mylist)
