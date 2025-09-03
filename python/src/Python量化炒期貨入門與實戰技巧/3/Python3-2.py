num = input("请输入一个正数：")
mynum = int(num)
# 下面利用if语句，判断输入的正数是奇数，还是偶数
if mynum % 2 == 0:
    # 如果输入的数取模于2，即除以2求余数，如果余数为0，就是偶数
    print("\n输入的正数是：", num)
    print(num, "是偶数")
else:
    print("\n输入的正数是：", num)
    print(num, "是奇数")
