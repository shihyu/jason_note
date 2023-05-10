var = 12
while var > 0:
    var = var - 1
    if var == 5 or var == 7 or var == 9:  # 变量为 5、7、9 时跳过输出
        continue
    print("当前变量值 :", var)
print("\n程序运行完毕，再见！")
