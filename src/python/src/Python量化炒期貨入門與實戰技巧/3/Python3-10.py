import math  # 导放math标准库

num = input("请输入一个三位数：")
if int(num) == pow(int(num[0]), 3) + pow(int(num[1]), 3) + pow(int(num[2]), 3):
    print()
    print(num, "是水仙花数！")
else:
    print()
    print(num, "不是水仙花数！")
