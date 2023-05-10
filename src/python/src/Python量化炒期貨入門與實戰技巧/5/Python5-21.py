import random

mynum = input("请输入要排序的数字个数：")
mylist1 = []
for i in range(int(mynum)):
    num = random.randint(100, 1000)
    mylist1.append(num)
    mylist1.sort()
    print("输入的数字排序：", mylist1)
myset1 = set(mylist1)
print("\n\n无重复数字：", myset1)
print("\n升序排列无重复数字", sorted(myset1))
print("\n降序排列无重复数字", sorted(myset1, reverse=True))
