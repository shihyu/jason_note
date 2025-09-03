import datetime

mytime = datetime.time(10, 30, 50)  # 定义一个time对象
myh = mytime.hour
print("mytime的小时是：", myh)
mym = mytime.minute
print("mytime的分钟是：", mym)
mys = mytime.second
print("mytime的秒数是：", mys)
print()
print("mytime的具体时间是：%d:%d:%d" % (myh, mym, mys))
