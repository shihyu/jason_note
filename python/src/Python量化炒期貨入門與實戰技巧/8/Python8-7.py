import datetime  # 导入datetime模块

myday = datetime.date.today()  # 调用date中的today()方法，显示当前的日期
print("当前的日期是：", myday)
myweek = myday.isoweekday()
print("当前日期是星期几：", myweek)
mynumday = myday.toordinal()
print("从公元公历开始到现在的天数：", mynumday)
print()
a = myday.replace(2018, 7, 8)
print("a的日期是：", a)
print("myday的日期没有变化，仍是：", myday)
x = datetime.date.max
y = datetime.date.min
print("date对象能表示的最大的日期是：", x)
print("date对象能表示的最小的日期是：", y)
