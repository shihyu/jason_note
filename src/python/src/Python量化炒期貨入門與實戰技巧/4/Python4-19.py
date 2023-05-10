coef = 1
rows = int(input("请输入要显示杨辉三角的行数:"))
# 利用i控制杨辉三角的行数
for i in range(0, rows):
    # 利用space控制每行的空格数
    for space in range(1, rows + 1 - i):
        print("   ", end="")
    # 利用j控制每行要显示的杨辉三角
    for j in range(0, i + 1):
        if j == 0 or i == 0:
            coef = 1
        else:
            coef = int(coef * (i - j + 1) / j)
        print("   ", coef, end="")
    # 换行
    print()
