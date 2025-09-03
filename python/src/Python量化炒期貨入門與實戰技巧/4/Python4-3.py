import random  # 导入random标准库

mymin = 200  # 定义变量，存放随机数中的最小数
i = 1  # 定义变量，用于统计循环次数
while i <= 20:
    r = random.randint(50, 150)  # 在50~150之间随机产生一个数
    i += 1  # 循环次数加1
    print("第 %d 随机数是: %s " % (i - 1, r))  # 显示第几个随机数是几
    if r < mymin:
        mymin = r  # 把随机数中的最小数放到mymin中
print("\n\n这20个数中，最小的数是：", mymin)
