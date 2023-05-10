mysum = 0  # 定义两个整型变量
num = 1
while num <= 200:  # 条件是num小于等于200，就继续执行while循环体中的代码
    mysum = mysum + num
    num += 1  # mysum变量就是1+2+……+200的和，而num变量是循环计数
print("1加到200的和为：", mysum)
