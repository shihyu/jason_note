n = int(input("请输入要显示弗洛伊德三角形的行数:"))
j = 1
for i in range(1, n + 1):
    for l in range(1, i + 1):
        print(j, "\t", end="")
        j = j + 1
    print()
