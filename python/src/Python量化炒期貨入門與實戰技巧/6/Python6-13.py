num = 1


def fun1():
    global num  # 使用 global 关键字声明
    print("使用 global 关键字声明后，就可以在自定义函数中引用外部变量，其值为：", num)
    num = 286  # 重新为外部变量num赋值
    print("重新为外部变量num赋值后的值：", num)


print("没调用函数前，全部变量的值：", num)
print()
fun1()  # 调用自定义函数fun1()
print()
print("调用函数后，全部变量的值：", num)
