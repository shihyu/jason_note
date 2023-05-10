import time  # 导入time模块

n = time.time()  # 获取当前时间的时间戳
tup1 = time.localtime(n)  # 把时间戳转化为包括9个元素的元组
myf = time.asctime(tup1)  # 把包括9个元素的元组格式化
print("显示格式化后的时间：", myf)  # 显示格式化后的当前时间
print()
tup2 = (2019, 3, 14, 15, 25, 37, 4, 73, 0)  # 定义一个包括9个元素的元组
myt = time.asctime(tup2)  # 格式化包括9个元素的元组
print("显示格式化后的元组tup2：", myt)
