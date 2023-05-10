import datetime

mydatetime = datetime.datetime.now()  # 获取当前日期和当前时间
print("当前日期和当前时间:", mydatetime)
mydate = mydatetime.date()
print("当前日期:", mydate)
mytime = mydatetime.time()
print("当前时间:", mytime)
print()
myy = mydatetime.year
print("当前日期的年份：", myy, "年")
mym = mydatetime.month
print("当前日期的月份：", mym, "月")
myd = mydatetime.day
print("当前日期的几日：", myd, "日")
print()
myh = mydatetime.hour
print("当前时间是几时：", myh, "小时")
mymi = mydatetime.minute
print("当前时间是几分钟：", mymi, "分钟")
myse = mydatetime.second
print("当前时间是几秒：", myh, "秒")
