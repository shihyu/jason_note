# list1列表中都是字符串数据
list1 = ["我", "爱", "python"]
# list2列表中都是数值型数据
list2 = [100, 200, 300, 400, 125]
print("list1的最大值:", max(list1))
print("list2的最大值:", max(list2))
print("list1的最小值:", min(list1))
print("list2的最小值:", min(list2))
print("\nlist1的元数个数:", len(list1))
print("list2的元数个数:", len(list2))
# id() 函数用于获取对象的内存地址
print("\n我的内存地址值：", id(list1[0]))
print("爱的内存地址值：", id(list1[1]))
print("python的内存地址值", id(list1[2]))
aTuple = (123, "www.baidu.com", "www.163.com")  # 定义元组
list1 = list(aTuple)  # 把元组变成列表
print("\n列表元素 : ", list1)
