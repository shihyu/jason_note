import datetime

t1 = datetime.timedelta(seconds=30)  # 时间差为30秒
t2 = datetime.timedelta(seconds=45)  # 时间差为45秒
print("显示t1的值：", t1)
print("显示t2的值：", t2)
print("显示t1的最大值：", t1.max)
print("显示t1的最小值：", t1.min)
print()
t3 = t1 + t2
# 两个timedelta相加
print(t3.seconds)
# 两个timedelta相减
t4 = t2 - t1
print(t4)
# timedelta乘法
t5 = t2 * 3
print(t5)
# timedelta除法
t6 = t1 / 3
print(t6)
# timedelta比较操作
if t1 > t2:
    print("datetime.timedelta(seconds =30)大于datetime.timedelta(seconds =45)")
elif t1 == t2:
    print("datetime.timedelta(seconds =30)等于datetime.timedelta(seconds =45)")
else:
    print("datetime.timedelta(seconds =30)小于datetime.timedelta(seconds =45)")

mydatetime = datetime.datetime.now()  # 获得当前的日期与时间
mydate = mydatetime.date()
mytime = mydatetime.time()
print("\n\n当前的日期是：", mydate)
myt = datetime.timedelta(days=10)  # 时间差为10天
mysum1 = mydate + myt  # 10天后的日期
print("10天后的日期:", mysum1)
print("\n\n当前的时间是：", mytime)
myh = datetime.timedelta(seconds=60)  # 时间差为10分钟
mysum2 = mydatetime + myh  # 10分钟后的时间
print("10分钟后的时间是：", mysum2.time())
print()
time1 = datetime.datetime(2019, 3, 15, 12, 0, 0)
time2 = datetime.datetime.now()
differtime = (time1 - time2).total_seconds()
print("(2019,3,15,12,0,0)与当前时间相差：", differtime, "秒！")
# 输出结果
