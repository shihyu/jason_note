def outer():  # 自定义函数
    num = 15

    def inner():  # 自定义嵌套函数
        nonlocal num  # nonlocal关键字声明
        print("nonlocal关键字声明，在嵌套函数中调用num的值，其值为", num)
        print()
        num = 198  # 重新为num赋值
        print("重新为num赋值后，其值为", num)
        print()

    inner()  # 调用嵌套函数
    print("调用嵌套函数后，num的值为", num)


outer()  # 调用自定义函数
