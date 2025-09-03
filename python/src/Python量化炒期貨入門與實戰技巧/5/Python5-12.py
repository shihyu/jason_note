# 定义元组，注意是嵌套元组
accounts = (("张平", "qd123456"), ("李红", "liping2019"), ("赵杰", "sdqd2018"))
print("编号\t\t用户名\t\t密码")
for index, value in enumerate(accounts):
    print("%s\t\t%s\t\t%s" % (index, value[0], value[1]))
