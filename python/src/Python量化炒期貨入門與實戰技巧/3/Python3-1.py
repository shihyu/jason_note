num1 = input("请输入第一个职工的工资：")
num2 = input("请输入第二个职工的工资：")
mynum1 = float(num1)
mynum2 = float(num2)
print("\n第一个职工的工资：", mynum1, "\t第二个职工的工资:", mynum2)
if mynum1 > mynum2:
    print("\n第一个职工的工资高，工资是：", mynum1)
else:
    print("\n第二个职工的工资高，工资是：", mynum2)
