s = 0
a = int(input("请输入a的值："))
n = int(input("请输入n的值："))
t = a  # 把输入的a值赋给变量t
while n > 0:
    s = s + t  # 变量s存放a+aa+...+aaa…aa
    a = a * 10  # 每循环一次，a的值扩大10倍
    t = t + a  # 变量t为aaa…aa的值
    n = n - 1  # 控制循环次数
print("\n\na+aa+...+aaa…aa=", s)
