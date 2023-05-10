import time  # 导入time模块

n = time.time()  # 获取当前时间的时间戳
tup1 = time.localtime(n)  # 把时间戳转化为包括9个元素的元组
# 日期的两种表示方法
myd = time.strftime("%Y-%m-%d", tup1)
print("当前的日期：", myd)
myd1 = time.strftime("%y-%m-%d", tup1)
print("当前的日期另一种表示方法：", myd1)
# 时间的两种表示方法
myt = time.strftime("%H:%M:%S:%p", tup1)
print("\n当前的时间：", myt)
myt1 = time.strftime("%I:%M:%S:%p", tup1)
print("当前的时间另一种表示方法：", myt1)
# 星期的两种表示方法
myw = time.strftime("%a", tup1)
print("\n当前是星期几：", myw)
myw1 = time.strftime("%A", tup1)
print("当前是星期几另一种表示方法：", myw1)
# 月份的两种表示方法
mym = time.strftime("%b", tup1)
print("\n当前是几月份：", mym)
mym1 = time.strftime("%B", tup1)
print("当前是几月份另一种表示方法：", mym1)
# 本地相应的日期表示和时间表示法
mypp = time.strftime("%c", tup1)
print("\n本地相应的日期表示和时间表示:", mypp)
# 本地相应的日期表示
myppd = time.strftime("%x", tup1)
print("本地相应的日期表示法：", myppd)
# 本地相应的时间表示
myppt = time.strftime("%X", tup1)
print("本地相应的时间表示法：", myppt)
# 当前是年内的第几天
myday = time.strftime("%j", tup1)
print("\n当前是年内的第几天：", myday)
# 当前是年内的第几个星期
myweeknum = time.strftime("%U", tup1)
print("\n当前是年内的第几个星期：", myweeknum)
# 当前是本星期的星期几
myweeks = time.strftime("%w", tup1)
print("当前是本星期的星期几：", myweeks)
# 当前时区的名称
mywe = time.strftime("%z", tup1)
print("\n当前时区的名称：", mywe)
