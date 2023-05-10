mysum = 0
num = 1
while num <= 100:
    if num % 2 == 1:
        mysum = mysum + num
    num += 1
else:
    print("100之内奇数的和为：", mysum)
