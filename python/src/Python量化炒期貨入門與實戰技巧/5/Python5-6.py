import random

list1 = []  # 定义一个空列表
for i in range(8):  # 利用for循环向列表中添加数据
    mynum = random.randint(100, 1000)
    list1.append(mynum)
print("\n随机产生的8个随机数是：", list1)
list1.sort()  # 默认为升序
print("\n\n从小到大排序8个随机数:", list1)
list1.sort(reverse=True)  # 设置排序为降序
print("从大到小排序8个随机数:", list1)
print("\n\n8个随机数中的最大数：", max(list1))
print("8个随机数中的最小数：", min(list1))
