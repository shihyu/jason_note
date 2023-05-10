# 定义列表变量
list1 = ["admin", "admin888", "zhangping", "zhangping2019"]
print("\n列表中的初始数据信息：", list1)
# 删除数据，即删除第三项和第四项数据
del list1[2:4]
print("\n删除数据后的列表信息：", list1)
# 删除列表，就可以删除列表中所有数据
del list1
print("\n成功删除所有列表数据！")
