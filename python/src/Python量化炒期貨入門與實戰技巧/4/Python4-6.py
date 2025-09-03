x1 = 0
x2 = 1
myday = 15
print("第16天的桃数为：1")
while myday > 0:
    x1 = (x2 + 1) * 2  # 第一天的桃子数是第2天桃子数加1后的2倍
    x2 = x1
    myday = myday - 1
    print("第", myday + 1, "天的桃数为：", x1)
