users = {
    "num1": {"name": "admin", "passwd": "admin888", "sex": "1"},
}  # 字典的初始值
list1 = []  # 定义一个空列表
for name, info in users.items():  # 利用双for循环，提出嵌套字典中的数据
    for key, value in info.items():
        list1.append(value)  # 把字典中的数据添加到列表中
print("用户注册之前信息：", users)
print(" ********************用户的创建**********************")  # 提示信息
print("注册".center(50, "*"))  # 注册
name = input("请输入注册姓名:")  # 利用input()函数输入注册姓名
if not name in list1[0]:  # 如果姓名没有在users中，就可以继续输入其他信息
    passwd = input("请输入注册密码:")
    sex = input("请输入性别：0表示'女',1表示'男':")
    users["num2"] = {"name": name, "passwd": passwd, "sex": sex}  # 向字典中添加数据
    print("新用户注册成功!")
    print("新用户注册成功后的信息：", users)
else:
    print("该用户名已注册，对不起！")
