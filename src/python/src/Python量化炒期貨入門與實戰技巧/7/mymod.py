def print_func(par):
    print("您好，调用了模块(mymodule)中的print_func函数：", par)
    return


def fib(n):  # 定义到 n 的斐波那契数列
    a, b = 0, 1
    while b < n:
        print(b, end=" ")  # 不换行输出
        a, b = b, a + b
    print()  # 输出一个空行
