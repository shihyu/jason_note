import datetime  # 导入datetime模块

myday = datetime.date.today()  # 调用date中的today()方法，显示当前的日期
print("当前的日期是：", myday)
print("\n分别提取当前日期的年、月、日，并显示：")
y = myday.year
print("当前日期的年份是：", y)
m = myday.month
print("当前日期的月份是：", m)
d = myday.day
print("当前日期的几日是：", d)
print("\n\n当前日期是：%d年%d月%d日" % (y, m, d))
