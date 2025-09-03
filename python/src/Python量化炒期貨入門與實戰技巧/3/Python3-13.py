myticket = input("请输入你是否有车票，如果有，输入1；没有输入0：")
ticket = int(myticket)
if ticket:
    kf_length = int(input("\n请输入您携带的刀的长度:"))
    print("\n\n车票检查通过，准备开始安检!")
    if kf_length > 20:
        print("\n您携带的刀太长了,有%d厘米长！" % kf_length)
        print("\n不允许带上车！")
    else:
        print("\n安检已经通过，祝您旅途愉快！")
else:
    print("\n\n对不起，请先买票")
