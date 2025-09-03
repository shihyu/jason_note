# 定义一个嵌套字典变量
users = {
    "num1": {"name": "admin", "passwd": "admin888", "sex": "1"},
    "num2": {"name": "赵杰", "passwd": "qd123456", "sex": "0"},
}
list1 = []  # 定义两个空的列表
list2 = []
for key1, value1 in users.items():
    list1.append(value1["name"])  # 添加用户姓名
    list2.append(value1["passwd"])  # 添加用户密码
print("用户登录系统".center(50, "*"))
timeout = 0  # 定义整型变量，用于统计次数
name = input("请输入用户的姓名：")
while timeout < 3:
    if not name in list1:  # 如果用户姓名不在嵌套字典
        if timeout == 2:  # 如果已输入3次，就会显示登录失败
            print("登录失败！")
            break
        print("用户不存在，请重新输入！")  # 显示提示信息
        timeout = timeout + 1  # 统计次数加上，并显示还有几次机会
        print("您还有 %d 次机会（共有3次机会）" % (3 - timeout), "\n")
        name = input("请输入用户的姓名：")
    else:  # 如果用户姓名在嵌套字典
        passwd = input("请输入用户的密码：")  # 利用input()函数输入密码
        if (name == list1[0] and passwd == list2[0]) or (
            name == list1[1] and passwd == list2[1]
        ):
            print("登录成功！")  # 如果密码正确，就会显示登录成功
            break
        else:  # 如果密码不正确，就会显示提示信息，并显示还有几次机会，当timeout等于2时，就会显示登录失败，并结束程序
            if timeout == 2:
                print("登录失败！")
                break
            print("密码不正确，请重新输入")
            timeout = timeout + 1
            print("\n您还有 %d 次机会（共有3次机会）" % (3 - timeout), "\n")
