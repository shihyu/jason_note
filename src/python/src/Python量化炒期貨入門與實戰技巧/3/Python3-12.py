import random  # 导入random标准库

a = random.randint(10, 90)
b = random.randint(10, 90)
c = random.randint(10, 90)
print("显示随机产生的3个9以内的正整数：", a, b, c)
print()
if a > b:
    if b > c:  # 这时a>b>c
        print("最大值：%s" % a)
        print("最小值：%s" % c)
    elif c > a:  # 这时a>b, c>b ,c>a，即c>a>b
        print("最大值：%s" % c)
        print("最小值：%s" % b)
    else:  # 这时a>b, c>b  a>c，即a>c>b
        print("最大值：%s" % a)
        print("最小值：%s" % b)
else:
    if c > b:  # 这时b>a ,c>b，即c>b>a
        print("最大值：%s" % c)
        print("最小值：%s" % a)
    elif a > c:  # 这时b>a , b>c, a<c 即b>a>c
        print("最大值：%s" % b)
        print("最小值：%s" % c)
    else:  # 这时b>a,b>c,c>a，即b>c>a
        print("最大值：%s" % b)
        print("最小值：%s" % a)
