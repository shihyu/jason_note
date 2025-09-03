Sn = 100.0
Hn = Sn / 2
print("第  1  次反弹的高度是：", Hn, "米")
for n in range(2, 11):
    Sn += 2 * Hn
    Hn /= 2
    print("第 ", n, " 次反弹的高度是：", Hn, " 米")
print("\n\n第10次落地时共经过 %f 米" % Sn)
