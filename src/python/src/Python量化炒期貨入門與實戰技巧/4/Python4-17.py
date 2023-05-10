print("显示500以内的所有完数：\n")
for j in range(2, 501):
    k = []
    n = -1
    s = j
    for i in range(1, j):
        if j % i == 0:
            n = n + 1
            s = s - i
            k.append(i)
    if s == 0:
        print("完数：%d" % j, "，其因子所下：")
        for i in range(n + 1):
            print(str(k[i]))
