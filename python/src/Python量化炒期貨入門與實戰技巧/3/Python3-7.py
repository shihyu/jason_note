year = input("请输入一个年份：")
myyear = int(year)
if (myyear % 400 == 0) or (myyear % 4 == 0 and myyear % 100 != 0):
    print("\n您输入的年份是：", myyear, "，这一年是润年。")
else:
    print("\n您输入的年份是：", myyear, "，这一年是平年。")
