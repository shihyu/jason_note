import calendar

myyear1 = int(input("请输入一个年份："))
if calendar.isleap(myyear1):
    print("%d 年是润年！" % myyear1)
else:
    print("%d 年不是润年！" % myyear1)
print()
myyear2 = int(input("请再输入一个年份："))
if myyear2 > myyear1:
    mynum1 = calendar.leapdays(myyear1, myyear2)
    print("%d年到%d之间，有%d个润年。" % (myyear1, myyear2, mynum1))
else:
    mynum1 = calendar.leapdays(myyear2, myyear1)
    print("%d年到%d之间，有%d个润年。" % (myyear2, myyear1, mynum1))
print()
mymonth = int(input("请再输入一个月份："))
mynum2, mynum3 = calendar.monthrange(myyear1, mymonth)
print("%d年%d月，第一天是星期%d，这个月共有%d天" % (myyear1, mymonth, mynum2, mynum3))
print()
mynum4, mynum5 = calendar.monthrange(myyear2, mymonth)
print("%d年%d月，第一天是星期%d，这个月共有%d天" % (myyear2, mymonth, mynum4, mynum5))
