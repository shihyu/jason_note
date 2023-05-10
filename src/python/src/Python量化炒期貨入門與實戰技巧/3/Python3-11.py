mynum = input("输入一个数字：")
num = int(mynum)
if num % 3 == 0:
    if num % 7 == 0:
        print("\n输入的数字可以整除 3 和 7")
    else:
        print("\n输入的数字可以整除 3，但不能整除 7")
else:
    if num % 7 == 0:
        print("\n输入的数字可以整除 7，但不能整除 3")
    else:
        print("\n输入的数字不能整除 3 和 7")
