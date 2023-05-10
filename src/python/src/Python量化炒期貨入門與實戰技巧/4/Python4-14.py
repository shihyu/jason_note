num1 = int(input("请输入第一个数："))
num2 = int(input("请输入第二个数："))
# 如果num2大于num1交换两个变量
if num2 > num1:
    temp = num2
    num2 = num1
    num1 = temp
for i in range(1, num2 + 1):
    if num1 % i == 0 and num2 % i == 0:
        mymax = i
print("\n\n两个数的最大公约数是：", mymax)
