import datetime  # 导入datetime模块

a = datetime.date.today()  # 调用date中的today()方法，显示当前的日期
b = datetime.date(2019, 2, 26)  # 直接为date赋值
print("a的日期是：", a)  # 显示两个日期
print("b的日期是：", b)
if a.__eq__(b):
    print("a的日期与b的日期相同！")
elif a.__gt__(b):
    print("a的日期大于b的日期.")
    myc = a.__sub__(b).days
    print("a的日期大于b的日期，多的天数是：", myc)
else:
    print("a的日期小于b的日期.")
    myc = b.__sub__(a).days
    print("b的日期大于a的日期，多的天数是：", myc)
